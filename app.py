import streamlit as st
from PyPDF2 import PdfReader
import openai

st.title("📄 Document Safety Analyst Tool")

if "api_valid" not in st.session_state:
    st.session_state.api_valid = False
if "api_key" not in st.session_state:
    st.session_state.api_key = ""

# API key input
if not st.session_state.api_valid:
    api_key = st.text_input("🔑 Paste your OpenAI API key:", type="password")
    if api_key:
        try:
            client = openai.OpenAI(api_key=api_key)
            _ = client.models.list()
            st.session_state.api_key = api_key
            st.session_state.api_valid = True
            st.success("✅ API key validated successfully.")
        except Exception as e:
            st.error(f"❌ Invalid API key: {e}")
else:
    client = openai.OpenAI(api_key=st.session_state.api_key)

uploaded_file = st.file_uploader("Upload your PDF", type="pdf")

def chunk_text(text, chunk_size=3000):
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

if uploaded_file and st.session_state.api_valid:
    reader = PdfReader(uploaded_file)
    text = ""
    for page_num, page in enumerate(reader.pages, start=1):
        page_text = page.extract_text()
        if page_text:
            text += f"\n--- Page {page_num} ---\n{page_text}\n"
        else:
            text += f"\n--- Page {page_num} ---\n[No text extracted]\n"

    confirm = st.button("🚨 CONFIRM", key="confirm")

    if confirm:
        question_pdf = "1. Assess the weather and NOTAM and provide an overall TEM assessment of the flight"
        questions_general = [
            "2. Highlight any other associated threats and suitable mitigations for the airspace and countries associated with the flight",
            "3. Review British foreign office for travel to each of the countries",
            "4. Are all required regulatory references present? If any are missing, highlight them.",
            "5. Identify any geopolitical or regulatory factors that could influence operational decision-making",
            "6. List the 3 closest Marriott group hotels to destination airport",
            "7. Are crew rest, accommodation, or duty arrangements mentioned, and are they appropriate?",
            "8. Are contingency or emergency procedures documented? Summarise them.",
            "9. Are risk mitigations clearly defined?",
            "10. Are responsibilities and accountabilities clearly allocated?"
        ]

        # Chunk the PDF text
        chunks = chunk_text(text, chunk_size=3000)

        # Collect partial responses for Q1
        partial_answers_q1 = []
        with st.spinner("💬 Analysing Question 1 using the PDF..."):
            for chunk in chunks:
                prompt_q1 = f"{question_pdf}\n\nDocument text:\n{chunk}"
                try:
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": prompt_q1}]
                    )
                    partial_answers_q1.append(response.choices[0].message.content.strip())
                except Exception as e:
                    partial_answers_q1.append(f"❌ Error: {e}")

        # Collate all Q1 answers into one final summary
        prompt_collate = (
            "Summarise the following into a single, coherent answer to the question: "
            "'Assess the weather and NOTAM and provide an overall TEM assessment of the flight.'\n\n"
            + "\n\n".join(partial_answers_q1)
        )
        try:
            final_response_q1 = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt_collate}]
            )
            output_q1 = final_response_q1.choices[0].message.content.strip()
        except Exception as e:
            output_q1 = f"❌ Error while collating Q1: {e}"

        # Handle Q2–Q10 with general AI-based knowledge
        prompt_general = (
            "Using general aviation, regulatory, and operational knowledge, and optionally referencing the context below, "
            "please provide clear and concise answers to the following questions:\n\n"
            + "\n".join(questions_general) +
            f"\n\n[Context for reference – do not rely on it]:\n{text[:4000]}"
        )
        try:
            response_general = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt_general}]
            )
            output_general = response_general.choices[0].message.content.strip()
        except Exception as e:
            output_general = f"❌ Error while processing Questions 2–10: {e}"

        # Present final 10 answers
        st.success("✅ Analysis complete!")
        st.markdown("### ✈️ Final Answers:")
        st.markdown("**1.** " + output_q1)
        st.markdown("---")
        st.markdown(output_general)