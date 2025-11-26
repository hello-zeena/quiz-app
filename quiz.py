import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import datetime
import time

# ---------------- GOOGLE SHEETS SETUP -------------------

@st.cache_resource
def get_sheets():
    SCOPE = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    CREDS = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)

    client = gspread.authorize(CREDS)
    

    quiz_sheet = client.open("Zinath Quiz").worksheet("Quiz_Responses")
    anon_sheet = client.open("Zinath Quiz").worksheet("Anonymous_Messages")
    return quiz_sheet, anon_sheet

quiz_sheet, anon_sheet = get_sheets()

# ------------- FIX HEADERS SO DATA STARTS AT COLUMN A -------------

headers = [
    "Timestamp",
    "Participant Name",
    "Q1",
    "Q2",
    "Q3",
    "Q4",
    "Q5",
    "Q6",
    "Q7",
    "Q8",
    "Q9",
    "Q10",
    "Q11",
    "Score",
    "Full Name",
    "Birthday",
    "Shoe Size",
    "Worst Subject",
    "One Word I Say A Lot",
    "A Lie I Told",
    "What You Like About Me",
    "What You Hate About Me",
    "Describe Me In 3 Words"
]

first_row = quiz_sheet.row_values(1)
if not first_row:   # If row 1 is empty
    quiz_sheet.insert_row(headers, index=1)

# ---------------- SESSION STATE -------------------

if "page" not in st.session_state:
    st.session_state.page = "start"
if "name" not in st.session_state:
    st.session_state.name = ""
if "current_question" not in st.session_state:
    st.session_state.current_question = 0
if "answers" not in st.session_state:
    st.session_state.answers = []
if "score" not in st.session_state:
    st.session_state.score = 0

# ---------------- QUESTIONS -------------------

questions = [
    {"question": "What’s my favorite food?", "options": ["Jollof Rice", "Pasta", "Yam", "Amala"], "answer": "Amala"},
    {"question": "When did I start learning Data Analytics?", "options": ["2022", "2023", "2024", "Not yet"], "answer": "2024"},
    {"question": "Who is my gist partner?", "options": ["Ola", "Jolaade", "Maryam", "Aisha"], "answer": "Jolaade"},
    {"question": "How many Data Analytics tool can I work with?", "options": ["6", "5", "4", "3"], "answer": "6"},
    {"question": "Do I like to stay in or go out?", "options": ["Stay in", "Go out"], "answer": "Stay in"},
    {"question": "Do I prefer texting or calling?", "options": ["texting", "calling"], "answer": "texting"},
    {"question": "Do I like sneakers or sandals?", "options": ["sneakers", "sandals", "Both"], "answer": "Both"},
    {"question": "Am I someone who puts on a wristwatch?", "options": ["Yes", "No"], "answer": "No"},
    {"question": "What color is my water bottle?", "options": ["Green", "Blue", "Black"], "answer": "Black"},
    {"question": "Have I ever broken a bone or been in a hospital?", "options": ["Yes", "No"], "answer": "Yes"},
    {"question": "Have I ever fallen asleep in public?", "options": ["Yes", "No"], "answer": "Yes"},
]

# ------------------- START PAGE -------------------

if st.session_state.page == "start":
    st.title("🎉 Who Knows Me Better 🎉")

    name = st.text_input("Enter your name to start:", key="start_name", placeholder="Enter your name here")

    if st.button("Start Quiz"):
        if not name.strip():
            st.warning("⚠️ Please enter your name to continue.")
        else:
            st.session_state.name = name.strip()
            st.session_state.page = "quiz"
            st.session_state.score = 0
            st.session_state.answers = []
            st.session_state.current_question = 0
            st.rerun()

# ------------------- QUIZ PAGE -------------------

elif st.session_state.page == "quiz":
    st.title(f"🎉 Welcome, {st.session_state.name}! Let’s begin 🎉")

    current = st.session_state.current_question
    q = questions[current]

    key = f"q_{current}"
    if key not in st.session_state:
        st.session_state[key] = None

    st.subheader(q["question"])
    answer = st.radio("Choose one:", q["options"], key=key, index=None)

    if st.button("Next"):
        if answer is None:
            st.warning("⚠️ Please select an answer before continuing!")
        else:
            st.session_state.answers.append(answer)
            if answer == q["answer"]:
                st.session_state.score += 1

            if current + 1 < len(questions):
                st.session_state.current_question += 1
            else:
                st.session_state.page = "score"
            st.rerun()

# ------------------- SCORE PAGE -------------------

elif st.session_state.page == "score":
    st.title("🎉 Score 🎉")
    st.subheader(f"{st.session_state.name}, you scored {st.session_state.score}/11!")
    st.info("Now answer these personal ‘Would You Know?’ questions 💗")

    if st.button("Continue"):
        st.session_state.page = "text_inputs"
        st.rerun()

# ------------------- TEXT INPUT PAGE -------------------

elif st.session_state.page == "text_inputs":
    st.header("🧠 WOULD YOU KNOW?")

    st.session_state.q12 = st.text_input("What’s my full name?")
    st.session_state.q13 = st.text_input("When is my birthday?")
    st.session_state.q14 = st.text_input("What’s my shoe size?")
    st.session_state.q15 = st.text_input("What’s my worst subject in school?")
    st.session_state.q16 = st.text_input("What’s one word I say a lot?")
    st.session_state.q17 = st.text_input("What’s a lie I’ve told that you know about?")

    st.subheader("💭 YOUR HONEST THOUGHT ABOUT ME")
    st.session_state.like = st.text_area("❤️ What you like about me")
    st.session_state.dislike = st.text_area("💔 What you hate about me")
    st.session_state.describe = st.text_input("📝 Describe me in three words")

    if st.button("Submit Quiz"):
        required = [
            st.session_state.q12, st.session_state.q13, st.session_state.q14,
            st.session_state.q15, st.session_state.q16, st.session_state.q17,
            st.session_state.like, st.session_state.dislike, st.session_state.describe
        ]
        if any(not str(field).strip() for field in required):
            st.warning("⚠️ Please answer all questions before continuing.")
        else:
            st.session_state.page = "thanks"
            st.rerun()

# ------------------- THANK YOU PAGE -------------------

elif st.session_state.page == "thanks":
    st.title("💌 Send Zinath an Anonymous Message")
    message = st.text_area("Drop a heartfelt or fun message anonymously ✨", key="anon_message")

    if st.button("Send Anonymous Message"):

        # ------------- THIS FIXES THE COLUMN SHIFT -------------
        quiz_sheet.append_row(
    [
        datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        st.session_state.name,
        *st.session_state.answers, 
        st.session_state.score,  # Q1–Q11
        st.session_state.q12,
        st.session_state.q13,
        st.session_state.q14,
        st.session_state.q15,
        st.session_state.q16,
        st.session_state.q17,
        st.session_state.like,
        st.session_state.dislike,
        st.session_state.describe,
    ],
    table_range="A1"
)

        anon_sheet.append_row([
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), message
        ])

        st.success("Thank you for your sweet anonymous message 💖")
        time.sleep(2)
        st.session_state.page = "done"
        st.rerun()

# ------------------- FINAL PAGE -------------------

elif st.session_state.page == "done":
    st.title("🎉 Thanks for participating! 💖")
    st.balloons()
