from flask import Flask, request, jsonify
import pandas as pd
import openai
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
openai.api_key = os.getenv('OPENAI_API_KEY')

app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)  # Ensure the upload folder exists

# Global variable to store the dataframe
df = None

@app.route('/')
def home():
    return "Welcome to the Data Analytics API! Use the /upload and /analyze endpoints."

@app.route('/favicon.ico')
def favicon():
    return '', 204

@app.route('/upload', methods=['POST'])
def upload_file():
    global df  # Declare df as global
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and file.filename.endswith('.csv'):
        # Save the file to the uploads folder
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        
        # Read the CSV file into a DataFrame
        df = pd.read_csv(filepath)
        
        print(f"File {file.filename} uploaded successfully")
        
        return jsonify({'message': 'File uploaded successfully'})
    else:
        return jsonify({'error': 'Invalid file type, please upload a CSV file'}), 400

@app.route('/analyze', methods=['POST'])
def analyze_data():
    global df
    if df is None:
        return jsonify({'error': 'No data available. Please upload a CSV file first.'}), 400

    user_input = request.form.get('input')
    if not user_input:
        return jsonify({'error': 'No input provided'}), 400

    # Ensure df.head() or df.sample() shows the data correctly
    prompt = f"Given the following data: {df.head().to_string()}, please {user_input}"
    messages = [{"role": "system", "content": "You are a data analysis assistant."},
                {"role": "user", "content": prompt}]
    
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages,
        max_tokens=1500
    )
    
    analysis = response.choices[0].message['content']

    return jsonify({'analysis': analysis})

if __name__ == '__main__':
    app.run(debug=True)
