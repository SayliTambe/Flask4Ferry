from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, ValidationError
import bcrypt
from flask_mysqldb import MySQL
from flask_sqlalchemy import SQLAlchemy
from datetime import date, timedelta

app = Flask(__name__)

# MySQL Configuration for user authentication
app.config['MYSQL_HOST'] = '144.24.96.48'
app.config['MYSQL_USER'] = 'khoji'
app.config['MYSQL_PASSWORD'] = 'Khoji@123'
app.config['MYSQL_DB'] = 'FerryOne'
app.secret_key = 'ganesh'

mysql = MySQL(app)

# SQLAlchemy Configuration for promotion management
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Sayli%40123@localhost/promotion_ferry'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class RegisterForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Register")

    def validate_email(self, field):
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users where email=%s", (field.data,))
        user = cursor.fetchone()
        cursor.close()
        if user:
            raise ValidationError('Email Already Taken')

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")

class Promotion(db.Model):
    __tablename__ = 'promotion'
    title = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(20), nullable=False, unique=True, primary_key=True)
    from_date = db.Column(db.Date, nullable=False)
    to_date = db.Column(db.Date, nullable=False)
    percentage = db.Column(db.Integer, nullable=False)

@app.route('/')
def promo():
    return render_template('promo.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password = form.password.data

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Store data into the database
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)", (name, email, hashed_password))
        mysql.connection.commit()
        cursor.close()

        return redirect(url_for('login'))

    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cursor.fetchone()
        cursor.close()
        if user and bcrypt.checkpw(password.encode('utf-8'), user[3].encode('utf-8')):
            session['user_id'] = user[0]
            return redirect(url_for('dashboard'))
        else:
            flash("Login failed. Please check your email and password")
            return redirect(url_for('login'))

    return render_template('login.html', form=form)

@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        user_id = session['user_id']

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users where id=%s", (user_id,))
        user = cursor.fetchone()
        cursor.close()

        if user:
            return render_template('dashboard.html', user=user)

    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash("You have been logged out successfully.")
    return redirect(url_for('login'))

@app.route('/add_promotion', methods=['POST'])
def add_promotion():
    data = request.json
    title = data.get('title')
    code = data.get('code')
    from_date = data.get('from_date')
    to_date = data.get('to_date')
    percentage = data.get('percentage')

    if not title or not code or not from_date or not to_date or not percentage:
        return jsonify({'error': 'All fields are required.'}), 400

    new_promotion = Promotion(
        title=title,
        code=code,
        from_date=from_date,
        to_date=to_date,
        percentage=percentage
    )
    db.session.add(new_promotion)
    db.session.commit()

    return jsonify({'message': 'Promotion added successfully.'})

@app.route('/promotions')
def get_promotions():
    promotions = Promotion.query.all()
    promotion_list = []
    for promo in promotions:
        promotion_list.append({
            'title': promo.title,
            'code': promo.code,
            'from_date': promo.from_date,
            'to_date': promo.to_date,
            'percentage': promo.percentage
        })
    return jsonify({'promotions': promotion_list})

@app.route('/promotions/current_month')
def get_current_month_promotions():
    today = date.today()
    first_day = today.replace(day=1)
    next_month = today.replace(day=28) + timedelta(days=4)
    last_day = next_month.replace(day=1) - timedelta(days=1)

    promotions = Promotion.query.filter(
        Promotion.from_date >= first_day,
        Promotion.to_date <= last_day
    ).all()

    promotion_list = []
    for promo in promotions:
        promotion_list.append({
            'title': promo.title,
            'code': promo.code,
            'from_date': promo.from_date,
            'to_date': promo.to_date,
            'percentage': promo.percentage
        })
    return jsonify({'promotions': promotion_list})

@app.route('/view_promotions')
def view_promotions():
    today = date.today()
    first_day = today.replace(day=1)
    next_month = today.replace(day=28) + timedelta(days=4)
    last_day = next_month.replace(day=1) - timedelta(days=1)

    promotions = Promotion.query.filter(
        Promotion.from_date >= first_day,
        Promotion.to_date <= last_day
    ).all()

    return render_template('view_promotions.html', promotions=promotions)

@app.route('/delete_promotion/<string:code>', methods=['DELETE'])
def delete_promotion(code):
    promotion = Promotion.query.filter_by(code=code).first_or_404()
    db.session.delete(promotion)
    db.session.commit()
    return jsonify({'message': 'Promotion deleted successfully.'})

@app.route('/modify_promotion/<string:code>', methods=['PUT'])
def modify_promotion(code):
    data = request.json
    promotion = Promotion.query.filter_by(code=code).first_or_404()

    title = data.get('title')
    from_date = data.get('from_date')
    to_date = data.get('to_date')
    percentage = data.get('percentage')

    if not title or not from_date or not to_date or not percentage:
        return jsonify({'error': 'All fields are required.'}), 400

    promotion.title = title
    promotion.from_date = from_date
    promotion.to_date = to_date
    promotion.percentage = percentage

    db.session.commit()
    return jsonify({'message': 'Promotion modified successfully.'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
