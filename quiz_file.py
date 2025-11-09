from tkinter import *
from tkinter import messagebox as tmsg
from datetime import datetime
from tkinter import simpledialog   
import os                          
       
# LOAD QUIZ DATA FROM TXT FILE
def load_quiz_from_file(filename):
    quiz_list = []
    try:
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read().strip()

        blocks = content.split("\n\n")      #Split by blank lines
        for block in blocks:
            lines = block.strip().split("\n")
            if not lines or len(lines) < 3:
                continue
            question_line = lines[0]
            options = []
            answer = ""

            for line in lines[1:]:          #Parse each line
                line = line.strip()
                if line.startswith("A)") or line.startswith("B)") or line.startswith("C)") or line.startswith("D)"):
                    options.append(line[3:].strip())
                elif line.startswith("Answer:"):
                    ans = line.split(":")[1].strip()
                    index = ord(ans.upper()) - ord('A')     
                    if 0 <= index < len(options):
                        answer = options[index]
            if question_line.startswith("Q:"):
                question = question_line[2:].strip()
            else:
                question = question_line.strip()

            if question and options and answer:
                quiz_list.append({
                    "question": question,
                    "options": options,
                    "answer": answer
                })
    except FileNotFoundError:
        tmsg.showerror("Error", f"File '{filename}' not found!")
        return []

    return quiz_list

# SAVE RESULT TO FILE  (REPLACE your function with this one)
def save_result_to_file(name, score, total, duration_seconds, user_choices, quiz_data):
    os.makedirs("attempts", exist_ok=True)  # ensure folder exists

    # --- summary line ---
    with open("results.txt", "a", encoding="utf-8") as f:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        percent = round((score/total)*100, 2) if total else 0
        f.write(f"{timestamp} | Name: {name} | Score: {score}/{total} | {percent}% | Duration: {int(duration_seconds)}s\n")

    # --- detailed attempt file ---
    ts_slug = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = "".join(c for c in name if c.isalnum() or c in (" ","_","-")).strip().replace(" ", "_") or "Anonymous"
    attempt_path = os.path.join("attempts", f"{ts_slug}_{safe_name}.txt")

    with open(attempt_path, "w", encoding="utf-8") as f:
        f.write(f"Name: {name}\n")
        f.write(f"Timestamp: {timestamp}\n")
        f.write(f"Total Questions: {len(quiz_data)}\n")
        f.write(f"Duration: {int(duration_seconds)} seconds\n")
        f.write("-"*60 + "\n\n")
        for i, q in enumerate(quiz_data):
            chosen = user_choices[i] if i < len(user_choices) else ""
            is_correct = "Correct" if chosen == q["answer"] else "Incorrect"
            f.write(f"Q{i+1}. {q['question']}\n")
            for idx, opt in enumerate(q["options"]):
                tag = []
                if opt == q["answer"]:
                    tag.append("Correct")
                if opt == chosen:
                    tag.append("Chosen")
                tag_str = f" ({', '.join(tag)})" if tag else ""
                f.write(f"  {chr(ord('A')+idx)}) {opt}{tag_str}\n")
            f.write(f"Result: {is_correct}\n")
            f.write("-"*60 + "\n")
        f.write(f"\nFinal Score: {score}/{len(quiz_data)} ({percent}%)\n")

    return attempt_path


# QUIZ LOGIC
def display_question():
    global q_no
    selected_option.set("")
    q_data = quiz_data[q_no]

    question_label.config(text=f"Q{q_no+1}. {q_data['question']}")

    for i in range(len(q_data["options"])):
        option_buttons[i].config(text=q_data["options"][i], value=q_data["options"][i])
    for i in range(len(q_data["options"]), 4):
        option_buttons[i].config(text="", value="")

    status_label.config(text=f"Question {q_no+1} of {len(quiz_data)} | Score: {score}")

def next_question():
    global q_no, score
    choice = selected_option.get()
    if choice == "":
        tmsg.showwarning("Warning", "Please select an option!")
        return
    if choice == quiz_data[q_no]["answer"]:
        score += 1
    if len(user_choices) == q_no:       # Store user choice
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
    attempt_path = save_result_to_file(                                  
        user_name, score, len(quiz_data), duration_seconds, user_choices, quiz_data
    )
    tmsg.showinfo("Quiz Completed",                                      
                  f"Your Score: {score}/{len(quiz_data)}\n\n"
                 # f"Summary saved to: results.txt\n"
                 # f"Detailed attempt: {attempt_path}"
                )                   
    root.destroy()                                                      


def restart_quiz():
    global q_no, score, start_time, user_choices
    q_no = 0
    score = 0
    user_choices = []   # Reset user choices
    start_time = datetime.now()  # Reset start time
    display_question()

def view_results_admin():
    if not os.path.exists("results.txt"):
        tmsg.showinfo("Info", "No results recorded yet.")
        return
    top = Toplevel(root)
    top.title("All Results (Summary)")
    top.geometry("700x450")
    txt = Text(top, wrap="word", font=("Consolas", 11))
    txt.pack(fill="both", expand=True)
    with open("results.txt", "r", encoding="utf-8") as f:
        txt.insert("1.0", f.read())
    txt.config(state=DISABLED)

# MAIN APPLICATION SETUP
root = Tk()
root.title("Quiz App")
root.geometry("700x500")
root.config(bg="white")

root.withdraw()  # Hide main window during name input

selected_option = StringVar(root, value="")
q_no = 0
score = 0
user_choices = []                
start_time = datetime.now()

user_name = simpledialog.askstring("Identify Yourself", "Enter your name:", parent=root)  
if not user_name or not user_name.strip():                                                
    user_name = " "                                                               


quiz_data = load_quiz_from_file("quiz_data.txt")      # Load data from external file

if not quiz_data:
    tmsg.showinfo("Info", "No quiz data available.")
    root.destroy()
else:
    question_label = Label(root, text="", font="Arial 16", wraplength=480, justify="left", bg="white")
    question_label.pack(pady=(20,10), anchor="w", padx=20)

    option_buttons = []
    for i in range(4):
        rb = Radiobutton(root, text="", variable=selected_option, value="", font="Arial 14", bg="white", anchor="w", wraplength=420)
        rb.pack(fill="x", padx=40, pady=5)
        option_buttons.append(rb)

    btn_frame = Frame(root, bg="white")
    btn_frame.pack(pady=20)
    Button(btn_frame, text="Next", command=next_question, font="Arial 13", bg="green", fg="white", width=10).grid(row=0, column=0, padx=10)
    Button(btn_frame, text="Restart", command=restart_quiz, font="Arial 13", bg="blue", fg="white", width=10).grid(row=0, column=1, padx=10)
    Button(btn_frame, text="Quit", command=root.destroy, font="Arial 13", bg="red", fg="white", width=10).grid(row=0, column=2, padx=10)

    status_label = Label(root, text="", font="Arial 12", bg="white")
    status_label.pack(pady=(0,10))

    root.deiconify()  # Show main window
    root.lift()         # Bring to front
    root.focus_force()  # Focus on it

    try:
        display_question()
    except Exception as e:
        tmsg.showerror("Error while displaying first question", str(e))

    root.mainloop()