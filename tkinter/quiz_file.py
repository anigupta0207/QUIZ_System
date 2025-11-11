from tkinter import *
from tkinter import ttk, messagebox as tmsg, filedialog
from datetime import datetime
import os, json
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

# ========================= CONFIG =========================
PALETTE = { "bg_top": "#eef3ff", 
    "bg_bottom": "#f9fcff", 
    "card_bg": "#ffffff",
    "text": "#1f2937", 
    "muted": "#6b7280",
    "accent": "#2563eb",
    "accent_dark": "#1e40af",
    "success": "#16a34a",
    "danger": "#dc2626",
    "radio_select": "#e0edff",
    "btn_text": "#ffffff",
}
FONT_H1   = ("Segoe UI", 20, "bold")
FONT_Q    = ("Segoe UI", 16, "bold")
FONT_OPT  = ("Segoe UI", 14)
FONT_META = ("Segoe UI", 11)
FONT_BTN  = ("Segoe UI", 12, "bold")

QUIZ_DEFS = [
    {"id": "quiz1", "title": "Quiz 1 — C++ Basics",    "path": os.path.join("quizzes", "quiz1.txt")},
    {"id": "quiz2", "title": "Quiz 2 — C Basics", "path": os.path.join("quizzes", "quiz2.txt")},
    {"id": "quiz3", "title": "Quiz 3 — Python Basics",   "path": os.path.join("quizzes", "quiz3.txt")},
]

USERS_FILE = "users.json"  # stored beside this script

# ===================== PATH HELPERS =======================
def script_path(*parts):
    base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, *parts)

def ensure_dirs():
    os.makedirs(script_path("attempts"), exist_ok=True)
    os.makedirs(script_path("quizzes"), exist_ok=True)

# ===================== USERS STORAGE ======================
def load_users():
    p = script_path(USERS_FILE)         
    if not os.path.exists(p):      
        return {}
    try:
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)  
    except Exception:
        return {}

def save_users(data):
    with open(script_path(USERS_FILE), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def ensure_default_admin():
    users = load_users()
    if "admin" not in users:
        users["admin"] = {"password": "admin", "role": "admin"}
        save_users(users)

# ===================== QUIZ LOAD/SAVE =====================
def load_quiz_from_file(filename):
    quiz_list = []
    try:
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read().strip()

        blocks = [b for b in content.split("\n\n") if b.strip()]         # split by double newlines 
        for block in blocks:
            lines = [ln.strip() for ln in block.split("\n") if ln.strip()]        # split by single newlines
            if len(lines) < 3:  # need at least Q + answers + Answer:
                continue

            question_line = lines[0]
            options = []
            answer = ""

            for line in lines[1:]:
                if line.startswith(("A)", "B)", "C)", "D)")):      # options
                    options.append(line[3:].strip())
                elif line.startswith("Answer:"):     # correct answer
                    ans = line.split(":", 1)[1].strip().upper()[:1]
                    idx = ord(ans) - ord('A')
                    if 0 <= idx < len(options):
                        answer = options[idx]

            question = question_line[2:].strip() if question_line.startswith("Q:") else question_line
            if question and options and answer:
                quiz_list.append({"question": question, "options": options[:4], "answer": answer})
    except FileNotFoundError:
        tmsg.showerror("Error", f"File '{filename}' not found!")
        return []
    return quiz_list

def save_result_to_file(name, score, total, duration_seconds, user_choices, quiz_data, quiz_title):
    ensure_dirs()

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")     
    percent = round((score/total)*100, 2) if total else 0

    with open(script_path("results.txt"), "a", encoding="utf-8") as f:    # summary line
        f.write(f"{timestamp} | Name: {name} | Quiz: {quiz_title} | Score: {score}/{total} | {percent}% | Duration: {int(duration_seconds)}s\n")

    ts_slug = datetime.now().strftime("%Y%m%d_%H%M%S")    
    safe_name = "".join(c for c in name if c.isalnum() or c in (" ","_","-")).strip().replace(" ", "_") or "Anonymous"      # safe filename
    attempt_path = script_path("attempts", f"{ts_slug}_{safe_name}.txt")   # detailed file

    with open(attempt_path, "w", encoding="utf-8") as f:   # detailed report
        f.write(f"Name: {name}\n")
        f.write(f"Timestamp: {timestamp}\n")
        f.write(f"Quiz: {quiz_title}\n")
        f.write(f"Total Questions: {len(quiz_data)}\n")
        f.write(f"Duration: {int(duration_seconds)} seconds\n")
        f.write("-"*60 + "\n\n")
        correct = 0
        for i, q in enumerate(quiz_data):
            chosen_text = ""
            if i < len(user_choices) and user_choices[i] is not None and user_choices[i] != -1:
                try:
                    chosen_text = q["options"][int(user_choices[i])]
                except Exception:
                    chosen_text = ""
            is_correct = (chosen_text == q["answer"])
            if is_correct:
                correct += 1

            f.write(f"Q{i+1}. {q['question']}\n")
            for idx, opt in enumerate(q["options"]):
                tags = []
                if opt == q["answer"]:
                    tags.append("Correct")
                if opt == chosen_text:
                    tags.append("Chosen")
                tag_str = f" ({', '.join(tags)})" if tags else ""
                f.write(f"  {chr(ord('A')+idx)}) {opt}{tag_str}\n")
            f.write(f"Result: {'Correct' if is_correct else 'Incorrect'}\n")
            f.write("-"*60 + "\n")
        percent = round((correct/len(quiz_data))*100, 2) if quiz_data else 0.0
        f.write(f"\nFinal Score: {correct}/{len(quiz_data)} ({percent}%)\n")

    return attempt_path

# ===================== UI HELPERS =========================
def gradient_background(canvas, w, h, start=PALETTE["bg_top"], end=PALETTE["bg_bottom"]):
    r1, g1, b1 = root.winfo_rgb(start)
    r2, g2, b2 = root.winfo_rgb(end)
    r_ratio = (r2 - r1) / max(1, h)
    g_ratio = (g2 - g1) / max(1, h)
    b_ratio = (b2 - b1) / max(1, h)
    for i in range(h):
        nr = int(r1 + (r_ratio * i))
        ng = int(g1 + (g_ratio * i))
        nb = int(b1 + (b_ratio * i))
        color = f'#{nr//256:02x}{ng//256:02x}{nb//256:02x}'
        canvas.create_line(0, i, w, i, fill=color)

def style_btn(btn, base, hover):
    def on_enter(e): btn.config(bg=hover)
    def on_leave(e): btn.config(bg=base)
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)

def make_card(master):
    card = Frame(master, bg=PALETTE["card_bg"], bd=0, highlightbackground="#e5e7eb", highlightthickness=1)
    card.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.86, relheight=0.78)
    return card

def clear_card():
    if hasattr(root, "current_card") and root.current_card:
        try: root.unbind("<Key>")
        except: pass
        root.current_card.destroy()
        root.current_card = None

# ===================== FRAMES / PAGES =====================
class LandingFrame(Frame):
    def __init__(self, master):
        super().__init__(master, bg=PALETTE["card_bg"], bd=0, highlightbackground="#e5e7eb", highlightthickness=1)

        Label(self, text="🎓 Welcome to the Quiz Hub", font=FONT_H1,
              bg=PALETTE["card_bg"], fg=PALETTE["text"]).pack(pady=(18, 4))

        Label(self, text="Choose how you want to continue:",
              font=FONT_META, bg=PALETTE["card_bg"], fg=PALETTE["muted"]).pack()

        btns = Frame(self, bg=PALETTE["card_bg"])
        btns.pack(pady=16)

        b1 = Button(btns, text="User Login", font=FONT_BTN, bg=PALETTE["accent"], fg=PALETTE["btn_text"],
                    bd=0, padx=22, pady=10, activebackground=PALETTE["accent_dark"],
                    command=show_user_login)
        b1.grid(row=0, column=0, padx=10)
        style_btn(b1, PALETTE["accent"], PALETTE["accent_dark"])

        b2 = Button(btns, text="User Signup", font=FONT_BTN, bg=PALETTE["success"], fg=PALETTE["btn_text"],
                    bd=0, padx=22, pady=10, activebackground="#15803d",
                    command=show_user_signup)
        b2.grid(row=0, column=1, padx=10)
        style_btn(b2, PALETTE["success"], "#15803d")

        b3 = Button(btns, text="Admin Login", font=FONT_BTN, bg=PALETTE["danger"], fg=PALETTE["btn_text"],
                    bd=0, padx=22, pady=10, activebackground="#991b1b",
                    command=show_admin_login)
        b3.grid(row=0, column=2, padx=10)
        style_btn(b3, PALETTE["danger"], "#991b1b")

class UserAuthFrame(Frame):
    def __init__(self, master, mode="login"):
        super().__init__(master, bg=PALETTE["card_bg"], bd=0, highlightbackground="#e5e7eb", highlightthickness=1)
        self.mode = mode
        title = "👤 User Login" if mode=="login" else "📝 User Signup"
        Label(self, text=title, font=FONT_H1, bg=PALETTE["card_bg"], fg=PALETTE["text"]).pack(pady=(18,6))

        form = Frame(self, bg=PALETTE["card_bg"])
        form.pack(pady=10)

        Label(form, text="Username", font=FONT_META, bg=PALETTE["card_bg"], fg=PALETTE["muted"]).grid(row=0, column=0, sticky="w")
        self.u_var = StringVar()
        Entry(form, textvariable=self.u_var, font=("Segoe UI", 12), width=28).grid(row=1, column=0, pady=(2,8))

        Label(form, text="Password", font=FONT_META, bg=PALETTE["card_bg"], fg=PALETTE["muted"]).grid(row=2, column=0, sticky="w")
        self.p_var = StringVar()
        Entry(form, textvariable=self.p_var, show="•", font=("Segoe UI", 12), width=28).grid(row=3, column=0, pady=(2,8))

        if mode == "signup":
            Label(form, text="Confirm Password", font=FONT_META, bg=PALETTE["card_bg"], fg=PALETTE["muted"]).grid(row=4, column=0, sticky="w")
            self.c_var = StringVar()
            Entry(form, textvariable=self.c_var, show="•", font=("Segoe UI", 12), width=28).grid(row=5, column=0, pady=(2,8))

        btns = Frame(self, bg=PALETTE["card_bg"])
        btns.pack(pady=6)

        if mode == "login":
            b = Button(btns, text="Login", font=FONT_BTN, bg=PALETTE["accent"], fg=PALETTE["btn_text"],
                       bd=0, padx=22, pady=8, activebackground=PALETTE["accent_dark"],
                       command=self.do_login)
            b.grid(row=0, column=0, padx=8)
            style_btn(b, PALETTE["accent"], PALETTE["accent_dark"])
        else:
            b = Button(btns, text="Create Account", font=FONT_BTN, bg=PALETTE["success"], fg=PALETTE["btn_text"],
                       bd=0, padx=22, pady=8, activebackground="#15803d",
                       command=self.do_signup)
            b.grid(row=0, column=0, padx=8)
            style_btn(b, PALETTE["success"], "#15803d")

        Button(btns, text="Back", font=FONT_BTN, bg="#9ca3af", fg="white",
               bd=0, padx=22, pady=8, activebackground="#6b7280",
               command=show_landing).grid(row=0, column=1, padx=8)

    def do_login(self):
        u = self.u_var.get().strip()
        p = self.p_var.get()
        users = load_users()
        if u in users and users[u].get("password") == p and users[u].get("role","user") == "user":
            show_quiz_select(u)
        else:
            tmsg.showerror("Login Failed", "Invalid username or password (or not a user).")

    def do_signup(self):
        u = self.u_var.get().strip()
        p = self.p_var.get()
        c = self.c_var.get()
        if not u or not p:
            tmsg.showwarning("Missing", "Please enter username and password.")
            return
        if p != c:
            tmsg.showwarning("Mismatch", "Passwords do not match.")
            return
        users = load_users()
        if u in users:
            tmsg.showerror("Exists", "Username already exists.")
            return
        users[u] = {"password": p, "role": "user"}
        save_users(users)
        tmsg.showinfo("Success", "Account created. You can log in now.")
        show_user_login()

class AdminLoginFrame(Frame):
    def __init__(self, master):
        super().__init__(master, bg=PALETTE["card_bg"], bd=0, highlightbackground="#e5e7eb", highlightthickness=1)
        Label(self, text="🛡️ Admin Login", font=FONT_H1, bg=PALETTE["card_bg"], fg=PALETTE["text"]).pack(pady=(18,6))

        form = Frame(self, bg=PALETTE["card_bg"])
        form.pack(pady=10)

        Label(form, text="Admin Username", font=FONT_META, bg=PALETTE["card_bg"], fg=PALETTE["muted"]).grid(row=0, column=0, sticky="w")
        self.u_var = StringVar()
        Entry(form, textvariable=self.u_var, font=("Segoe UI", 12), width=28).grid(row=1, column=0, pady=(2,8))

        Label(form, text="Password", font=FONT_META, bg=PALETTE["card_bg"], fg=PALETTE["muted"] if 'PALETATE' in globals() else PALETTE["muted"]).grid(row=2, column=0, sticky="w")
        self.p_var = StringVar()
        Entry(form, textvariable=self.p_var, show="•", font=("Segoe UI", 12), width=28).grid(row=3, column=0, pady=(2,8))

        btns = Frame(self, bg=PALETTE["card_bg"])
        btns.pack(pady=6)
        b = Button(btns, text="Login", font=FONT_BTN, bg=PALETTE["danger"], fg=PALETTE["btn_text"],
                   bd=0, padx=22, pady=8, activebackground="#991b1b",
                   command=self.do_login)
        b.grid(row=0, column=0, padx=8)
        style_btn(b, PALETTE["danger"], "#991b1b")

        Button(btns, text="Back", font=FONT_BTN, bg="#9ca3af", fg="white",
               bd=0, padx=22, pady=8, activebackground="#6b7280",
               command=show_landing).grid(row=0, column=1, padx=8)

    def do_login(self):
        u = self.u_var.get().strip()
        p = self.p_var.get()
        users = load_users()
        if u in users and users[u].get("password") == p and users[u].get("role") == "admin":
            show_admin_dashboard(u)
        else:
            tmsg.showerror("Login Failed", "Invalid admin credentials.")

class QuizSelectFrame(Frame):
    def __init__(self, master, username):
        super().__init__(master, bg=PALETTE["card_bg"], bd=0, highlightbackground="#e5e7eb", highlightthickness=1)
        self.username = username
        Label(self, text=f"Hello, {username}", font=FONT_META, bg=PALETTE["card_bg"], fg=PALETTE["muted"]).pack(anchor="ne", padx=16, pady=(12,0))
        Label(self, text="📘 Choose a Quiz", font=FONT_H1, bg=PALETTE["card_bg"], fg=PALETTE["text"]).pack(pady=(6,10))

        self.choice = IntVar(value=-1)
        box = Frame(self, bg=PALETTE["card_bg"])
        box.pack(pady=6)
        for i, q in enumerate(QUIZ_DEFS):
            Radiobutton(box, text=q["title"], variable=self.choice, value=i,
                        bg=PALETTE["card_bg"], font=FONT_OPT, anchor="w",
                        selectcolor=PALETTE["radio_select"]).pack(fill="x", padx=10, pady=6)

        btns = Frame(self, bg=PALETTE["card_bg"])
        btns.pack(pady=12)
        start = Button(btns, text="Start", font=FONT_BTN, bg=PALETTE["success"], fg=PALETTE["btn_text"],
                       bd=0, padx=22, pady=8, activebackground="#15803d",
                       command=self.start_quiz)
        start.grid(row=0, column=0, padx=8)
        style_btn(start, PALETTE["success"], "#15803d")

        Button(btns, text="Logout", font=FONT_BTN, bg="#9ca3af", fg="white",
               bd=0, padx=22, pady=8, activebackground="#6b7280",
               command=show_landing).grid(row=0, column=1, padx=8)

    def start_quiz(self):
        idx = self.choice.get()
        if idx not in range(len(QUIZ_DEFS)):
            tmsg.showwarning("Pick a quiz", "Please select a quiz to continue.")
            return
        show_quiz(self.username, QUIZ_DEFS[idx])

class QuizFrame(Frame):
    def __init__(self, master, user_name, quiz_def):
        super().__init__(master, bg=PALETTE["card_bg"], bd=0, highlightbackground="#e5e7eb", highlightthickness=1)
        self.user_name = user_name
        self.quiz_def = quiz_def

        # Load quiz
        file_path = script_path(quiz_def["path"])
        self.quiz_data = load_quiz_from_file(file_path)

        self.q_no = 0
        self.score = 0
        self.user_choices = []
        self.start_time = datetime.now()
        self.selected_index = IntVar(value=-1)

        # Header
        header = Frame(self, bg=PALETTE["card_bg"])
        header.pack(fill="x", pady=(16, 8), padx=18)
        Label(header, text=quiz_def["title"], font=FONT_H1, bg=PALETTE["card_bg"], fg=PALETTE["text"]).pack(side="left")
        Label(header, text=f"Candidate: {user_name}", font=FONT_META, bg=PALETTE["card_bg"], fg=PALETTE["muted"]).pack(side="right")

        # Progress
        pf = Frame(self, bg=PALETTE["card_bg"])
        pf.pack(fill="x", padx=18, pady=(0, 8))
        self.progress_var = IntVar(value=0)
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Blue.Horizontal.TProgressbar",
                        troughcolor="#eef2ff", background=PALETTE["accent"], thickness=12,
                        troughrelief="flat", bordercolor="#eef2ff",
                        lightcolor=PALETTE["accent"], darkcolor=PALETTE["accent_dark"])
        ttk.Progressbar(pf, style="Blue.Horizontal.TProgressbar",
                        variable=self.progress_var, maximum=100).pack(fill="x", side="left", expand=True)
        self.progress_label = Label(pf, text="0%", font=FONT_META, bg=PALETTE["card_bg"], fg=PALETTE["muted"])
        self.progress_label.pack(side="left", padx=(8,0))

        # Question
        qc = Frame(self, bg=PALETTE["card_bg"])
        qc.pack(fill="both", expand=True, padx=22, pady=(6,0))
        self.question_label = Label(qc, text="", font=FONT_Q, wraplength=760, justify="left",
                                    bg=PALETTE["card_bg"], fg=PALETTE["text"])
        self.question_label.pack(anchor="w", pady=(6, 10))

        self.options_frame = Frame(qc, bg=PALETTE["card_bg"])
        self.options_frame.pack(fill="x", pady=(2, 10))
        self.option_buttons = []
        for i in range(4):
            rb = Radiobutton(
                self.options_frame, text="", variable=self.selected_index, value=i,
                font=FONT_OPT, bg=PALETTE["card_bg"], fg=PALETTE["text"],
                selectcolor=PALETTE["radio_select"], anchor="w",
                padx=12, pady=4, activebackground=PALETTE["card_bg"], highlightthickness=0
            )
            rb.pack(fill="x", pady=4)
            self.option_buttons.append(rb)

        # Buttons
        br = Frame(self, bg=PALETTE["card_bg"])
        br.pack(pady=(6, 6))
        btn_next = Button(br, text="Next", font=FONT_BTN, bg=PALETTE["success"], fg=PALETTE["btn_text"],
                          padx=22, pady=6, bd=0, activebackground="#15803d", cursor="hand2",
                          command=self.next_question)
        btn_next.grid(row=0, column=0, padx=8)
        style_btn(btn_next, PALETTE["success"], "#15803d")

        btn_restart = Button(br, text="Restart", font=FONT_BTN, bg=PALETTE["accent"], fg=PALETTE["btn_text"],
                             padx=22, pady=6, bd=0, activebackground=PALETTE["accent_dark"], cursor="hand2",
                             command=self.restart_quiz)
        btn_restart.grid(row=0, column=1, padx=8)
        style_btn(btn_restart, PALETTE["accent"], PALETTE["accent_dark"])

        btn_quit = Button(br, text="Quit", font=FONT_BTN, bg=PALETTE["danger"], fg=PALETTE["btn_text"],
                          padx=22, pady=6, bd=0, activebackground="#991b1b", cursor="hand2",
                          command=show_landing)
        btn_quit.grid(row=0, column=2, padx=8)
        style_btn(btn_quit, PALETTE["danger"], "#991b1b")

        self.status_label = Label(self, text="", font=FONT_META, bg=PALETTE["card_bg"], fg=PALETTE["muted"])
        self.status_label.pack(pady=(2,12))

        root.bind("<Key>", self._key_handler)

        if not self.quiz_data:
            tmsg.showinfo("Info", "No quiz data for this quiz.")
            show_quiz_select(user_name)
        else:
            self.display_question()

    def display_question(self):
        q = self.quiz_data[self.q_no]
        self.question_label.config(text=f"Q{self.q_no+1}. {q['question']}")
        for i in range(4):
            if i < len(q["options"]):
                self.option_buttons[i].config(text=q["options"][i], value=i, state=NORMAL)
            else:
                self.option_buttons[i].config(text="", value=i, state=DISABLED)
        self.selected_index.set(-1)  # clear selection
        progress = int(((self.q_no + 1) / len(self.quiz_data)) * 100)
        self.progress_var.set(progress)
        self.progress_label.config(text=f"{progress}%")
        self.status_label.config(text=f"Question {self.q_no+1} of {len(self.quiz_data)}  |  Score: {self.score}")

    def next_question(self):
        choice = self.selected_index.get()
        if choice == -1:
            tmsg.showwarning("Heads up", "Please select an option before continuing.")
            return

        if self.quiz_data[self.q_no]["options"][choice] == self.quiz_data[self.q_no]["answer"]:
            self.score += 1
        if len(self.user_choices) == self.q_no:
            self.user_choices.append(choice)
        else:
            self.user_choices[self.q_no] = choice

        self.q_no += 1
        if self.q_no < len(self.quiz_data):
            self.display_question()
        else:
            self.finish_quiz()

    def restart_quiz(self):
        self.q_no = 0
        self.score = 0
        self.user_choices = []
        self.start_time = datetime.now()
        self.display_question()

    def finish_quiz(self):
        end_time = datetime.now()
        duration_seconds = (end_time - self.start_time).total_seconds()
        save_result_to_file(self.user_name, self.score, len(self.quiz_data), duration_seconds,
                            self.user_choices, self.quiz_data, self.quiz_def["title"])
        percent = round((self.score/len(self.quiz_data))*100, 2)
        if self.score >= len(self.quiz_data) * 0.7:
            tmsg.showinfo("Quiz Completed",
                      f"Well done, {self.user_name}!\n\n"
                      f"{self.quiz_def['title']}\n"
                      f"Score: {self.score}/{len(self.quiz_data)}  ({percent}%)")
        else:
            tmsg.showinfo("Quiz Completed",
                      f"Good effort, {self.user_name}.\n\n"
                      f"{self.quiz_def['title']}\n"
                      f"Score: {self.score}/{len(self.quiz_data)}  ({percent}%)\n\n"
                      f"Consider reviewing the material and trying again.")
        show_quiz_select(self.user_name)

    def _key_handler(self, event):
        if event.char in ("1","2","3","4"):
            idx = int(event.char) - 1
            if 0 <= idx < 4 and self.option_buttons[idx]["state"] == NORMAL:
                self.selected_index.set(idx)
        elif event.keysym in ("Return","KP_Enter") or event.char.lower() == "n":
            self.next_question()
        elif event.char.lower() == "r":
            self.restart_quiz()
        elif event.keysym == "Escape":
            show_landing()

def load_results_for_charts():
    path = script_path("results.txt")
    rows = []
    if not os.path.exists(path):
        return rows

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                parts = [p.strip() for p in line.split("|")]
                quiz = None
                score = total = None
                for p in parts[1:]:
                    if p.lower().startswith("quiz:"):
                        quiz = p.split(":", 1)[1].strip()
                    elif p.lower().startswith("score:"):
                        st = p.split(":", 1)[1].strip()  # e.g. "8/10"
                        if "/" in st:
                            a, b = st.split("/", 1)
                            score = int(a.strip()); total = int(b.strip())
                if quiz is None or score is None or total is None:
                    continue
                rows.append({"quiz": quiz, "score": score, "total": total})
            except:
                # skip malformed lines
                continue
    return rows

class AdminDashboardFrame(Frame):
    def __init__(self, master, admin_name):
        super().__init__(master, bg=PALETTE["card_bg"], bd=0, highlightbackground="#e5e7eb", highlightthickness=1)
        self.admin_name = admin_name

        Label(self, text=f"🛡️ Admin Dashboard", font=FONT_H1, bg=PALETTE["card_bg"], fg=PALETTE["text"]).pack(pady=(16,4))
        Label(self, text=f"Welcome, {admin_name}", font=FONT_META, bg=PALETTE["card_bg"], fg=PALETTE["muted"]).pack()

        # Top buttons
        top = Frame(self, bg=PALETTE["card_bg"])
        top.pack(fill="x", padx=16, pady=6)

        Button(top, text="Refresh", font=FONT_BTN, bg=PALETTE["accent"], fg=PALETTE["btn_text"], bd=0,
               padx=16, pady=6, activebackground=PALETTE["accent_dark"],
               command=self.refresh).pack(side="left", padx=(0,8))

        Button(top, text="Charts", font=FONT_BTN, bg="#0ea5e9", fg="white", bd=0,
               padx=16, pady=6, activebackground="#0284c7",
               command=self.open_charts).pack(side="left", padx=(0,8))

        Button(top, text="Back to Landing", font=FONT_BTN, bg="#9ca3af", fg="white", bd=0,
               padx=16, pady=6, activebackground="#6b7280",
               command=show_landing).pack(side="left")

        # Filter row
        filt = Frame(self, bg=PALETTE["card_bg"])
        filt.pack(fill="x", padx=16, pady=(4,0))
        Label(filt, text="Filter by username:", font=FONT_META, bg=PALETTE["card_bg"], fg=PALETTE["muted"]).pack(side="left")
        self.filter_var = StringVar()
        Entry(filt, textvariable=self.filter_var, font=("Segoe UI", 11), width=22).pack(side="left", padx=6)
        Button(filt, text="Apply", font=FONT_BTN, bg=PALETTE["success"], fg="white", bd=0,
               padx=12, pady=4, activebackground="#15803d",
               command=self.refresh).pack(side="left", padx=6)

        # ----- Resizable split panes -----
        hpane = ttk.Panedwindow(self, orient="horizontal")
        hpane.pack(fill="both", expand=True, padx=16, pady=10)

        # LEFT: results summary
        left = Frame(hpane, bg=PALETTE["card_bg"])
        Label(left, text="results.txt", font=FONT_META, bg=PALETTE["card_bg"], fg=PALETTE["muted"]).pack(anchor="w")
        left_wrap = Frame(left, bg=PALETTE["card_bg"])
        left_wrap.pack(fill="both", expand=True)

        self.summary = Text(left_wrap, wrap="word", font=("Consolas", 11), bg="#fbfbfb")
        self.summary.pack(side="left", fill="both", expand=True)
        left_scroll = Scrollbar(left_wrap, orient="vertical", command=self.summary.yview)
        left_scroll.pack(side="right", fill="y")
        self.summary.configure(yscrollcommand=left_scroll.set)

        # RIGHT: attempts list + viewer (vertical split)
        right = Frame(hpane, bg=PALETTE["card_bg"])
        Label(right, text="attempts/", font=FONT_META, bg=PALETTE["card_bg"], fg=PALETTE["muted"]).pack(anchor="w")

        vpane = ttk.Panedwindow(right, orient="vertical")
        vpane.pack(fill="both", expand=True)

        top_right = Frame(vpane, bg=PALETTE["card_bg"])
        list_wrap = Frame(top_right, bg=PALETTE["card_bg"])
        list_wrap.pack(fill="both", expand=True)
        self.attempt_list = Listbox(list_wrap, font=("Consolas", 10))
        self.attempt_list.pack(side="left", fill="both", expand=True)
        self.attempt_list.bind("<<ListboxSelect>>", self.open_attempt)
        list_scroll = Scrollbar(list_wrap, orient="vertical", command=self.attempt_list.yview)
        list_scroll.pack(side="right", fill="y")
        self.attempt_list.configure(yscrollcommand=list_scroll.set)

        bottom_right = Frame(vpane, bg=PALETTE["card_bg"])
        view_wrap = Frame(bottom_right, bg=PALETTE["card_bg"])
        view_wrap.pack(fill="both", expand=True)
        self.attempt_view = Text(view_wrap, wrap="word", font=("Consolas", 11), bg="#fbfbfb")
        self.attempt_view.pack(side="left", fill="both", expand=True)
        view_scroll = Scrollbar(view_wrap, orient="vertical", command=self.attempt_view.yview)
        view_scroll.pack(side="right", fill="y")
        self.attempt_view.configure(yscrollcommand=view_scroll.set)

        # Initial sizes (draggable)
        hpane.add(left, weight=6)
        hpane.add(right, weight=4)
        vpane.add(top_right, weight=1)
        vpane.add(bottom_right, weight=2)

        self.refresh()

    def refresh(self):
        # summary
        self.summary.config(state=NORMAL)
        self.summary.delete("1.0", END)
        res_path = script_path("results.txt")
        filt = self.filter_var.get().strip().lower()
        if os.path.exists(res_path):
            with open(res_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            if filt:
                lines = [ln for ln in lines if f"name: {filt}" in ln.lower() or f"Name: {filt}" in ln]
            self.summary.insert("1.0", "".join(lines) if lines else "(No matching entries)")
        else:
            self.summary.insert("1.0", "(results.txt not found)")
        self.summary.config(state=DISABLED)

        # attempts list
        self.attempt_list.delete(0, END)
        attempts_dir = script_path("attempts")
        if os.path.isdir(attempts_dir):
            files = sorted(os.listdir(attempts_dir))
            filt = self.filter_var.get().strip().lower()
            for fn in files:
                if fn.lower().endswith(".txt"):
                    if filt and filt not in fn.lower():
                        continue
                    self.attempt_list.insert(END, fn)
        self.attempt_view.delete("1.0", END)

    def open_attempt(self, event=None):
        sel = self.attempt_list.curselection()
        if not sel:
            return
        fn = self.attempt_list.get(sel[0])
        p = script_path("attempts", fn)
        self.attempt_view.delete("1.0", END)
        try:
            with open(p, "r", encoding="utf-8") as f:
                self.attempt_view.insert("1.0", f.read())
        except Exception as e:
            self.attempt_view.insert("1.0", f"(Error reading file)\n{e}")

    # ---------- NEW: Charts ----------
    def open_charts(self):
        try:
            data = load_results_for_charts()
        except Exception as e:
            tmsg.showerror("Charts", f"Failed to load results: {e}")
            return

        if not data:
            tmsg.showinfo("Charts", "No data in results.txt yet.")
            return

    # Sum correct vs total per quiz/subject
        totals = {}  # quiz_title -> {"got": int, "possible": int}
        for row in data:
            qtitle = row["quiz"] or "Unknown"
            d = totals.setdefault(qtitle, {"got": 0, "possible": 0})
            d["got"] += int(row["score"])
            d["possible"] += int(row["total"])

        # Order subjects by QUIZ_DEFS if available
        try:
            titles = [qd["title"] for qd in QUIZ_DEFS]
        except NameError:
            titles = list(totals.keys())

        if not titles:
            titles = list(totals.keys()) or ["No Subjects"]

        n = max(1, len(titles))
        fig, axes = plt.subplots(1, n, figsize=(5*n, 4.6), dpi=100)
        if n == 1:
            axes = [axes]

        for ax, title in zip(axes, titles):
            agg = totals.get(title, {"got": 0, "possible": 0})
            got = agg["got"]
            poss = agg["possible"]
            miss = max(0, poss - got)

            if poss == 0:
                ax.pie([1], labels=["No Attempts"], autopct=lambda *_: "", startangle=90)
            else:
                ax.pie(
                    [got, miss],
                    labels=["Correct", "Incorrect"],
                    autopct="%1.1f%%",
                    startangle=90
                )
            ax.set_title(title)
            ax.axis("equal")

        fig.tight_layout()

        win = Toplevel(self)
        win.title("Quiz Score Pies (by Subject)")
        canvas = FigureCanvasTkAgg(fig, master=win)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

# ===================== NAVIGATION =========================
def show_landing():
    clear_card()
    card = make_card(root)
    frm = LandingFrame(card)
    frm.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.9, relheight=0.9)
    root.current_card = card

def show_user_login():
    clear_card()
    card = make_card(root)
    frm = UserAuthFrame(card, mode="login")
    frm.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.9, relheight=0.9)
    root.current_card = card

def show_user_signup():
    clear_card()
    card = make_card(root)
    frm = UserAuthFrame(card, mode="signup")
    frm.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.9, relheight=0.9)
    root.current_card = card

def show_admin_login():
    clear_card()
    card = make_card(root)
    frm = AdminLoginFrame(card)
    frm.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.9, relheight=0.9)
    root.current_card = card

def show_admin_dashboard(admin_name):
    clear_card()
    card = make_card(root)
    frm = AdminDashboardFrame(card, admin_name)
    # a bit wider & taller than before
    frm.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.98, relheight=0.96)
    root.current_card = card


def show_quiz_select(username):
    clear_card()
    card = make_card(root)
    frm = QuizSelectFrame(card, username)
    frm.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.9, relheight=0.9)
    root.current_card = card

def show_quiz(username, quiz_def):
    clear_card()
    card = make_card(root)
    frm = QuizFrame(card, username, quiz_def)
    frm.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.96, relheight=0.94)
    root.current_card = card

# ===================== BOOTSTRAP =========================
root = Tk()
root.title("Quiz Hub")
root.geometry("980x650")
root.minsize(860, 560)
root.configure(bg=PALETTE["bg_bottom"])
root.current_card = None

ensure_dirs()
ensure_default_admin()

# Background gradient canvas
bg_canvas = Canvas(root, highlightthickness=0, bd=0)
bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)
root.update_idletasks()
gradient_background(bg_canvas, root.winfo_width(), root.winfo_height())

show_landing()
root.mainloop()