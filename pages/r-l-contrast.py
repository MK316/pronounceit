import streamlit as st
import pandas as pd
import re
from streamlit_mic_recorder import speech_to_text

# -----------------------------
# Page setup
# -----------------------------
st.set_page_config(
    page_title="R-L Speaking Diagnosis",
    layout="centered"
)

st.title("🔊 R-L Speaking Diagnosis")
st.caption("Speak the given word. The app will diagnose your /r/ and /l/ production.")

# -----------------------------
# Diagnostic word data
# -----------------------------
diagnostic_words = [
    {"ID": 1, "Target": "right", "Target_Sound": "R", "Contrast": "light"},
    {"ID": 2, "Target": "light", "Target_Sound": "L", "Contrast": "right"},
    {"ID": 3, "Target": "rice", "Target_Sound": "R", "Contrast": "lice"},
    {"ID": 4, "Target": "lock", "Target_Sound": "L", "Contrast": "rock"},
    {"ID": 5, "Target": "road", "Target_Sound": "R", "Contrast": "load"},
    {"ID": 6, "Target": "load", "Target_Sound": "L", "Contrast": "road"},
    {"ID": 7, "Target": "rip", "Target_Sound": "R", "Contrast": "lip"},
    {"ID": 8, "Target": "lip", "Target_Sound": "L", "Contrast": "rip"},
    {"ID": 9, "Target": "royal", "Target_Sound": "R", "Contrast": "loyal"},
    {"ID": 10, "Target": "loyal", "Target_Sound": "L", "Contrast": "royal"},
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


def give_overall_feedback(score, total):
    percentage = score / total

    if percentage >= 0.9:
        return (
            "Excellent",
            "Your /r/ and /l/ production was highly recognizable."
        )
    elif percentage >= 0.7:
        return (
            "Good",
            "Your /r/ and /l/ production was mostly recognizable, but a few words need focused practice."
        )
    elif percentage >= 0.5:
        return (
            "Developing",
            "Your /r/ and /l/ production is still developing. Practice the contrast slowly and clearly."
        )
    else:
        return (
            "Needs focused practice",
            "Your /r/ and /l/ production needs more focused practice. Start with slow repetition."
        )


# -----------------------------
# Session state
# -----------------------------
if "test_started" not in st.session_state:
    st.session_state.test_started = False

if "current_index" not in st.session_state:
    st.session_state.current_index = 0

if "results" not in st.session_state:
    st.session_state.results = []

if "diagnosis_done" not in st.session_state:
    st.session_state.diagnosis_done = False

if "practice_unlocked" not in st.session_state:
    st.session_state.practice_unlocked = False

if "recorder_version" not in st.session_state:
    st.session_state.recorder_version = 0


# -----------------------------
# Intro
# -----------------------------
st.markdown("## Step 1. Diagnostic Speaking Test")

st.markdown(
    """
    You will speak **10 words**.  
    The app will analyze how your speech is recognized.

    During the test, the recording and recognition result will not be displayed.  
    When your speech is recognized, the next word will appear automatically.

    이 단계에서는 녹음 파일과 인식 결과를 바로 보여주지 않는다.  
    단어가 인식되면 다음 단어로 자동 이동하고, 10개 단어가 끝난 뒤 전체 진단 결과를 제시한다.
    """
)

# -----------------------------
# Start / Reset buttons
# -----------------------------
col1, col2 = st.columns(2)

with col1:
    if st.button("Start Test"):
        st.session_state.test_started = True
        st.session_state.current_index = 0
        st.session_state.results = []
        st.session_state.diagnosis_done = False
        st.session_state.practice_unlocked = False
        st.session_state.recorder_version = 0
        st.rerun()

with col2:
    if st.button("Reset Test"):
        st.session_state.test_started = False
        st.session_state.current_index = 0
        st.session_state.results = []
        st.session_state.diagnosis_done = False
        st.session_state.practice_unlocked = False
        st.session_state.recorder_version += 1
        st.rerun()


# -----------------------------
# Diagnostic test
# -----------------------------
if st.session_state.test_started and not st.session_state.diagnosis_done:

    current_index = st.session_state.current_index

    if current_index < len(df):
        row = df.iloc[current_index]

        target = row["Target"]
        contrast = row["Contrast"]
        target_sound = row["Target_Sound"]

        st.markdown("---")
        st.markdown(f"### Word {current_index + 1} of {len(df)}")
        st.markdown(f"## Say this word: **{target}**")
        st.caption("Click Start, say the word, and click Stop. The next word will appear automatically when recognized.")

        recognized_text = speech_to_text(
            language="en",
            start_prompt="🎙️ Start recording",
            stop_prompt="⏹️ Stop recording",
            just_once=True,
            use_container_width=True,
            key=f"speech_{current_index}_{st.session_state.recorder_version}"
        )

        if recognized_text:
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
            st.session_state.recorder_version += 1

            if st.session_state.current_index >= len(df):
                st.session_state.diagnosis_done = True

            st.rerun()

    else:
        st.session_state.diagnosis_done = True
        st.rerun()

elif not st.session_state.test_started and not st.session_state.diagnosis_done:
    st.info("Click **Start Test** to begin.")


# -----------------------------
# Diagnosis result
# -----------------------------
if st.session_state.diagnosis_done:
    st.markdown("---")
    st.markdown("## Step 2. Diagnosis Result")

    result_df = pd.DataFrame(st.session_state.results)

    if not result_df.empty:
        score = int(result_df["Correct"].sum())
        total = len(result_df)

        level, feedback = give_overall_feedback(score, total)

        st.markdown(f"### Score: **{score} / {total}**")
        st.markdown(f"### Level: **{level}**")
        st.info(feedback)

        st.markdown("### Detailed Recognition Results")
        st.dataframe(result_df, use_container_width=True)

        st.markdown("### R-L Confusion Summary")

        confusion_df = result_df[
            result_df["Result"].isin(
                [
                    "R-L confusion",
                    "Possible L-to-R confusion",
                    "Possible R-to-L confusion"
                ]
            )
        ]

        if confusion_df.empty:
            st.success("No clear R-L confusion was detected.")
        else:
            st.warning(f"{len(confusion_df)} possible R-L confusion item(s) detected.")
            st.dataframe(
                confusion_df[
                    ["No", "Target", "Target Sound", "Recognized", "Result", "Diagnosis"]
                ],
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

    result_df = pd.DataFrame(st.session_state.results)
    missed_df = result_df[result_df["Correct"] == False]

    if missed_df.empty:
        st.success("Great! All words were recognized correctly.")
    else:
        st.markdown("### Recommended Practice Words")
        st.dataframe(
            missed_df[["Target", "Target Sound", "Recognized", "Diagnosis"]],
            use_container_width=True
        )

        selected_word = st.selectbox(
            "Choose a word to practice",
            missed_df["Target"].tolist()
        )

        st.markdown(f"## Practice word: **{selected_word}**")
        st.write("Say the word slowly and clearly. Repeat it several times.")


# -----------------------------
# Teacher note
# -----------------------------
st.markdown("---")
st.markdown("## Teacher Note")

st.markdown(
    """
    This app uses automatic speech recognition as a quick diagnosis tool.  
    It does not measure pronunciation acoustically.

    자동음성인식 결과는 학습자의 발화가 기계에 어떻게 인식되는지를 보여주는 참고 자료이다.  
    따라서 이 결과는 최종 평가 점수라기보다 연습 방향을 정하는 진단 자료로 사용하는 것이 적절하다.
    """
)
