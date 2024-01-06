from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-key-goes-here'

# Flask Authentication and Login Manager
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app=app)

# CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy()
db.init_app(app)


# CREATE TABLE IN DB
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
    
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

 
 
with app.app_context():
    db.create_all()


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/register', methods=["GET","POST"])
def register():
    if request.method == "POST":
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        hashed_password = generate_password_hash(password, method='sha256', salt_length=8)
        print(hashed_password)
        
        # Check if email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return "Email already registered. Please user a different email."

        # Add new user to the database
        new_user = User(name=name, password=hashed_password, email=email)
        db.session.add(new_user)
        
        try:
            db.session.commit()
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            return f"{e}: An error occurred registering the user. Please try again."
        
        
    return render_template("register.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('secrets'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('secrets'))
        else:
            flash('Invalid email or password')

    return render_template('login.html')


@app.route('/secrets')
def secrets():
    return render_template("secrets.html")


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))



@app.route('/download', methods=["GET", "POST"])
@login_required
def download():
    try:
        return send_from_directory('static', "files/cheat_sheet.pdf", as_attachment=True)
    except Exception as e:
        return str(e)


if __name__ == "__main__":
    app.run(debug=True)
