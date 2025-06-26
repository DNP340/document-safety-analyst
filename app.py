import streamlit as st
from PyPDF2 import PdfReader
import openai

st.title("📄 Document Safety Analyst Tool")

# API key input
api_key = st.text_input("🔑 Paste your OpenAI API key:", type="password")

uploaded_file = st.file_uploader("Upload your PDF", type="pdf")

def chunk_text(text, chunk_size=3000):
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

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
            prompt_template = "Apply these questions to the provided document text:\n"
            for idx, q in enumerate(questions, 1):
                prompt_template += f"{idx}. {q}\n"

            chunks = chunk_text(text, chunk_size=3000)
            combined_output = ""
            with st.spinner(f"💬 Processing {len(chunks)} chunk(s)..."):
                for i, chunk in enumerate(chunks, 1):
                    st.info(f"Processing chunk {i}/{len(chunks)}...")
                    prompt = prompt_template + f"\nDocument text:\n{chunk}"
                    try:
                        response = client.chat.completions.create(
                            model="gpt-3.5-turbo",
                            messages=[{"role": "user", "content": prompt}]
                        )
                        combined_output += f"\n--- Response for chunk {i} ---\n"
                        combined_output += response.choices[0].message.content + "\n"
                    except Exception as e:
                        combined_output += f"\n❌ Error processing chunk {i}: {e}\n"
            st.success("✅ Analysis complete!")
            st.markdown(combined_output)