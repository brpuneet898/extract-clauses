import streamlit as st
import re
from PyPDF2 import PdfReader
from docx import Document

# Function to extract text from PDF
def extract_text_from_pdf(pdf_file):
    reader = PdfReader(pdf_file)
    text = ''
    for page in reader.pages:
        text += page.extract_text()
    return text

# Function to extract text from DOCX
def extract_text_from_docx(docx_file):
    doc = Document(docx_file)
    text = ''
    for para in doc.paragraphs:
        text += para.text + '\n'
    return text

# Function to identify and extract clauses from the document text
def extract_clauses(text):
    # Regular expression pattern to match numbered or bulleted points
    # This pattern will match:
    # 1. Clause heading
    # 2. Bullet point (• or -)
    # A clause ends when a new numbered/bulleted point starts.
    pattern = r'(\d+[\.)]|•|-)\s*([^\n]+)\.(.*?)(?=\n(\d+[\.)]|•|-|\Z))'
    
    clauses = []

    # Find all matches using regex
    matches = re.findall(pattern, text, flags=re.DOTALL)

    # Iterate through the matches and organize them into a list of clauses
    for match in matches:
        number_or_bullet = match[0].strip()  # Number or bullet point
        heading = match[1].strip()  # Clause heading (e.g., "Board Duties")
        description = match[2].strip()  # Clause description

        # Format the extracted clause
        clause = f"{number_or_bullet} {heading}: {description}"
        clauses.append(clause)

    # Now handle cases where the last clause does not have a new clause after it
    # Example: handle ending parts like "Governing Law"
    if len(clauses) > 0:
        last_clause = clauses[-1]
        if last_clause.endswith('Governing Law'):
            clauses[-1] = last_clause + " [Clause continued without a new clause]"

    return clauses

# Streamlit UI
st.title("Legal Clause Extractor")

# File uploader to upload either PDF or DOCX file
uploaded_file = st.file_uploader("Upload a PDF or DOCX file", type=["pdf", "docx"])

if uploaded_file is not None:
    # Extract text based on file type
    if uploaded_file.type == "application/pdf":
        st.write("Extracting text from PDF...")
        text = extract_text_from_pdf(uploaded_file)
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        st.write("Extracting text from DOCX...")
        text = extract_text_from_docx(uploaded_file)

    # Call the function to extract clauses
    st.write("Extracting clauses from the document...")
    clauses = extract_clauses(text)

    # Display the extracted clauses
    if clauses:
        st.subheader("Extracted Legal Clauses:")
        for idx, clause in enumerate(clauses, 1):
            st.write(f"**Clause {idx}:** {clause}")
    else:
        st.write("No clauses were extracted, or there was an issue with the document.")
