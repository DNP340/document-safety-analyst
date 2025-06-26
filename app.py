import streamlit as st
from PyPDF2 import PdfReader
import openai

st.title("📄 Document Safety Analyst Tool")

# API key input
api_key = st.text_input("🔑 Paste your OpenAI API key:", type="password")

uploaded_file = st.file_uploader("Upload your PDF", type="pdf")

if uploaded_file:
    reader = PdfReader(uploaded_file)
    text = ""
    for page_num, page in enumerate(reader.pages, start=1):
        page_text = page.extract_text()
        if page_text:
            text += f"\n--- Page {page_num} ---\n{page_text}\n"
        else:
            text += f"\n--- Page {page_num} ---\n[No text extracted]\n"

    st.text_area("📑 Extracted Document Text", text, height=300)

    confirm = st.button("🚨 CONFIRM", key="confirm")

    if confirm:
        if not api_key:
            st.error("⚠️ Please paste your OpenAI API key before confirming.")
        else:
            client = openai.OpenAI(api_key=api_key)
            questions = [
                "Assess the weather and NOTAM and provide an overall TEM assessment of the flight",
                "Highlight any other associated threats and suitable mitigations for the airspace and countries associated with the flight",
                "Review British foreign office for travel to each of the countries",
                "Are all required regulatory references present? If any are missing, highlight them.",
                "Are NOTAMs, weather information, or airport data outdated or missing?",
                "List the 3 closest Marriott group hotels to destination airport",
                "Are crew rest, accommodation, or duty arrangements mentioned, and are they appropriate?",
                "Are contingency or emergency procedures documented? Summarise them.",
                "Are risk mitigations clearly defined?",
                "Are responsibilities and accountabilities clearly allocated?"
            ]
            prompt = "Apply these questions to the provided document text:\n"
            for idx, q in enumerate(questions, 1):
                prompt += f"{idx}. {q}\n"
            prompt += f"\nDocument text:\n{text}"

            with st.spinner("💬 Querying ChatGPT..."):
                try:
                    response = client.chat.completions.create(
                        model="gpt-4",
                        messages=[{"role": "user", "content": prompt}]
                    )
                    st.success("✅ Analysis complete!")
                    st.markdown(response.choices[0].message.content)
                except Exception as e:
                    st.error(f"❌ Error: {e}")