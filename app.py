import streamlit as st
from PyPDF2 import PdfReader
import openai
from fpdf import FPDF

st.set_page_config(page_title="Flight Briefing Summary", layout="centered")
st.title("🛫 Flight Briefing Summary Generator")

if "api_valid" not in st.session_state:
    st.session_state.api_valid = False
if "api_key" not in st.session_state:
    st.session_state.api_key = ""
if "report_text" not in st.session_state:
    st.session_state.report_text = ""

# API Key
if not st.session_state.api_valid:
    api_key = st.text_input("🔑 Paste your OpenAI API key:", type="password")
    if api_key:
        try:
            client = openai.OpenAI(api_key=api_key)
            _ = client.models.list()
            st.session_state.api_key = api_key
            st.session_state.api_valid = True
            st.success("✅ API key validated.")
        except Exception as e:
            st.error(f"❌ Invalid API key: {e}")
else:
    client = openai.OpenAI(api_key=st.session_state.api_key)

# Upload
uploaded_file = st.file_uploader("📄 Upload a Flight Briefing PDF", type="pdf")

# Helper
def chunk_text(text, chunk_size=3000):
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

# PDF Export
def generate_pdf(content):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=11)
    for line in content.split("\n"):
        pdf.multi_cell(0, 10, line)
    return pdf

# Main processing
if uploaded_file and st.session_state.api_valid:
    reader = PdfReader(uploaded_file)
    doc_text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            doc_text += page_text + "\n"

    confirm = st.button("✈️ Generate Summary")

    if confirm:
        chunks = chunk_text(doc_text)
        partial_answers = []

        with st.spinner("🧠 Analysing briefing pack..."):
            for chunk in chunks:
                prompt = (
                    "You are a senior flight operations analyst. Review the following briefing pack excerpt "
                    "and extract key operational information about weather and NOTAMs. "
                    "Focus on threats, operational risks, and suggested mitigations.

"
                    f"{chunk}"
                )
                try:
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": prompt}]
                    )
                    partial_answers.append(response.choices[0].message.content.strip())
                except Exception as e:
                    partial_answers.append(f"Error: {e}")

        collate_prompt = (
            "Summarise the following aviation weather and NOTAM notes into a single operational-style briefing. "
            "Structure it using ICAO threat and mitigation terminology.

"
            + "\n\n".join(partial_answers)
        )

        try:
            collated = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": collate_prompt}]
            )
            section_one = collated.choices[0].message.content.strip()
        except Exception as e:
            section_one = f"❌ Error while collating results: {e}"

        # Foreign Office context
        fco_prompt = (
            "Based on the context below, identify any countries or regions mentioned. "
            "Then summarise the current UK Foreign Office travel advice for those areas.

"
            f"{doc_text[:3000]}"
        )
        try:
            response_fco = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": fco_prompt}]
            )
            fco_summary = response_fco.choices[0].message.content.strip()
        except Exception as e:
            fco_summary = f"❌ Error retrieving FCO advice: {e}"

        full_report = f"FLIGHT ANALYSIS SUMMARY\n\n{section_one}\n\nFOREIGN OFFICE SECURITY BRIEFING\n{fco_summary}"
        st.session_state.report_text = full_report

        st.markdown("### 📝 Briefing Output")
        st.text_area("Flight Analysis", full_report, height=400)

        # Optional download
        if st.button("📥 Download PDF"):
            pdf = generate_pdf(full_report)
            pdf.output("/tmp/briefing_summary.pdf")
            with open("/tmp/briefing_summary.pdf", "rb") as f:
                st.download_button("⬇️ Download Flight Summary PDF", f, file_name="Flight_Analysis_Summary.pdf")