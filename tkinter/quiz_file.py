from tkinter import *
from tkinter import messagebox as tmsg
from tkinter import simpledialog
from tkinter import ttk
from datetime import datetime
import os

# -------------------- THEME --------------------
PALETTE = {
    "bg_top":     "#eef3ff",
    "bg_bottom":  "#f9fcff",
    "card_bg":    "#ffffff",
    "text":       "#1f2937",
    "muted":      "#6b7280",
    "accent":     "#2563eb",
    "accent_dark":"#1e40af",
    "success":    "#16a34a",
    "danger":     "#dc2626",
    "radio_select":"#e0edff",
    "btn_text":   "#ffffff",
}

FONT_H1   = ("Segoe UI", 20, "bold")
FONT_Q    = ("Segoe UI", 16, "bold")
FONT_OPT  = ("Segoe UI", 14)
FONT_META = ("Segoe UI", 11)
FONT_BTN  = ("Segoe UI", 12, "bold")

# -------------------- QUIZ LOADER --------------------
def load_quiz_from_file(filename):
    quiz_list = []
    try:
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read().strip()

        blocks = [b for b in content.split("\n\n") if b.strip()]
        for block in blocks:
            lines = [ln.strip() for ln in block.split("\n") if ln.strip()]
            if len(lines) < 3:
                continue

            question_line = lines[0]
            options = []
            answer = ""

            for line in lines[1:]:
                if line.startswith(("A)", "B)", "C)", "D)")):
                    options.append(line[3:].strip())
                elif line.startswith("Answer:"):
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

# -------------------- SAVE RESULTS --------------------
def save_result_to_file(name, score, total, duration_seconds, user_choices, quiz_data):
    os.makedirs("attempts", exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    percent = round((score/total)*100, 2) if total else 0
    with open("results.txt", "a", encoding="utf-8") as f:
        f.write(f"{timestamp} | Name: {name} | Score: {score}/{total} | {percent}% | Duration: {int(duration_seconds)}s\n")

    ts_slug = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = "".join(c for c in name if c.isalnum() or c in (" ","_","-")).strip().replace(" ", "_") or "Anonymous"
    attempt_path = os.path.join("attempts", f"{ts_slug}_{safe_name}.txt")

    with open(attempt_path, "w", encoding="utf-8") as f:
        f.write(f"Name: {name}\n")
        f.write(f"Timestamp: {timestamp}\n")
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

# -------------------- UI HELPERS --------------------
def gradient_background(canvas, w, h, start=PALETTE["bg_top"], end=PALETTE["bg_bottom"]):
    r1, g1, b1 = root.winfo_rgb(start)
    r2, g2, b2 = root.winfo_rgb(end)
    r_ratio = (r2 - r1) / h
    g_ratio = (g2 - g1) / h
    b_ratio = (b2 - b1) / h
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

# -------------------- QUIZ LOGIC --------------------
def display_question():
    global q_no
    q = quiz_data[q_no]

    question_label.config(text=f"Q{q_no+1}. {q['question']}")

    # assign option texts and integer values 0..3
    for i in range(4):
        if i < len(q["options"]):
            option_buttons[i].config(
                text=q["options"][i],
                value=i,                 # integer value
                state=NORMAL,
                selectcolor=PALETTE["radio_select"],
                activebackground=PALETTE["card_bg"],
                bg=PALETTE["card_bg"]
            )
        else:
            option_buttons[i].config(text="", value=i, state=DISABLED)

    # CLEAR SELECTION using a sentinel value that matches no radio
    selected_index.set(-1)

    # update progress
    progress = int(((q_no + 1) / len(quiz_data)) * 100)
    progress_var.set(progress)
    progress_label.config(text=f"{progress}%")

    status_label.config(text=f"Question {q_no+1} of {len(quiz_data)}  |  Score: {score}")

def next_question():
    global q_no, score
    choice = selected_index.get()
    if choice == -1:
        tmsg.showwarning("Heads up", "Please select an option before continuing.")
        return

    # check correctness
    if 0 <= choice < len(quiz_data[q_no]["options"]):
        if quiz_data[q_no]["options"][choice] == quiz_data[q_no]["answer"]:
            score += 1

    # store picked index
    if len(user_choices) == q_no:
        user_choices.append(choice)
    else:
        user_choices[q_no] = choice

    q_no += 1
    if q_no < len(quiz_data):
        display_question()
    else:
        show_result()

def show_result():
    end_time = datetime.now()
    duration_seconds = (end_time - start_time).total_seconds()
    save_result_to_file(user_name, score, len(quiz_data), duration_seconds, user_choices, quiz_data)

    percent = round((score/len(quiz_data))*100, 2)
    tmsg.showinfo("Quiz Completed",
                  f"Well done, {user_name}!\n\n"
                  f"Score: {score}/{len(quiz_data)}  ({percent}%)")
    root.destroy()

def restart_quiz(event=None):
    global q_no, score, user_choices, start_time
    q_no = 0
    score = 0
    user_choices = []
    start_time = datetime.now()
    display_question()

def key_handler(event):
    if event.char in ("1","2","3","4"):
        idx = int(event.char) - 1
        if 0 <= idx < 4 and option_buttons[idx]["state"] == NORMAL:
            selected_index.set(idx)
    elif event.keysym in ("Return","KP_Enter") or event.char.lower() == "n":
        next_question()
    elif event.char.lower() == "r":
        restart_quiz()
    elif event.keysym == "Escape":
        root.destroy()

# -------------------- MAIN WINDOW --------------------
root = Tk()
root.title("Quiz App")
root.geometry("900x600")
root.minsize(820, 520)
root.configure(bg=PALETTE["bg_bottom"])
root.withdraw()  # hide while asking name

# Background gradient
bg_canvas = Canvas(root, highlightthickness=0, bd=0, width=900, height=600)
bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)
root.update_idletasks()
gradient_background(bg_canvas, root.winfo_width(), root.winfo_height())

# Card
card = Frame(root, bg=PALETTE["card_bg"], bd=0, highlightbackground="#e5e7eb", highlightthickness=1)
card.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.86, relheight=0.78)

# Header
header = Frame(card, bg=PALETTE["card_bg"])
header.pack(fill="x", pady=(16, 8), padx=18)

title_label = Label(header, text="📝 Multiple Choice Quiz", font=FONT_H1, bg=PALETTE["card_bg"], fg=PALETTE["text"])
title_label.pack(side="left")

meta_label = Label(header, text="", font=FONT_META, bg=PALETTE["card_bg"], fg=PALETTE["muted"])
meta_label.pack(side="right")

# Progress
progress_frame = Frame(card, bg=PALETTE["card_bg"])
progress_frame.pack(fill="x", padx=18, pady=(0, 8))

progress_var = IntVar(root, value=0)
# Fix typo above - initialize properly
progress_var = IntVar(value=0)

style = ttk.Style()
style.theme_use("clam")
style.configure("Blue.Horizontal.TProgressbar",
                troughcolor="#eef2ff", background=PALETTE["accent"], thickness=12,
                troughrelief="flat", bordercolor="#eef2ff", lightcolor=PALETTE["accent"], darkcolor=PALETTE["accent_dark"])

pbar = ttk.Progressbar(progress_frame, style="Blue.Horizontal.TProgressbar", variable=progress_var, maximum=100)
pbar.pack(fill="x", side="left", expand=True)

progress_label = Label(progress_frame, text="0%", font=FONT_META, bg=PALETTE["card_bg"], fg=PALETTE["muted"])
progress_label.pack(side="left", padx=(8, 0))

# Question area
q_container = Frame(card, bg=PALETTE["card_bg"])
q_container.pack(fill="both", expand=True, padx=22, pady=(6, 0))

question_label = Label(q_container, text="", font=FONT_Q, wraplength=760, justify="left", bg=PALETTE["card_bg"], fg=PALETTE["text"])
question_label.pack(anchor="w", pady=(6, 10))

# Options
selected_index = IntVar(card, value=-1)   # <-- sentinel: no selection
options_frame = Frame(q_container, bg=PALETTE["card_bg"])
options_frame.pack(fill="x", pady=(2, 10))

option_buttons = []
for i in range(4):
    rb = Radiobutton(
        options_frame,
        text="",
        variable=selected_index,
        value=i,                        # integer unique value
        font=FONT_OPT,
        bg=PALETTE["card_bg"],
        fg=PALETTE["text"],
        selectcolor=PALETTE["radio_select"],
        anchor="w",
        padx=12,
        pady=4,
        activebackground=PALETTE["card_bg"],
        highlightthickness=0
    )
    rb.pack(fill="x", pady=4)
    option_buttons.append(rb)

# Buttons
btn_row = Frame(card, bg=PALETTE["card_bg"])
btn_row.pack(pady=(6, 6))

btn_next = Button(btn_row, text="Next", font=FONT_BTN, bg=PALETTE["success"], fg=PALETTE["btn_text"], padx=22, pady=6, bd=0, activebackground="#15803d", cursor="hand2", command=next_question)
btn_next.grid(row=0, column=0, padx=8)
style_btn(btn_next, PALETTE["success"], "#15803d")

btn_restart = Button(btn_row, text="Restart", font=FONT_BTN, bg=PALETTE["accent"], fg=PALETTE["btn_text"], padx=22, pady=6, bd=0, activebackground=PALETTE["accent_dark"], cursor="hand2", command=restart_quiz)
btn_restart.grid(row=0, column=1, padx=8)
style_btn(btn_restart, PALETTE["accent"], PALETTE["accent_dark"])

btn_quit = Button(btn_row, text="Quit", font=FONT_BTN, bg=PALETTE["danger"], fg=PALETTE["btn_text"], padx=22, pady=6, bd=0, activebackground="#991b1b", cursor="hand2", command=root.destroy)
btn_quit.grid(row=0, column=2, padx=8)
style_btn(btn_quit, PALETTE["danger"], "#991b1b")

# Status
status_label = Label(card, text="", font=FONT_META, bg=PALETTE["card_bg"], fg=PALETTE["muted"])
status_label.pack(pady=(2, 12))

# Ask name
user_name = simpledialog.askstring("Identify Yourself", "Enter your name:", parent=root)
if not user_name or not user_name.strip():
    user_name = "Anonymous"
meta_label.config(text=f"Candidate: {user_name}")

# Load quiz relative to this script
script_dir = os.path.dirname(os.path.abspath(__file__))
quiz_data_path = os.path.join(script_dir, "quiz_data.txt")
quiz_data = load_quiz_from_file(quiz_data_path)

# Globals
q_no = 0
score = 0
user_choices = []
start_time = datetime.now()

if not quiz_data:
    root.deiconify()
    tmsg.showinfo("Info", "No quiz data available.")
    root.destroy()
else:
    # Keyboard shortcuts
    root.bind("<Key>", key_handler)

    # Show window
    root.deiconify()
    root.lift()
    root.focus_force()

    try:
        display_question()
    except Exception as e:
        tmsg.showerror("Error while displaying first question", str(e))

    root.mainloop()
