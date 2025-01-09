import streamlit as st
from transformers import AutoTokenizer, AutoModelForTokenClassification
from PyPDF2 import PdfReader
from docx import Document
import torch

# Load InLegalBERT from Hugging Face
tokenizer = AutoTokenizer.from_pretrained("law-ai/InLegalBERT")
model = AutoModelForTokenClassification.from_pretrained("law-ai/InLegalBERT")

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

# Function to extract legal clauses using InLegalBERT
def extract_clauses_from_legalbert(text):
    # Tokenize the input text
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)

    # Get model outputs
    with torch.no_grad():
        outputs = model(**inputs)

    # Extract tokens and labels
    logits = outputs.logits
    predictions = torch.argmax(logits, dim=-1).squeeze().cpu().numpy()

    # Decode tokens and identify clause-related tokens (depends on the model's labeling scheme)
    tokens = tokenizer.convert_ids_to_tokens(inputs['input_ids'].squeeze().cpu().numpy())
    clauses = []

    # Iterate through tokens and consider clause-like tokens
    current_clause = []
    for token, prediction in zip(tokens, predictions):
        if prediction != 0:  # Assuming '0' is the label for non-clause tokens
            current_clause.append(token)
        else:
            if current_clause:
                clauses.append(" ".join(current_clause))
                current_clause = []
    
    if current_clause:  # Append any remaining clause
        clauses.append(" ".join(current_clause))

    return clauses

# Streamlit UI
st.title("Legal Clause Extractor with InLegalBERT")

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

    # Call InLegalBERT model to extract legal clauses
    st.write("Extracting legal clauses using InLegalBERT...")
    clauses = extract_clauses_from_legalbert(text)

    # Display the extracted clauses
    if clauses:
        st.subheader("Extracted Legal Clauses:")
        for idx, clause in enumerate(clauses, 1):
            st.write(f"**Clause {idx}:** {clause}")
    else:
        st.write("No clauses were extracted, or there was an issue with the document.")
