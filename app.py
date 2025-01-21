from flask import Flask, request, render_template
import asyncio
import test_script  # Import your script here

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')  # Create a simple HTML form for uploads

@app.route('/upload', methods=['POST'])
def upload_files():
    files = request.files.getlist('files')  # Get the list of uploaded files
    if files:
        file_names = [file.filename for file in files]  # Extract file names
        print(f"Uploaded files: {file_names}")  # For debugging
        
        # Pass file names and files to your script
        results = asyncio.run(test_script.main(files, file_names))
        return results  # Return the results
    else:
        return "No files uploaded!"
    
if __name__ == '__main__':
    app.run(debug=True)
