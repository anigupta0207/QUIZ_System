from tkinter import *
import tkinter.messagebox as tmsg

# LOAD QUIZ DATA FROM TXT FILE
def load_quiz_from_file(filename):
    quiz_list = []
    try:
        with open(filename, "r") as f:
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

    q_no += 1
    if q_no < len(quiz_data):
        display_question()
    else:
        show_result()

def show_result():
    tmsg.showinfo("Quiz Completed", f"Your Score: {score}/{len(quiz_data)}")
    root.destroy()

def restart_quiz():
    global q_no, score
    q_no = 0
    score = 0
    display_question()

# MAIN APPLICATION SETUP
root = Tk()
root.title("Quiz App")
root.geometry("520x420")
root.config(bg="white")
selected_option = StringVar(value="")
q_no = 0
score = 0

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


display_question() 
root.mainloop()