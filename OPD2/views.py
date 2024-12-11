"""
Routes and views for the flask application.
"""

from datetime import datetime
from OPD2 import app
from flask import render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
from outfit_display import get_random_outfit, plot_outfit


app.secret_key = os.urandom(24)
MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_LENGTH = 64

def get_db_connection():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    with conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                email TEXT UNIQUE
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS favorites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                outfit_image TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
    conn.close()


if not os.path.exists('favorites.db'):
    init_db()

if not os.path.exists('users.db'):
    init_db()


@app.route('/')
def home():
    user = None
    if 'username' in session:
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (session['username'],)).fetchone()
        conn.close()
    return render_template('index.html', user=user)



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'] 
        password = request.form['password'] 
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password'], password): 
            session['username'] = username  
            flash('Login successful!', 'success')   
            return redirect(url_for('home')) 
        else:
            flash('Invalid username or password.', 'error')  
    
    return render_template('index.html') 

@app.route('/register', methods=['POST'])
def register():
    username = request.form['username'] 
    email = request.form['email']    
    password = request.form['password']    

    if len(password) < MIN_PASSWORD_LENGTH or len(password) > MAX_PASSWORD_LENGTH:
        flash(f'The password must contain from {MIN_PASSWORD_LENGTH} before {MAX_PASSWORD_LENGTH} symbols.', 'error')
        return redirect(url_for('home')) 

    hashed_password = generate_password_hash(password, method='pbkdf2:sha256:600000')

    conn = get_db_connection()
    try:
        with conn:
            conn.execute(
                'INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                (username, email, hashed_password)
            )
        flash('Registration was successful! Now you can login.', 'success')
        return redirect(url_for('home')) 
    except sqlite3.IntegrityError:
        flash('Username already exists.', 'error')
        return redirect(url_for('home'))  
    finally:
        conn.close()

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('username', None)  
    flash('You have been logged out.', 'success')  
    return redirect(url_for('home'))  

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'username' in session:
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (session['username'],)).fetchone()
        conn.close()

        return render_template('office.html', user=user)
    else:
        flash("Please login to access your profile.", "error")
        return render_template('index.html') 

    
@app.route('/update_profile', methods=['POST'])
def update_profile():
    if 'username' in session:
        username = request.form['username']
        email = request.form['email']

        conn = get_db_connection()
        conn.execute('UPDATE users SET username = ?, email = ?, WHERE username = ?',
                     (username, email, session['username']))
        conn.commit()
        conn.close()

        flash("The data has been successfully updated.", "success")
        return redirect(url_for('profile'))
    else:
        flash("Please log in to perform this action.", "error")
        return redirect(url_for('index'))
    
@app.route('/contact')
def contact():
    return render_template('contact.html')
    
@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/gen')
def gen():
    upper_body_img, lower_body_img, footwear_img = get_random_outfit()
    
    if upper_body_img is not None and lower_body_img is not None and footwear_img is not None:
        plot_outfit(upper_body_img, lower_body_img, footwear_img)
        
        return render_template('generation.html', outfit_image='static/outfit.png')
    
    return "No outfit available."

@app.route('/generate')
def generate():
    return redirect(url_for('gen'))

@app.route('/save_favorite', methods=['POST'])
def save_favorite():
    if 'username' in session:
        outfit_image = request.form['outfit_image']
        conn = get_db_connection()
        
        user = conn.execute('SELECT id FROM users WHERE username = ?', (session['username'],)).fetchone()
        if user:
            with conn:
                conn.execute('INSERT INTO favorites (user_id, outfit_image) VALUES (?, ?)', (user['id'], outfit_image))
            flash('Outfit saved to favorites!', 'success')
        else:
            flash('User not found.', 'error')
        
        conn.close()
    else:
        flash("Please log in to save favorites.", "error")
    
    return redirect(url_for('gen'))

@app.route('/favorites')
def favorites():
    if 'username' in session:
        conn = get_db_connection()
        user = conn.execute('SELECT id FROM users WHERE username = ?', (session['username'],)).fetchone()
        
        if user:
            favorites = conn.execute('SELECT outfit_image FROM favorites WHERE user_id = ?', (user['id'],)).fetchall()
            return render_template('favorites.html', favorites=favorites)
        
    flash("Please log in to view your favorites.", "error")
    return redirect(url_for('home'))