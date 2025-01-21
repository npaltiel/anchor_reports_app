from flask import Flask, request, render_template
import asyncio
import test_script  # Import your script here

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')  # Create a simple HTML form for uploads

@app.route('/upload', methods=['POST'])
def upload_files():
    notes = request.files.get('Notes')  # Access file from 'file1' field
    caregivers = request.files.get('Caregivers')  # Access file from 'file2' field
    final = request.files.get('Final')

    # Check if files are uploaded
    if not notes or not caregivers or not final:
        return "All three files must be uploaded!", 400
    
    results = asyncio.run(test_script.main(notes, caregivers, final))
    return results  # Return the results
    
if __name__ == '__main__':
    app.run(debug=True)
