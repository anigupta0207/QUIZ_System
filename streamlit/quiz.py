import streamlit as st
import json
import os
import random
from datetime import datetime

# ---------- Utility Functions ----------

def load_quiz_data():
    """Load quiz data from JSON files."""

    # Get the absolute path to the questions directory
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
    
    quizzes = []
    user_scores = {}
    
    # Load quiz data files
    for level, filename in quiz_files.items():
        try:
            if os.path.exists(filename):
                with open(filename, "r", encoding="utf-8") as f:
                    quiz_data = json.load(f)

                    # ✅ Pick only 20 random questions each time from the full set
                    all_questions = quiz_data.get("questions", [])
                    random_20 = random.sample(all_questions, min(20, len(all_questions)))
                    quiz_data["questions"] = random_20

                    quizzes.append(quiz_data)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            st.error(f"Error loading {filename}: {e}")
    
    # Load user scores
    user_scores_path = os.path.join(current_dir, "user_scores.json")
    if os.path.exists(user_scores_path):
        try:
            with open(user_scores_path, "r", encoding="utf-8") as f:
                user_scores = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            user_scores = {}
    
    return {
        "quizzes": quizzes,
        "user_scores": user_scores
    }

def save_user_scores(user_scores):
    """Save user scores to JSON file."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    user_scores_path = os.path.join(current_dir, "user_scores.json")
    with open(user_scores_path, "w", encoding="utf-8") as f:
        json.dump(user_scores, f, indent=4)

def show_quiz_app():
    # Main quiz application function.
    st.set_page_config(page_title="Quiz App", page_icon="🎯", layout="wide")
    st.title("🎯 Quiz Master Pro")

    # Session state initializers for navigation/quiz selection
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

    # Mapping for quiz files (by subject + level)
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

    # Check if user is logged in
    if not st.session_state.get("logged_in", False):
        st.warning("Please log in first to access the quiz application.")
        return

    st.sidebar.success(f"✅ Logged in as: {st.session_state.username}")

    # 1. Select Subject
    # ... previous code ...

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


    # 2. Select Level
    if st.session_state.selected_level is None:
        st.subheader(f"Choose {st.session_state.selected_subject} Quiz Level")
        levels = ["basic", "intermediate", "advanced"]
        st.session_state.selected_level = st.radio("Select Level:", levels)
        st.stop()

    # 3. Load quiz data according to selection (only once)
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

    # 4. Run Quiz
    if not st.session_state.quiz_completed:
        question_data = quiz["questions"][st.session_state.current_question]
        st.subheader(f"Question {st.session_state.current_question + 1} of {len(quiz['questions'])}")
        st.write(f"**{question_data['question']}**")
        selected_option = st.radio(
            "Choose your answer:",
            question_data["options"],
            index=None,
            key=f"question_{st.session_state.current_question}"
        )
        if st.button("Submit Answer", type="primary"):
            if selected_option == question_data['answer']:
                st.session_state.score += question_data['points']
                st.success("Correct! 🎉")
            else:
                st.error(f"Wrong! The correct answer is: {question_data['answer']}")
            if st.session_state.current_question < len(quiz["questions"]) - 1:
                st.session_state.current_question += 1
                st.rerun()
            else:
                st.session_state.quiz_completed = True
                # Save score
                user_scores_path = os.path.join(current_dir, "user_scores.json")
                if os.path.exists(user_scores_path):
                    with open(user_scores_path, "r", encoding="utf-8") as f:
                        user_scores = json.load(f)
                else:
                    user_scores = {}
                uname = st.session_state.username
                if uname not in user_scores:
                    user_scores[uname] = {}
                user_scores[uname][str(quiz["id"])] = {
                    "score": st.session_state.score,
                    "completed_at": datetime.now().isoformat(),
                    "quiz_title": quiz["title"]
                }
                save_user_scores(user_scores)
                st.rerun()

    else:
        # Quiz completed
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
            # Reset selection states and quiz session states
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


if __name__ == "__main__":
    show_quiz_app()