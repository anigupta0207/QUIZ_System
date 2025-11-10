import streamlit as st
import json
import os
import random
from datetime import datetime
import csv

# ---------- Utility Functions ----------

def load_quiz_data():
    """Load quiz data from JSON files."""

    current_dir = os.path.dirname(os.path.abspath(__file__))
    questions_dir = os.path.join(current_dir, "questions")

    quiz_files = {
        "C": {
            "basic": os.path.join(questions_dir, "c_b.json"),
            "intermediate": os.path.join(questions_dir, "c_i.json"),
            "advanced": os.path.join(questions_dir, "c_a.json"),
        },
        "C++": {
            "basic": os.path.join(questions_dir, "cpp_b.json"),
            "intermediate": os.path.join(questions_dir, "cpp_i.json"),
            "advanced": os.path.join(questions_dir, "cpp_a.json"),
        },
        "Python": {
            "basic": os.path.join(questions_dir, "python_b.json"),
            "intermediate": os.path.join(questions_dir, "python_i.json"),
            "advanced": os.path.join(questions_dir, "python_a.json"),
        },
    }
    data = load_quiz_data()
    user_scores = data["user_scores"]

    quizzes = {}

    # ✅ Load all quiz files properly
    for subject, levels in quiz_files.items():
        quizzes[subject] = {}
        for level, filename in levels.items():

            if os.path.exists(filename):
                with open(filename, "r", encoding="utf-8") as f:
                    quiz_data = json.load(f)

                # ✅ Random 20 questions ALWAYS correct
                all_q = quiz_data.get("questions", [])
                quiz_data["questions"] = random.sample(all_q, min(20, len(all_q)))

                quizzes[subject][level] = quiz_data
            else:
                st.error(f"Missing quiz file: {filename}")

    # ✅ Load user scores
    user_scores_path = os.path.join(current_dir, "user_scores.json")

    if os.path.exists(user_scores_path):
        try:
            with open(user_scores_path, "r", encoding="utf-8") as f:
                user_scores = json.load(f)
        except:
            user_scores = {}
    else:
        user_scores = {}

    return {
        "quizzes": quizzes,
        "user_scores": user_scores,
    }

def save_user_scores(user_scores):
    """Save user scores to JSON file."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    user_scores_path = os.path.join(current_dir, "user_scores.json")
    with open(user_scores_path, "w", encoding="utf-8") as f:
        json.dump(user_scores, f, indent=4)

        
def save_to_csv(username, quiz_id, quiz_title, score, completed_at):
    csv_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scores.csv")

    # Header exists?
    file_exists = os.path.isfile(csv_file)

    with open(csv_file, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        # Write header only once
        if not file_exists:
            writer.writerow(["username", "quiz_id", "quiz_title", "score", "completed_at"])

        writer.writerow([username, quiz_id, quiz_title, score, completed_at])


def show_quiz_app():
    st.set_page_config(page_title="PrepSecure", page_icon="🎯", layout="wide")
    st.title("🎯 Quiz Master Pro")

    # Session state initializers
    if "selected_subject" not in st.session_state:
        st.session_state.selected_subject = None
    if "selected_level" not in st.session_state:
        st.session_state.selected_level = None
    if "current_quiz" not in st.session_state:
        st.session_state.current_quiz = None
    if "current_question" not in st.session_state:
        st.session_state.current_question = 0
    if "score" not in st.session_state:
        st.session_state.score = 0
    if "quiz_completed" not in st.session_state:
        st.session_state.quiz_completed = False

    current_dir = os.path.dirname(os.path.abspath(__file__))
    questions_dir = os.path.join(current_dir, "questions")
    quiz_files = {
        "C": {
            "basic": os.path.join(questions_dir, "c_b.json"),
            "intermediate": os.path.join(questions_dir, "c_i.json"),
            "advanced": os.path.join(questions_dir, "c_a.json")
        },
        "C++": {
            "basic": os.path.join(questions_dir, "cpp_b.json"),
            "intermediate": os.path.join(questions_dir, "cpp_i.json"),
            "advanced": os.path.join(questions_dir, "cpp_a.json")
        },
        "Python": {
            "basic": os.path.join(questions_dir, "python_b.json"),
            "intermediate": os.path.join(questions_dir, "python_i.json"),
            "advanced": os.path.join(questions_dir, "python_a.json")
        }
    }

    # Login check
    if not st.session_state.get("logged_in", False):
        st.warning("Please log in first to access the quiz application.")
        return

    st.sidebar.success(f"✅ Logged in as: {st.session_state.username}")

    # --- SUBJECT SELECTION ---
    # 1. Select Subject
    # ... previous code ...
    # ✅ Tell web.py that quiz has started → start face & voice detection
    st.session_state.quiz_started = True

    if st.session_state.selected_subject is None:
        st.subheader("Choose Your Subject")

        subjects = [
            {"name": "C", "img": "https://img.icons8.com/color/150/c-programming.png", "desc": "Efficient systems programming"},
            {"name": "C++", "img": "https://img.icons8.com/color/150/c-plus-plus-logo.png", "desc": "Object-oriented programming"},
            {"name": "Python", "img": "https://img.icons8.com/color/150/python.png", "desc": "Rapid scripting & automation"}
        ]

        st.markdown("""
            <style>
                .subject-container {
                    text-align: center;
                    padding: 20px;
                    display: flex;
                    flex-direction: column;
                    justify-content: flex-start;
                    align-items: center;
                    min-height: 330px;
                }
                .center-btn {
                    display: flex;
                    justify-content: center;
                    margin-top: 10px;
                }
            </style>
        """, unsafe_allow_html=True)

        cols = st.columns(3)

        for i, card in enumerate(subjects):
            with cols[i]:
                st.markdown(f"""
                    <div class="subject-container">
                        <img src="{card['img']}" width="150">
                        <h3>{card['name']}</h3>
                        <p style='color:gray;'>{card['desc']}</p>
                    </div>
                """, unsafe_allow_html=True)

                # ✅ Perfectly centered button
                st.markdown("<div class='center-btn'>", unsafe_allow_html=True)
                if st.button(f"Select {card['name']}", key=f"sub_{card['name']}"):
                    st.session_state.selected_subject = card["name"]
                    st.session_state.selected_level = None
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

        st.stop()

    # --- LEVEL SELECTION ---
    #        --- LEVEL SELECTION (Modern Card Layout) ---
    # --- LEVEL SELECTION (Modern Card Layout + Start Button) ---
    if st.session_state.selected_level is None:

        st.subheader(f"Choose {st.session_state.selected_subject} Quiz Level")

        LEVELS = [
            {
                "level": "basic",
                "color": "linear-gradient(135deg,#89f7fe 0%, #66a6ff 100%)",
                "desc": "Beginner friendly",
                "emoji": "🌱"
            },
            {
                "level": "intermediate",
                "color": "linear-gradient(135deg,#fbc2eb 0%, #a6c1ee 100%)",
                "desc": "Boost your skills",
                "emoji": "🚀"
            },
            {
                "level": "advanced",
                "color": "linear-gradient(135deg,#f6d365 0%, #fda085 100%)",
                "desc": "Challenge yourself",
                "emoji": "🔥"
            }
        ]

        # ✅ Modern CSS
        st.markdown("""
        <style>
            .level-card {
                width: 100%;
                padding: 24px;
                border-radius: 18px;
                color: white;
                text-align: center;
                box-shadow: 0 4px 20px rgba(0,0,0,0.20);
                display: flex;
                flex-direction: column;
                justify-content: center;
                transition: 0.25s;
                cursor: default;
            }
            .level-card:hover {
                transform: translateY(-6px) scale(1.02);
                box-shadow: 0 12px 28px rgba(0,0,0,0.28);
            }
            .level-title {
                font-size: 26px;
                font-weight: 700;
            }
            .level-desc {
                font-size: 16px;
                margin-top: 6px;
                opacity: 0.9;
            }
            .start-btn button {
                background-color: rgba(255, 255, 255, 0.2) !important;
                border: 2px solid white !important;
                color: white !important;
                padding: 8px 20px !important;
                border-radius: 12px !important;
                font-size: 16px !important;
                margin-top: 15px !important;
                transition: 0.25s;
            }
            .start-btn button:hover {
                background-color: white !important;
                color: black !important;
            }
        </style>
        """, unsafe_allow_html=True)

        cols = st.columns(3)

        for i, item in enumerate(LEVELS):
            with cols[i]:
                
                # Card UI
                st.markdown(
                    f"""
                    <div class="level-card" style="background:{item['color']}">
                        <div class="level-title">{item['emoji']} {item['level'].title()}</div>
                        <div class="level-desc">{item['desc']}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                # ✅ Start Button
                if st.button(f"Start {item['level'].title()}", key=f"START_{item['level']}", help="Begin this level"):
                    st.session_state.selected_level = item["level"]
                    st.rerun()

        st.stop()



    # --- LOAD QUIZ DATA AND RUN QUIZ ---
    # Load data ONCE per quiz start
    if st.session_state.current_quiz is None:
        filename = quiz_files[st.session_state.selected_subject][st.session_state.selected_level]
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as f:
                quiz = json.load(f)
            # Pick 20 random questions each time
            all_questions = quiz.get("questions", [])
            quiz["questions"] = random.sample(all_questions, min(20, len(all_questions)))
            st.session_state.current_quiz = quiz
        else:
            st.error("Quiz file missing! Please check the questions folder.")
            st.session_state.selected_subject = None
            st.session_state.selected_level = None
            st.stop()

    quiz = st.session_state.current_quiz

    # Show quiz or results here...
    # Add your question rendering and completion logic



    # 4. Run Quiz

    if not st.session_state.quiz_completed:

        # ✅ Beautiful progress bar
        progress = (st.session_state.current_question) / len(quiz["questions"])
        st.progress(progress)

        # ✅ Modern Card Style
        st.markdown("""
        <style>
        .question-card {
            background: rgba(255,255,255,0.15);
            padding: 25px;
            border-radius: 18px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.25);
            box-shadow: 0 4px 20px rgba(0,0,0,0.15);
            margin-bottom: 20px;
        }
        .option-item {
            padding: 12px 18px;
            border-radius: 12px;
            margin: 6px 0;
            transition: 0.15s;
            border: 1px solid rgba(255,255,255,0.2);
        }
        .option-item:hover {
            background: rgba(255,255,255,0.25);
        }
        </style>
        """, unsafe_allow_html=True)

        question_data = quiz["questions"][st.session_state.current_question]


        # ✅ Question Card
        
        st.markdown("""
<style>
/* Force monospaced code-like font globally for .code-font */
.code-font, .code-font * {
    font-family: 'Fira Code', 'Consolas', 'Courier New', monospace !important;
    font-size: 18px !important;
    white-space: pre-wrap !important;
}
</style>
""", unsafe_allow_html=True)

        st.markdown(f"""
        <div class="question-card">
            <h3>Question {st.session_state.current_question + 1} of {len(quiz["questions"])}</h3>
            <p class="code-font">{question_data['question']}</p>
        </div>
        """, unsafe_allow_html=True)

        # ✅ Modern Highlighted Buttons
        import html

        # Escape + wrap in span so HTML cannot break options
        safe_options = [
            f"{html.escape(opt)}"
            for opt in question_data["options"]
        ]
        safe_answer = f"<span>{html.escape(question_data['answer'])}</span>"

        selected_option = st.radio(
            "Select your answer:",
            safe_options,
            index=None,
            key=f"q_{st.session_state.current_question}",
            format_func=lambda x: x,   # Prevents Streamlit from stripping HTML
        )


        st.write("")

        # ✅ Submit Answer
        if st.button("Submit Answer", type="primary"):

            if selected_option is None:
                st.warning("Please select an option before submitting!")
                st.stop()

            if selected_option == safe_answer:
                st.success("✅ Correct answer!")
                st.session_state.score += question_data["points"]
            else:
                st.error(f"❌ Wrong! Correct answer: **{question_data['answer']}**")

            # Next question or finish
            if st.session_state.current_question < len(quiz["questions"]) - 1:
                st.session_state.current_question += 1
                st.rerun()
            else:
                st.session_state.quiz_completed = True
                # --- Save JSON ---
                uname = st.session_state.username
                if uname not in user_scores:
                    user_scores[uname] = {}

                user_scores[uname][str(quiz["id"])] = {
                    "score": st.session_state.score,
                    "completed_at": datetime.now().isoformat(),
                    "quiz_title": quiz["title"]
                }

                save_user_scores(user_scores)

                # --- Save CSV ---
                save_to_csv(
                    username = uname,
                    quiz_id = quiz["id"],
                    quiz_title = quiz["title"],
                    score = st.session_state.score,
                    completed_at = datetime.now().isoformat()
                )
                st.rerun()


    else:
        # ✅ QUIZ COMPLETED SECTION

        # ✅ Save to JSON FIRST
        current_dir = os.path.dirname(os.path.abspath(__file__))
        user_scores_path = os.path.join(current_dir, "user_scores.json")

        # Load old scores
        if os.path.exists(user_scores_path):
            with open(user_scores_path, "r", encoding="utf-8") as f:
                user_scores = json.load(f)
        else:
            user_scores = {}

        uname = st.session_state.username

        # Make sure username exists
        if uname not in user_scores:
            user_scores[uname] = {}

        # Save JSON
        user_scores[uname][str(quiz["id"])] = {
            "score": st.session_state.score,
            "completed_at": datetime.now().isoformat(),
            "quiz_title": quiz["title"]
        }

        with open(user_scores_path, "w", encoding="utf-8") as f:
            json.dump(user_scores, f, indent=4)

        # ✅ Save INTO CSV also
        save_to_csv(
            uname,
            quiz["id"],
            quiz["title"],
            st.session_state.score,
            datetime.now().isoformat()
        )

        # ✅ UI SECTION
        st.balloons()
        st.header("🎊 Quiz Completed!")
        total_points = sum(q["points"] for q in quiz["questions"])
        st.subheader(f"Your Score: {st.session_state.score}/{total_points}")
        
        percentage = (st.session_state.score / total_points) * 100
        st.progress(int(percentage))
        st.write(f"**{percentage:.1f}%**")

        if percentage >= 80:
            st.success("🎉 Excellent performance!")
        elif percentage >= 60:
            st.info("👍 Good job!")
        else:
            st.warning("💪 Keep practicing!")

        if st.button("Take Another Quiz"):
            st.session_state.selected_subject = None
            st.session_state.selected_level = None
            st.session_state.current_quiz = None
            st.session_state.current_question = 0
            st.session_state.score = 0
            st.session_state.quiz_completed = False
            st.rerun()

    st.sidebar.write("---")
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
        # ✅ Tell web.py to stop face & voice detection
    return True



if __name__ == "__main__":
    show_quiz_app()