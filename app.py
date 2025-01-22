from flask import Flask, request, render_template, redirect, url_for, session, Markup
import asyncio
import script  # Import your script here

app = Flask(__name__)
app.secret_key = 'ANCH1234'

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
    
    session['results'] = asyncio.run(script.main(notes, caregivers, final))
    return redirect(url_for('results'))  # Return the results

@app.route('/results')
def results():
    # Get results from session
    results = session.pop('results', None)  # Pop ensures it's cleared after showing
    results = Markup(results)

    if not results:
        return redirect(url_for('home'))  # Redirect to home if no results
    return render_template('results.html', results=results)  # Display results
    
if __name__ == '__main__':
    app.run(debug=True)
