from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file
import json
import random
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np
from PIL import Image
import os
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors

app = Flask(__name__)
app.secret_key = 'supersecretkey'

model = load_model('bdc.h5')

disease_keywords = {
    "Disease A": ["headache", "fever", "dizziness"],
    "Disease B": ["nausea", "vomiting", "abdominal pain"],
    "Disease C": ["chest pain", "shortness of breath", "fatigue"]
}

def preprocess_and_predict(file):
    # Save the uploaded file
    file_path = os.path.join('uploads', file.filename)
    file.save(file_path)

    # Load the image and resize it to the input size the model expects (224x224)
    img = image.load_img(file_path, target_size=(224, 224))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension
    img_array = img_array / 255.0  # Normalize the image
    
    # Predict the class probabilities
    predictions = model.predict(img_array)
    
    # Get the predicted class (the class with the highest probability)
    predicted_class = np.argmax(predictions, axis=1)[0]
    
    # Map class index to disease name (use a dictionary for your classes)
    disease_classes = {
        0: "Disease A",
        1: "Disease B",
        2: "Disease C",
        3: "Epilepsy",
        4: "Disease E",
        5: "Disease F"
    }
    
    # Return the predicted disease name
    return disease_classes.get(predicted_class, "Unknown Disease")

# Helper function to load users data from user.json
def load_users():
    try:
        with open('user.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

# Helper function to save users data to user.json
def save_users(users_data):
    with open('user.json', 'w') as f:
        json.dump(users_data, f, indent=4)

# Home route - login page
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        users = load_users()
        for user in users:
            if user['username'] == username and user['password'] == password:
                session['username'] = username
                return redirect(url_for('dashboard'))
        
        flash("Invalid username or password!")
        return redirect(url_for('login'))
    return render_template('login.html')

# Route for account creation page
@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']
        contact = request.form['contact']
        
        otp = random.randint(100000, 999999)
        print(f"Your OTP is: {otp}")  # This simulates OTP sent to user
        
        session['otp'] = otp  # Save OTP to session for verification
        
        # Store user data in session temporarily until OTP verification
        session['new_user_data'] = {
            'username': username,
            'password': password,
            'name': name,
            'age': age,
            'gender': gender,
            'contact': contact
        }
        
        return redirect(url_for('otp_verify'))
    
    return render_template('create.html')


def generate_pdf(symptoms, matched_diseases):
    
    pdf_path = os.path.join('static', 'reports', 'symptoms_report.pdf')
    
    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
    # Retrieve user data from session
    users = load_users()
    current_user = None
    for user in users:
        if user['username'] == session['username']:
            current_user = user
            break

    # Get user details
    name = current_user['name']
    age = current_user['age']
    gender = current_user['gender']
    contact = current_user['contact']

    # Create an in-memory PDF
    c = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter

    # Add logo to the report
    logo_path = os.path.join(os.getcwd(), 'static', 'logo.png')  # Make sure to place your logo here
    c.drawImage(logo_path, 30, height - 100, width=100, height=50)  # Logo placement (left top)

    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(150, height - 50, "Brain Disease Detection Report")
    
    # Confidential Header
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(colors.red)
    c.drawString(30, height - 120, "CONFIDENTIAL - MEDICAL REPORT")

    # Patient Information Section
    c.setFont("Helvetica", 10)
    c.setFillColor(colors.black)
    c.drawString(30, height - 150, f"Patient Name: {name}")
    c.drawString(30, height - 170, f"Age: {age}")
    c.drawString(30, height - 190, f"Gender: {gender}")
    c.drawString(30, height - 210, f"Contact Number: {contact}")

    # Symptoms Section
    c.setFont("Helvetica-Bold", 12)
    c.drawString(30, height - 240, "Symptoms Provided:")
    c.setFont("Helvetica", 10)
    c.drawString(30, height - 260, symptoms)

    # Possible Disease Section
    c.setFont("Helvetica-Bold", 12)
    c.drawString(30, height - 290, "Possible Disease(s) Identified:")
    y_position = height - 310
    for disease in matched_diseases:
        c.setFont("Helvetica", 10)
        c.drawString(30, y_position, f"- {disease}")
        y_position -= 20

    # Disease Summary Section (Dummy data for now, you can expand this based on actual disease summaries)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(30, y_position - 30, "Possible Disease Summary:")

    y_position -= 40
    disease_summaries = {
        "Disease A": "Disease A typically involves symptoms like headache and dizziness.",
        "Disease B": "Disease B involves nausea and abdominal pain, often associated with gastrointestinal issues.",
        "Disease C": "Disease C affects the heart and lungs, causing chest pain and shortness of breath."
    }

    for disease in matched_diseases:
        c.setFont("Helvetica", 10)
        summary = disease_summaries.get(disease, "No summary available.")
        y_position -= 20
        c.drawString(30, y_position, f"{disease}: {summary}")
        y_position -= 40

    # Closing statement
    c.setFont("Helvetica", 10)
    c.drawString(30, y_position - 30, "Please consult a medical professional for further evaluation and treatment.")

    c.showPage()
    c.save()

    return pdf_path

@app.route('/disease', methods=['GET', 'POST'])
def disease():
    # Check if user is logged in
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        symptoms = request.form['symptoms'].lower()
        symptoms_words = set(symptoms.split())

        matched_diseases = []
        
        users = load_users()
        current_user = None
        for user in users:
            if user['username'] == session.get('username'):
                current_user = user
                break

        if current_user:
            # Update symptoms data for the user
            current_user['symptoms'] = symptoms

            # Save the updated user data back to the JSON file
            save_users(users)
        
        # Compare the extracted words with the disease keywords
        for disease, keywords in disease_keywords.items():
            for symptom in keywords:
                if symptom in symptoms_words:
                    matched_diseases.append(disease)
                    break  # No need to check further if one symptom matches
        
        if matched_diseases:
            pdf_path = generate_pdf(symptoms, matched_diseases)
            return render_template('dis.html', diseases=matched_diseases, pdf_url=pdf_path)


    return render_template('disease.html')

# OTP verification page
@app.route('/otp_verify', methods=['GET', 'POST'])
def otp_verify():
    if 'otp' not in session:
        return redirect(url_for('create_account'))

    if request.method == 'POST':
        otp_input = request.form['otp']
        if str(session['otp']) == otp_input:
            # OTP verified, save user data
            users = load_users()
            new_user = session['new_user_data']
            user_id = len(users)  # Index-based approach
            new_user['user_id'] = user_id
            new_user['symptoms'] = []
            users.append(new_user)
            save_users(users)

            flash("Account created successfully!")
            session.pop('otp', None)  # Clear OTP from session
            session.pop('new_user_data', None)  # Clear user data from session
            return redirect(url_for('login'))
        else:
            flash("Incorrect OTP! Please try again.")
            return redirect(url_for('otp_verify'))
    
    return render_template('otp_verify.html', otp=session['otp'])

# Dashboard route
@app.route('/dashboard', methods=['GET'])
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    return render_template('dash.html', username=session['username'])

# Logout handling
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

# Profile page route
@app.route('/profile', methods=['GET'])
def profile():
    if 'username' not in session:
        return redirect(url_for('login'))

    users = load_users()
    current_user = None
    for user in users:
        if user['username'] == session['username']:
            current_user = user
            break

    return render_template('profile.html', user=current_user)

# Voice-to-text page for extracting symptoms
@app.route('/symptoms', methods=['GET', 'POST'])
def symptoms():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        symptoms_text = request.form['symptoms']
        users = load_users()
        for user in users:
            if user['username'] == session['username']:
                user['symptoms'] = symptoms_text.split(',')  # Save symptoms as a list
                break
        save_users(users)
        flash("Symptoms saved successfully!")
        return redirect(url_for('possible_disease'))

    return render_template('symptoms.html')

# Possible Disease Suggestion page
@app.route('/possible_disease', methods=['GET'])
def possible_disease():
    if 'username' not in session:
        return redirect(url_for('login'))

    users = load_users()
    current_user = None
    for user in users:
        if user['username'] == session['username']:
            current_user = user
            break

    symptoms = current_user.get('symptoms', [])
    possible_diseases = ["Disease A", "Disease B", "Disease C"]  # Dummy suggestions

    # Logic to match symptoms with possible diseases
    matched_diseases = [disease for disease in possible_diseases if any(symptom in disease for symptom in symptoms)]

    return render_template('possible_disease.html', diseases=matched_diseases)

# Bookings page
@app.route('/bookings', methods=['GET'])
def bookings():
    if 'username' not in session:
        return redirect(url_for('login'))

    doctors = [
        {"name": "Dr. Smith", "specialty": "Neurologist", "contact": "1234567890"},
        {"name": "Dr. Johnson", "specialty": "Neurosurgeon", "contact": "9876543210"},
        {"name": "Dr. Lee", "specialty": "General Physician", "contact": "5555555555"}
    ]

    return render_template('book.html', doctors=doctors)

# Scans analysis page
@app.route('/scans_analysis', methods=['GET', 'POST'])
def scans_analysis():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Handle the image upload (placeholder)
        file = request.files['scan']
        if file:
            # For now, just simulate the scan analysis result
            res = preprocess_and_predict(file)
            session['scan_result'] = res
            return redirect(url_for('scan_results'))

    return render_template('scan.html')

# Scan results page
@app.route('/scan_results', methods=['GET'])
def scan_results():
    if 'username' not in session:
        return redirect(url_for('login'))

    scan_result = session.get('scan_result', "No results yet.")
    loading = session.get('loading', False)
    return render_template('results.html', result=scan_result, loading=loading)

if __name__ == '__main__':
    app.run(debug=True)
