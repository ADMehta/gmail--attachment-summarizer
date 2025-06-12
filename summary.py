import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("❌ GEMINI_API_KEY not found. Check your .env file.")
genai.configure(api_key=api_key)

def summarize_text_gemini(text, filename=None):
    """Summarizes text using Gemini AI with context-aware prompting."""

    # Determine file type from extension
    filetype_prompt = ""
    if filename:
        ext = os.path.splitext(filename)[-1].lower()
        if ext == ".csv":
            filetype_prompt = "This is a CSV file. Provide a summary describing the contents, columns, and patterns."
        elif ext == ".feature":
            filetype_prompt = "This is a Gherkin feature file. Summarize the test scenarios and feature purpose."
        elif ext == ".docx":
            filetype_prompt = "This is a DOCX document. Provide a concise summary of its contents."
        elif ext == ".pdf":
            filetype_prompt = "This is a PDF document. Summarize its content accurately."
        elif ext in [".jpg", ".jpeg", ".png"]:
            filetype_prompt = "This is text extracted from an image. Summarize what can be understood from it."
        elif ext in [".txt"]:
            filetype_prompt = "This is a plain text file. Provide a brief summary of its content."
        else:
            filetype_prompt = "Summarize the following document's content."

    prompt = f"{filetype_prompt}\n\n{text.strip()}"

    model = genai.GenerativeModel("gemini-1.5-pro")
    response = model.generate_content(
        prompt,
        generation_config={
            "temperature": 0.7,
            "max_output_tokens": 200
        }
    )
    return response.text.strip()
