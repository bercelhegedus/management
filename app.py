
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from dataentry_app import dataentry_blueprint
from update_app import update_blueprint
from users import User

# Example users (id, username, password)
users = [
    User(1, 'alice', 'password123'),
    User(2, 'bob', 'securepass')
]

app = Flask(__name__)

app.register_blueprint(dataentry_blueprint)
app.register_blueprint(update_blueprint)

app.config['SECRET_KEY'] = 'your_secret_key_here'  # Change this to a random string

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # specify what function is the login view

@login_manager.user_loader
def load_user(user_id):
    return next((user for user in users if user.id == int(user_id)), None)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = next((user for user in users if user.username == username), None)
        if user and user.verify_password(password):
            login_user(user)
            return redirect(url_for('landing'))
        flash('Invalid username or password.')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def landing():
    return render_template('landing_index.html')

if __name__ == '__main__':
    app.run(debug=True)
