import streamlit as st
import json
import os
import random
from datetime import datetime
import csv
import html
import subprocess

# Path to project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SUSPECT_FILE = os.path.join(PROJECT_ROOT, "suspect_count.json")

# ✅ Save User Scores
def save_user_scores(user_scores):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    user_scores_path = os.path.join(current_dir, "user_scores.json")
    with open(user_scores_path, "w", encoding="utf-8") as f:
        json.dump(user_scores, f, indent=4)


# ✅ Save to CSV
def save_to_csv(username, quiz_id, quiz_title, score, completed_at,sus_percentage):
    csv_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scores.csv")
    file_exists = os.path.isfile(csv_file)

    with open(csv_file, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        if not file_exists:
            writer.writerow(["username", "quiz_id", "quiz_title", "score", "completed_at","sus_percentage"])

        writer.writerow([username, quiz_id, quiz_title, score, completed_at, sus_percentage])


# ✅ Main Quiz App
def show_quiz_app():

    st.set_page_config(page_title="PrepSecure", page_icon="🎯", layout="wide")
    st.title("🎯 Quiz Master Pro")

    # ✅ Initialize States
    default_states = {
        "selected_subject": None,
        "selected_level": None,
        "current_quiz": None,
        "current_question": 0,
        "score": 0,
        "quiz_completed": False,
        "answers": {},
        "face_process": None,
        "voice_process": None
    }

    for key, val in default_states.items():
        if key not in st.session_state:
            st.session_state[key] = val

    # ✅ LOGIN CHECK
    if not st.session_state.get("logged_in", False):
        st.warning("Please log in first.")
        return

    # ✅ ALWAYS VISIBLE LOGOUT BUTTON
    with st.sidebar:
        st.success(f"✅ Logged in as: {st.session_state.username}")

        if st.button("🚪 Logout", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

    # -----------------------------------------
    # ✅ SUBJECT SELECTION
    # -----------------------------------------
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

                if st.button(f"Select {card['name']}", key=f"sub_{card['name']}"):
                    st.session_state.selected_subject = card["name"]
                    st.rerun()

        st.stop()

    # -----------------------------------------
    # ✅ LEVEL SELECTION
    # -----------------------------------------
    if st.session_state.selected_level is None:

        st.subheader(f"Choose {st.session_state.selected_subject} Level")

        # ✅ BACK BUTTON
        if st.button("⬅ Back to Subjects"):
            st.session_state.selected_subject = None
            st.rerun()

        LEVELS = [
            {"level": "basic", "color": "linear-gradient(135deg,#89f7fe 0%, #66a6ff 100%)", "desc": "Beginner friendly", "emoji": "🌱"},
            {"level": "intermediate", "color": "linear-gradient(135deg,#fbc2eb 0%, #a6c1ee 100%)", "desc": "Boost your skills", "emoji": "🚀"},
            {"level": "advanced", "color": "linear-gradient(135deg,#f6d365 0%, #fda085 100%)", "desc": "Challenge yourself", "emoji": "🔥"}
        ]

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
            }
            .level-card:hover {
                transform: translateY(-6px) scale(1.02);
                box-shadow: 0 12px 28px rgba(0,0,0,0.28);
            }
        </style>
        """, unsafe_allow_html=True)

        cols = st.columns(3)

        for i, item in enumerate(LEVELS):
            with cols[i]:
                st.markdown(
                    f"""
                    <div class="level-card" style="background:{item['color']}">
                        <div style="font-size:26px;font-weight:700;">{item['emoji']} {item['level'].title()}</div>
                        <div style="font-size:16px;opacity:0.9;">{item['desc']}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                if st.button(f"Start {item['level'].title()}", key=f"start_{item['level']}"):
                    # ✅ Now begin the quiz
                    st.session_state.selected_level = item["level"]
                    st.rerun()


        st.stop()

    # -----------------------------------------
    # ✅ LOAD JSON QUIZ FILE (WITH C++ MAPPING FIX)
    # -----------------------------------------

    current_dir = os.path.dirname(os.path.abspath(__file__))
    questions_dir = os.path.join(current_dir, "questions")

    # ✅ Correct mapping for file prefix
    file_map = {
        "C": "c",
        "C++": "cpp",
        "Python": "python"
    }

    subject_prefix = file_map.get(st.session_state.selected_subject)

    file_path = os.path.join(
        questions_dir,
        f"{subject_prefix}_{st.session_state.selected_level[0]}.json"
    )

    if st.session_state.current_quiz is None:
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                quiz = json.load(f)
            all_q = quiz.get("questions", [])
            quiz["questions"] = random.sample(all_q, min(20, len(all_q)))
            st.session_state.current_quiz = quiz
        else:
            st.error(f"❌ Quiz file not found: {file_path}")
            st.stop()

    quiz = st.session_state.current_quiz
    questions = quiz["questions"]

    # -----------------------------------------
    # ✅ QUIZ COMPLETED
    # -----------------------------------------
    if st.session_state.quiz_completed:
        # ✅ Load suspicion count
        sus_path = SUSPECT_FILE

        if os.path.exists(sus_path):
            sus_count = json.load(open(SUSPECT_FILE)).get("current", 0)
        else:
            sus_count = 0

        total_q = len(questions)
        sus_percentage = min(int((sus_count / total_q) * 100), 100)


        st.balloons()
        st.header("🎊 Quiz Completed!")

        total_points = sum(q["points"] for q in questions)
        st.subheader(f"Your Score: {st.session_state.score}/{total_points}")

        uname = st.session_state.username
        user_scores_path = os.path.join(current_dir, "user_scores.json")

        if os.path.exists(user_scores_path):
            with open(user_scores_path, "r", encoding="utf-8") as f:
                old_data = json.load(f)
        else:
            old_data = {}

        if uname not in old_data:
            old_data[uname] = {}

        subject_name = st.session_state.get("selected_subject", "Unknown")
        quiz_level = st.session_state.get("selected_level", "Unknown").title()

        old_data[uname][str(quiz["id"])] = {
            "quiz_title": quiz.get("title", "Untitled Quiz"),
            "subject": subject_name,
            "level": quiz_level,
            "score": st.session_state.score,
            "suspicion_percent": sus_percentage,
            "completed_at": datetime.now().isoformat()
        }

        save_user_scores(old_data)

        save_to_csv(
            uname,
            quiz.get("id", "N/A"),
            quiz.get("title", "Untitled Quiz"),
            st.session_state.score,
            datetime.now().isoformat(),
            sus_percentage
        )

        st.success("✅ Your score has been saved successfully!")

        if st.button("Take Another Quiz", key="retry_quiz"):
            for key in [
                "selected_subject", "selected_level",
                "current_quiz", "current_question",
                "score", "quiz_completed", "answers"
            ]:
                del st.session_state[key]
            st.rerun()

        return

    # -----------------------------------------
    # ✅ QUIZ RUNNING
    # -----------------------------------------

    idx = st.session_state.current_question
    if not st.session_state.get("quiz_started", False):
        st.session_state.quiz_started = True

    q = questions[idx]

    st.progress((idx + 1) / len(questions))

    st.markdown("""
    <style>
    .question-card {
        background: rgba(255,255,255,0.08);
        backdrop-filter: blur(12px);
        border-radius: 18px;
        border: 1px solid rgba(255,255,255,0.15);
        padding: 28px;
        margin-bottom: 20px;
        color: white;
    }
    .question-text {
        font-size: 22px;
        line-height: 1.6;
        color: white;
        font-family: 'Fira Code', 'Consolas', 'Courier New';
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="question-card">
        <h3 style="color:white;">Question {idx+1} of {len(questions)}</h3>
        <p class="question-text">{q["question"]}</p>
    </div>
    """, unsafe_allow_html=True)

    options = list(enumerate(q["options"]))

    prev_index = st.session_state.answers.get(idx, None)

    selected_tuple = st.radio(
        "Select your answer:",
        options,
        index=prev_index if prev_index is not None else None,
        format_func=lambda x: html.escape(x[1]),
        key=f"q_{idx}"
    )

    if selected_tuple is not None:
        selected_index = selected_tuple[0]
        st.session_state.answers[idx] = selected_index
    else:
        selected_index = None

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("⬅ Previous Question", disabled=(idx == 0)):
            st.session_state.current_question -= 1
            st.rerun()

    with col3:
        if idx < len(questions) - 1:
            if st.button("Next ➡"):
                st.session_state.current_question += 1
                st.rerun()
        else:
            if st.button("✅ Finish Quiz"):
                st.session_state.ask_submit = True
                st.rerun()

    if idx == len(questions) - 1:

        if st.session_state.get("ask_submit", False):

            st.warning("⚠️ Are you sure you want to submit the test? You cannot change answers later.")

            colA, colB = st.columns(2)

            with colA:
                if st.button("✅ Yes, Submit"):
                    
                    sus_path = SUSPECT_FILE

                    st.session_state.score = 0
                    for i, que in enumerate(questions):
                        user_index = st.session_state.answers.get(i)
                        correct_index = que["options"].index(que["answer"])
                        if user_index == correct_index:
                            st.session_state.score += que["points"]

                    st.session_state.quiz_completed = True
                    st.session_state.ask_submit = False
                    json.dump({"current": 0}, open(SUSPECT_FILE, "w"))
                    
                    
                    st.rerun()

            with colB:
                if st.button("❌ No, go back"):
                    st.session_state.ask_submit = False
                    
                    st.rerun()




# ✅ Run App
if __name__ == "__main__":
    show_quiz_app()
