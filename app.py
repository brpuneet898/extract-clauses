import streamlit as st
import re
from PyPDF2 import PdfReader
from docx import Document

def extract_text_from_pdf(pdf_file):
    reader = PdfReader(pdf_file)
    text = ''
    for page in reader.pages:
        text += page.extract_text()
    return text

def extract_text_from_docx(docx_file):
    doc = Document(docx_file)
    text = ''
    for para in doc.paragraphs:
        text += para.text + '\n'
    return text

def extract_clauses(text):
    pattern = r'(\d+[\.)]|•|-)\s*([^\n]+)\.(.*?)(?=\n(\d+[\.)]|•|-|\Z))'
    
    clauses = []
    matches = re.findall(pattern, text, flags=re.DOTALL)

    for match in matches:
        number_or_bullet = match[0].strip()  
        heading = match[1].strip()  
        description = match[2].strip()  

        clause = f"{number_or_bullet} {heading}: {description}"
        clauses.append(clause)

    if len(clauses) > 0:
        last_clause = clauses[-1]
        if last_clause.endswith('Governing Law'):
            clauses[-1] = last_clause + " [Clause continued without a new clause]"

    return clauses

st.title("Legal Clause Extractor")

uploaded_file = st.file_uploader("Upload a PDF or DOCX file", type=["pdf", "docx"])

if uploaded_file is not None:
    if uploaded_file.type == "application/pdf":
        st.write("Extracting text from PDF...")
        text = extract_text_from_pdf(uploaded_file)
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        st.write("Extracting text from DOCX...")
        text = extract_text_from_docx(uploaded_file)

    st.write("Extracting clauses from the document...")
    clauses = extract_clauses(text)

    if clauses:
        st.subheader("Extracted Legal Clauses:")
        for idx, clause in enumerate(clauses, 1):
            st.write(f"**Clause {idx}:** {clause}")
    else:
        st.write("No clauses were extracted, or there was an issue with the document.")
