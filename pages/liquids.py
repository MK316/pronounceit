import streamlit as st
import pandas as pd
import speech_recognition as sr
from streamlit_mic_recorder import mic_recorder
from io import BytesIO
import tempfile
import re

# -----------------------------
# Page setup
# -----------------------------
st.set_page_config(
    page_title="R-L Speaking Diagnosis",
    layout="centered"
)

st.title("🔊 R-L Speaking Diagnosis")
st.caption("Speak the given word. The app will recognize your speech and give a diagnosis.")

# -----------------------------
# Diagnostic word data
# -----------------------------
diagnostic_words = [
    {
        "ID": 1,
        "Target": "right",
        "Target_Sound": "R",
        "Contrast": "light"
    },
    {
        "ID": 2,
        "Target": "light",
        "Target_Sound": "L",
        "Contrast": "right"
    },
    {
        "ID": 3,
        "Target": "rice",
        "Target_Sound": "R",
        "Contrast": "lice"
    },
    {
        "ID": 4,
        "Target": "lock",
        "Target_Sound": "L",
        "Contrast": "rock"
    },
    {
        "ID": 5,
        "Target": "road",
        "Target_Sound": "R",
        "Contrast": "load"
    },
    {
        "ID": 6,
        "Target": "load",
        "Target_Sound": "L",
        "Contrast": "road"
    },
    {
        "ID": 7,
        "Target": "rip",
        "Target_Sound": "R",
        "Contrast": "lip"
    },
    {
        "ID": 8,
        "Target": "lip",
        "Target_Sound": "L",
        "Contrast": "rip"
    },
    {
        "ID": 9,
        "Target": "royal",
        "Target_Sound": "R",
        "Contrast": "loyal"
    },
    {
        "ID": 10,
        "Target": "loyal",
        "Target_Sound": "L",
        "Contrast": "royal"
    },
]

df = pd.DataFrame(diagnostic_words)

# -----------------------------
# Helper functions
# -----------------------------
def clean_text(text):
    text = str(text).lower().strip()
    text = re.sub(r"[^a-z\s]", "", text)
    return text

def get_first_word(text):
    text = clean_text(text)
    if not text:
        return ""
    return text.split()[0]

def recognize_speech_from_wav_bytes(audio_bytes):
    recognizer = sr.Recognizer()

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
        tmp_file.write(audio_bytes)
        tmp_path = tmp_file.name

    with sr.AudioFile(tmp_path) as source:
        audio_data = recognizer.record(source)

    try:
        recognized = recognizer.recognize_google(audio_data, language="en-US")
        return recognized, None
    except sr.UnknownValueError:
        return "", "The speech was not recognized clearly."
    except sr.RequestError:
        return "", "Speech recognition service is unavailable."

def diagnose_response(target, contrast, target_sound, recognized_text):
    target_clean = clean_text(target)
    contrast_clean = clean_text(contrast)
    recognized_first = get_first_word(recognized_text)

    if recognized_first == "":
        return {
            "Result": "Not recognized",
            "Correct": False,
            "Diagnosis": "The app could not recognize the word clearly."
        }

    if recognized_first == target_clean:
        return {
            "Result": "Correct",
            "Correct": True,
            "Diagnosis": f"The word was recognized as '{recognized_first}'."
        }

    if recognized_first == contrast_clean:
        return {
            "Result": "R-L confusion",
            "Correct": False,
            "Diagnosis": f"The target was '{target}', but it was recognized as '{contrast}'."
        }

    # Onset-based diagnosis
    if recognized_first.startswith("r") and target_sound == "L":
        return {
            "Result": "Possible L-to-R confusion",
            "Correct": False,
            "Diagnosis": f"The target begins with /l/, but the recognized word began with /r/: '{recognized_first}'."
        }

    if recognized_first.startswith("l") and target_sound == "R":
        return {
            "Result": "Possible R-to-L confusion",
            "Correct": False,
            "Diagnosis": f"The target begins with /r/, but the recognized word began with /l/: '{recognized_first}'."
        }

    return {
        "Result": "Different recognition",
        "Correct": False,
        "Diagnosis": f"The target was '{target}', but the app recognized '{recognized_first}'."
    }

def give_overall_feedback(score):
    if score >= 9:
        return (
            "Excellent",
            "Your /r/ and /l/ production is highly recognizable. You can move directly to advanced practice."
        )
    elif score >= 7:
        return (
            "Good",
            "Your /r/ and /l/ production is mostly recognizable, but a few words need focused practice."
        )
    elif score >= 5:
        return (
            "Developing",
            "Your /r/ and /l/ production is still developing. Practice the contrast slowly and clearly."
        )
    else:
        return (
            "Needs focused practice",
            "Your /r/ and /l/ production needs more focused practice. Start with listening and slow repetition."
        )

# -----------------------------
# Session state
# -----------------------------
if "current_index" not in st.session_state:
    st.session_state.current_index = 0

if "results" not in st.session_state:
    st.session_state.results = []

if "diagnosis_done" not in st.session_state:
    st.session_state.diagnosis_done = False

if "practice_unlocked" not in st.session_state:
    st.session_state.practice_unlocked = False

# -----------------------------
# Intro
# -----------------------------
st.markdown("## Step 1. Diagnostic Speaking Test")

st.markdown(
    """
    You will speak **10 words**.  
    The app will use speech recognition to check how each word is recognized.

    This is not a perfect pronunciation test.  
    It is a quick intelligibility-based diagnosis using automatic speech recognition.

    이 진단은 발음의 모든 음성학적 특징을 정확히 평가하는 시험이 아니라,  
    학습자의 발화가 자동음성인식에서 어떻게 인식되는지를 바탕으로 한 간단한 진단이다.
    """
)

# -----------------------------
# Reset button
# -----------------------------
if st.button("Reset Test"):
    st.session_state.current_index = 0
    st.session_state.results = []
    st.session_state.diagnosis_done = False
    st.session_state.practice_unlocked = False
    st.rerun()

# -----------------------------
# Diagnostic test
# -----------------------------
if not st.session_state.diagnosis_done:
    current_index = st.session_state.current_index

    if current_index < len(df):
        row = df.iloc[current_index]
        target = row["Target"]
        contrast = row["Contrast"]
        target_sound = row["Target_Sound"]

        st.markdown("---")
        st.markdown(f"### Word {current_index + 1} of {len(df)}")
        st.markdown(f"## Say this word: **{target}**")
        st.caption(f"Focus: initial /{target_sound.lower()}/ sound")

        audio = mic_recorder(
            start_prompt="🎙️ Start recording",
            stop_prompt="⏹️ Stop recording",
            just_once=True,
            use_container_width=True,
            key=f"recorder_{current_index}"
        )

        if audio:
            st.audio(audio["bytes"], format="audio/wav")

            if st.button("Analyze My Speech", key=f"analyze_{current_index}"):
                recognized_text, error = recognize_speech_from_wav_bytes(audio["bytes"])

                if error:
                    st.error(error)
                    recognized_text = ""

                diagnosis = diagnose_response(
                    target=target,
                    contrast=contrast,
                    target_sound=target_sound,
                    recognized_text=recognized_text
                )

                st.session_state.results.append(
                    {
                        "No": current_index + 1,
                        "Target": target,
                        "Target Sound": f"/{target_sound.lower()}/",
                        "Contrast": contrast,
                        "Recognized": recognized_text,
                        "Result": diagnosis["Result"],
                        "Correct": diagnosis["Correct"],
                        "Diagnosis": diagnosis["Diagnosis"]
                    }
                )

                st.session_state.current_index += 1

                if st.session_state.current_index >= len(df):
                    st.session_state.diagnosis_done = True

                st.rerun()

    else:
        st.session_state.diagnosis_done = True
        st.rerun()

# -----------------------------
# Result page
# -----------------------------
if st.session_state.diagnosis_done:
    st.markdown("---")
    st.markdown("## Step 2. Diagnosis Result")

    result_df = pd.DataFrame(st.session_state.results)

    if not result_df.empty:
        score = int(result_df["Correct"].sum())
        total = len(result_df)

        level, feedback = give_overall_feedback(score)

        st.markdown(f"### Score: **{score} / {total}**")
        st.markdown(f"### Level: **{level}**")
        st.info(feedback)

        st.markdown("### Detailed results")
        st.dataframe(result_df, use_container_width=True)

        st.markdown("### R-L confusion summary")

        rl_confusions = result_df[
            result_df["Result"].isin([
                "R-L confusion",
                "Possible L-to-R confusion",
                "Possible R-to-L confusion"
            ])
        ]

        if rl_confusions.empty:
            st.success("No clear R-L confusion was detected.")
        else:
            st.warning(f"{len(rl_confusions)} possible R-L confusion item(s) detected.")
            st.dataframe(
                rl_confusions[["No", "Target", "Recognized", "Result", "Diagnosis"]],
                use_container_width=True
            )

        if st.button("Move to Practice"):
            st.session_state.practice_unlocked = True
            st.rerun()

# -----------------------------
# Practice section
# -----------------------------
if st.session_state.practice_unlocked:
    st.markdown("---")
    st.markdown("## Step 3. Practice")

    st.success("Practice mode is now unlocked.")

    st.markdown(
        """
        In the practice stage, you can focus on the words that were not clearly recognized.

        연습 단계에서는 진단 결과에서 잘 인식되지 않은 단어를 중심으로 반복 연습할 수 있다.
        """
    )

    result_df = pd.DataFrame(st.session_state.results)

    if not result_df.empty:
        missed_df = result_df[result_df["Correct"] == False]

        if missed_df.empty:
            st.write("Great! All words were recognized correctly.")
        else:
            st.markdown("### Recommended practice words")
            st.dataframe(
                missed_df[["Target", "Target Sound", "Recognized", "Diagnosis"]],
                use_container_width=True
            )

            selected_word = st.selectbox(
                "Choose a word to practice",
                missed_df["Target"].tolist()
            )

            st.markdown(f"## Practice word: **{selected_word}**")
            st.write("Say the word slowly and clearly. Then repeat it several times.")
