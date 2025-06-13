import os
import json
import google.generativeai as genai
import vertexai

def get_gemini_api_key():
    try:
        with open("gemini_key.json") as f:
            key = json.load(f)["GEMINI_API_KEY"]
            if not key:
                raise ValueError("❌ GEMINI_API_KEY is empty.")
            return key
    except Exception as e:
        print("❌ Failed to load Gemini key:", e, flush=True)
        raise

def summarize_text_gemini(text, filename=None):
    """Summarizes text using Gemini AI with context-aware prompting."""
    
    vertextai.init(project="gmailattachmentsummarizer",location="us-central1")
    
    api_key = get_gemini_api_key()
    #genai.configure(api_key=api_key,project_id="gmailattachmentsummarizer",location="us-central1")
    genai.configure(api_key=api_key)
    
    

    filetype_prompt = ""
    if filename:
        ext = os.path.splitext(filename)[-1].lower()
        filetype_prompt = {
            ".csv": "This is a CSV file. Provide a summary describing the contents, columns, and patterns.",
            ".feature": "This is a Gherkin feature file. Summarize the test scenarios and feature purpose.",
            ".docx": "This is a DOCX document. Provide a concise summary of its contents.",
            ".pdf": "This is a PDF document. Summarize its content accurately.",
            ".jpg": "This is text extracted from an image. Summarize what can be understood from it.",
            ".jpeg": "This is text extracted from an image. Summarize what can be understood from it.",
            ".png": "This is text extracted from an image. Summarize what can be understood from it.",
            ".txt": "This is a plain text file. Provide a brief summary of its content."
        }.get(ext, "Summarize the following document's content.")

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
