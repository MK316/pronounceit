import streamlit as st
import pandas as pd
from gtts import gTTS
from io import BytesIO
import random

# -----------------------------
# Page setup
# -----------------------------
st.set_page_config(
    page_title="R-L Minimal Pair Practice",
    layout="centered"
)

st.title("🔊 R-L Minimal Pair Practice")
st.caption("Practice English words that begin with /r/ and /l/.")

# -----------------------------
# Minimal pair data
# -----------------------------
data = [
    {"ID": 1, "R_word": "right", "L_word": "light", "R_IPA": "/raɪt/", "L_IPA": "/laɪt/", "Meaning_R": "오른쪽, 맞는", "Meaning_L": "빛, 가벼운"},
    {"ID": 2, "R_word": "rice", "L_word": "lice", "R_IPA": "/raɪs/", "L_IPA": "/laɪs/", "Meaning_R": "쌀, 밥", "Meaning_L": "이, 머릿니"},
    {"ID": 3, "R_word": "rock", "L_word": "lock", "R_IPA": "/rɑːk/", "L_IPA": "/lɑːk/", "Meaning_R": "바위", "Meaning_L": "자물쇠, 잠그다"},
    {"ID": 4, "R_word": "road", "L_word": "load", "R_IPA": "/roʊd/", "L_IPA": "/loʊd/", "Meaning_R": "길, 도로", "Meaning_L": "짐, 싣다"},
    {"ID": 5, "R_word": "read", "L_word": "lead", "R_IPA": "/riːd/", "L_IPA": "/liːd/", "Meaning_R": "읽다", "Meaning_L": "이끌다"},
    {"ID": 6, "R_word": "red", "L_word": "led", "R_IPA": "/red/", "L_IPA": "/led/", "Meaning_R": "빨간", "Meaning_L": "이끌었다"},
    {"ID": 7, "R_word": "race", "L_word": "lace", "R_IPA": "/reɪs/", "L_IPA": "/leɪs/", "Meaning_R": "경주", "Meaning_L": "끈, 레이스"},
    {"ID": 8, "R_word": "rent", "L_word": "lent", "R_IPA": "/rent/", "L_IPA": "/lent/", "Meaning_R": "빌리다, 임대료", "Meaning_L": "빌려주었다"},
    {"ID": 9, "R_word": "royal", "L_word": "loyal", "R_IPA": "/ˈrɔɪəl/", "L_IPA": "/ˈlɔɪəl/", "Meaning_R": "왕실의", "Meaning_L": "충성스러운"},
    {"ID": 10, "R_word": "row", "L_word": "low", "R_IPA": "/roʊ/", "L_IPA": "/loʊ/", "Meaning_R": "줄, 노 젓다", "Meaning_L": "낮은"},
    {"ID": 11, "R_word": "rip", "L_word": "lip", "R_IPA": "/rɪp/", "L_IPA": "/lɪp/", "Meaning_R": "찢다", "Meaning_L": "입술"},
    {"ID": 12, "R_word": "rate", "L_word": "late", "R_IPA": "/reɪt/", "L_IPA": "/leɪt/", "Meaning_R": "비율, 평가하다", "Meaning_L": "늦은"},
]

df = pd.DataFrame(data)

# -----------------------------
# Helper function: make TTS audio
# -----------------------------
@st.cache_data
def make_tts_audio(text, lang="en"):
    tts = gTTS(text=text, lang=lang)
    audio_fp = BytesIO()
    tts.write_to_fp(audio_fp)
    audio_fp.seek(0)
    return audio_fp.read()

# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.header("Menu")
mode = st.sidebar.radio(
    "Choose mode",
    ["Practice Mode", "Listening Test Mode", "Data View"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### Pronunciation Focus")
st.sidebar.markdown(
    """
    - **/r/**: 혀끝이 입천장에 닿지 않음  
    - **/l/**: 혀끝이 윗잇몸 근처에 닿음  
    - Korean learners often find this contrast difficult because Korean ㄹ does not map exactly onto English /r/ or /l/.
    """
)

# -----------------------------
# Initialize session state
# -----------------------------
if "score" not in st.session_state:
    st.session_state.score = 0

if "total" not in st.session_state:
    st.session_state.total = 0

if "current_question" not in st.session_state:
    st.session_state.current_question = None

# -----------------------------
# Practice Mode
# -----------------------------
if mode == "Practice Mode":
    st.subheader("Practice Mode")
    st.write("Choose a minimal pair and listen to the difference.")

    pair_options = [
        f"{row.R_word} / {row.L_word}"
        for _, row in df.iterrows()
    ]

    selected_pair = st.selectbox("Choose a word pair", pair_options)

    selected_index = pair_options.index(selected_pair)
    row = df.iloc[selected_index]

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### /r/ word")
        st.markdown(f"## {row['R_word']}")
        st.write(f"IPA: {row['R_IPA']}")
        st.write(f"Meaning: {row['Meaning_R']}")

        r_text = f"{row['R_word']}. Listen carefully. {row['R_word']}."
        r_audio = make_tts_audio(r_text, lang="en")
        st.audio(r_audio, format="audio/mp3")

    with col2:
        st.markdown("### /l/ word")
        st.markdown(f"## {row['L_word']}")
        st.write(f"IPA: {row['L_IPA']}")
        st.write(f"Meaning: {row['Meaning_L']}")

        l_text = f"{row['L_word']}. Listen carefully. {row['L_word']}."
        l_audio = make_tts_audio(l_text, lang="en")
        st.audio(l_audio, format="audio/mp3")

    st.markdown("---")
    st.markdown("### Practice sentence")

    word_type = st.radio(
        "Choose word type for sentence practice",
        ["/r/ word", "/l/ word"],
        horizontal=True
    )

    if word_type == "/r/ word":
        target_word = row["R_word"]
    else:
        target_word = row["L_word"]

    sentence = f"Please say the word {target_word}. The word is {target_word}."

    st.write(sentence)
    sentence_audio = make_tts_audio(sentence, lang="en")
    st.audio(sentence_audio, format="audio/mp3")

# -----------------------------
# Listening Test Mode
# -----------------------------
elif mode == "Listening Test Mode":
    st.subheader("Listening Test Mode")
    st.write("Listen to the audio and choose the word you heard.")

    col_a, col_b = st.columns(2)

    with col_a:
        if st.button("New Question"):
            row = df.sample(1).iloc[0]
            target_type = random.choice(["R_word", "L_word"])

            if target_type == "R_word":
                target_word = row["R_word"]
                other_word = row["L_word"]
            else:
                target_word = row["L_word"]
                other_word = row["R_word"]

            st.session_state.current_question = {
                "ID": int(row["ID"]),
                "target_word": target_word,
                "other_word": other_word,
                "R_word": row["R_word"],
                "L_word": row["L_word"],
                "answer": target_word
            }

    with col_b:
        if st.button("Reset Score"):
            st.session_state.score = 0
            st.session_state.total = 0
            st.session_state.current_question = None
            st.success("Score has been reset.")

    question = st.session_state.current_question

    if question is None:
        st.info("Click 'New Question' to start.")
    else:
        target_word = question["target_word"]

        test_text = f"Listen carefully. {target_word}. {target_word}."
        test_audio = make_tts_audio(test_text, lang="en")

        st.markdown("### Listen")
        st.audio(test_audio, format="audio/mp3")

        choices = [question["R_word"], question["L_word"]]
        random.shuffle(choices)

        user_choice = st.radio(
            "Which word did you hear?",
            choices,
            key=f"choice_{question['ID']}_{question['target_word']}"
        )

        if st.button("Check Answer"):
            st.session_state.total += 1

            if user_choice == question["answer"]:
                st.session_state.score += 1
                st.success(f"Correct! The answer is **{question['answer']}**.")
            else:
                st.error(f"Try again. The answer was **{question['answer']}**.")

            st.write(
                f"Current score: **{st.session_state.score} / {st.session_state.total}**"
            )

        st.markdown("---")
        st.markdown("### Word pair")
        st.write(f"/r/ word: **{question['R_word']}**")
        st.write(f"/l/ word: **{question['L_word']}**")

# -----------------------------
# Data View
# -----------------------------
elif mode == "Data View":
    st.subheader("Data View")
    st.write("This is the minimal pair dataset used in the app.")
    st.dataframe(df, use_container_width=True)

    st.markdown("### Column explanation")
    st.write(
        """
        - `R_word`: word beginning with /r/
        - `L_word`: word beginning with /l/
        - `R_IPA`: IPA transcription of the /r/ word
        - `L_IPA`: IPA transcription of the /l/ word
        - `Meaning_R`: Korean meaning of the /r/ word
        - `Meaning_L`: Korean meaning of the /l/ word
        """
    )
