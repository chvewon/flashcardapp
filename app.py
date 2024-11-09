from flask import Flask, request, jsonify
from PIL import Image
from flask import Flask
from flask_cors import CORS



import pytesseract
import pdfplumber
import io
import requests
import openai

app = Flask(__name__)
CORS(app)  # This enables CORS for all routes in the app

# Route for handling text extraction
@app.route('/extract-text', methods=['POST'])
def extract_text():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    
    try:
        if file.content_type.startswith('image/'):
            # Use Tesseract OCR for image files
            image = Image.open(file)
            text = pytesseract.image_to_string(image)
        elif file.content_type == 'application/pdf':
            # Use pdfplumber for PDFs
            text = ""
            with pdfplumber.open(file) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() or ""
        else:
            return jsonify({"error": "Unsupported file type"}), 400

        return jsonify({"text": text})
    
    except Exception as e:
        return jsonify({"error": "Failed to process file"}), 500


# Configure OpenAI API Key
#openai.api_key = 'your_openai_api_key'
# Route for generating Flash cards 
@app.route('/generate-flashcards', methods=['POST'])
def generate_flashcards_from_text():
     data = request.get_json()
     ext_text = data.get('text', '').strip()
     print (ext_text)
     if not ext_text:
         return jsonify({"error": "No text provide"}), 400
       
    # Define the prompt to instruct the model to create flashcards
     prompt = (
        f"Create flashcards from the following text. For each flashcard, "
        f"provide a question and a corresponding answer. Use a clear and concise format:\n\n"
        f"{ext_text}\n\n"
        "Flashcards:\n"
        "Question: <Your question here>\nAnswer: <The answer here>\n"
     )
     print (prompt)
     # Call OpenAI API
     response = openai.ChatCompletion.create(
        model="gpt-4-turbo",  # Or "gpt-4" if you have access
        messages=[
        {"role": "user", "content": prompt}  # Correctly format the message
        ],
        max_tokens=300,  # Adjust as needed based on text length and expected response
        temperature=0.5  # Adjust for creativity (lower for more straightforward answers)
     )
    

     flashcards = response['choices'][0]['message']['content']
     print(flashcards)
     return jsonify({"text": flashcards})
    # return flashcards



if __name__ == '__main__':
    app.run(debug=True)



# Example usage
#extracted_text = """
#Python is a high-level, interpreted programming language known for its readability and versatility.
#It is commonly used in data science, web development, automation, and more. Python emphasizes simplicity and efficiency.
#"""

flashcards = generate_flashcards_from_text(extracted_text)
print(flashcards)
