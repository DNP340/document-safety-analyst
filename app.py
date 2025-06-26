import streamlit as st
from PyPDF2 import PdfReader

st.title("📄 Document Safety Analyst Tool")

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

    st.text_area("📑 Extracted Document Text (copy this into ChatGPT prompt below)", text, height=400)

    st.markdown("""
    ### ✅ Standard Prompt to Paste into ChatGPT
    ```
    Apply the following questions to the document text:
    1️⃣ What is the purpose of this document?
    2️⃣ Are there any operational limitations specified?
    3️⃣ Are there any safety-critical items noted?
    4️⃣ Are all required regulatory references present? If any are missing, highlight them.
    5️⃣ Are NOTAMs, weather information, or airport data outdated or missing?
    6️⃣ Are any MEL/CDL items declared?
    7️⃣ Are crew rest, accommodation, or duty arrangements mentioned, and are they appropriate?
    8️⃣ Are contingency or emergency procedures documented? Summarise them.
    9️⃣ Are risk mitigations clearly defined?
    🔟 Are responsibilities and accountabilities clearly allocated?

    Output format:
    - Purpose:
    - Operational limitations:
    - Safety-critical items:
    - Regulatory references (present/missing):
    - NOTAMs/weather/airport data status:
    - MEL/CDL items:
    - Crew rest/accommodation:
    - Contingency procedures:
    - Risk mitigations:
    - Responsibilities:
    ```
    """)