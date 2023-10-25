import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from pymongo import MongoClient

app = Flask(__name__)
app.secret_key = 'YOUR_SECRET_KEY'  # Replace with your own secure secret key

# Initialize the MongoDB client with your MongoDB Atlas URI
uri = "mongodb+srv://grievances:kavi1234@cluster0.2l5sbxf.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(uri)

# Specify your database and collection names
databaseName = 'grievancedb'
collectionName = 'grievancecln'
database = client[databaseName]
collection = database[collectionName]

# Directory to store login details
LOGIN_DETAILS_DIR = 'login_details'

# Create the login details directory if it doesn't exist
if not os.path.exists(LOGIN_DETAILS_DIR):
    os.makedirs(LOGIN_DETAILS_DIR)

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the user exists in MongoDB
        user_data = collection.find_one({'username': username})
        if user_data and user_data['password'] == password:
            session['username'] = username

            # Create a file to store login details
            login_details_file = os.path.join(LOGIN_DETAILS_DIR, f"{username}_login_details.txt")
            with open(login_details_file, 'w') as details_file:
                details_file.write(f'Username: {username}, Password: {password}\n')

            return redirect(url_for('dashboard'))
        else:
            flash("Login failed. Please check your credentials.", 'error')

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        fullname = request.form['fullname']
        gender = request.form['gender']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Check if the user already exists in MongoDB
        existing_user = collection.find_one({'username': username})
        if existing_user:
            flash("Registration failed. Username already exists.", 'error')
        elif password != confirm_password:
            flash("Registration failed. Passwords do not match.", 'error')
        else:
            # Insert the new user into MongoDB
            new_user = {'username': username, 'fullname': fullname, 'gender': gender, 'password': password}
            collection.insert_one(new_user)

            flash("Registration successful! You can now log in.", 'success')
            return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        return render_template('dashboard.html', username=session['username'])
    else:
        return redirect(url_for('login'))

@app.route('/progress')
def progress():
    return render_template('progress.html')

@app.route('/fill')
def fill():
    return render_template('fill.html')

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=5000)

