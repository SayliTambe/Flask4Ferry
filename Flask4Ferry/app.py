from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, ValidationError
import bcrypt
from flask_mysqldb import MySQL
from flask_sqlalchemy import SQLAlchemy
from datetime import date, datetime, timedelta

# Import configuration
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# MySQL Configuration for user authentication
mysql = MySQL(app)

# SQLAlchemy Configuration for promotion management
db = SQLAlchemy(app)

class RegisterForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Register")

    def validate_email(self, field):
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE email=%s", (field.data,))
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
    promo_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    promo_title = db.Column(db.String(45), nullable=True)
    promo_code = db.Column(db.String(45), unique=True, nullable=True)
    promo_startdt = db.Column(db.String(45), nullable=False)
    promo_enddt = db.Column(db.String(45), nullable=False)
    promodisc_amt = db.Column(db.Float, nullable=False)

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
        cursor.execute("SELECT * FROM users WHERE id=%s", (user_id,))
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
    start_date = data.get('from_date')
    end_date = data.get('to_date')
    discount_amount = data.get('percentage')

    if not title or not code or not start_date or not end_date or not discount_amount:
        return jsonify({'error': 'All fields are required.'}), 400

    new_promotion = Promotion(
        promo_title=title,
        promo_code=code,
        promo_startdt=start_date,
        promo_enddt=end_date,
        promodisc_amt=discount_amount
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
            'title': promo.promo_title,
            'code': promo.promo_code,
            'from_date': promo.promo_startdt,
            'to_date': promo.promo_enddt,
            'percentage': promo.promodisc_amt
        })
    return jsonify({'promotions': promotion_list})

@app.route('/promotions/current_month')
def get_current_month_promotions():
    today = date.today()
    first_day = today.replace(day=1)
    next_month = today.replace(day=28) + timedelta(days=4)
    last_day = next_month.replace(day=1) - timedelta(days=1)

    promotions = Promotion.query.filter(
        Promotion.promo_startdt >= first_day,
        Promotion.promo_enddt <= last_day
    ).all()

    promotion_list = []
    for promo in promotions:
        promotion_list.append({
            'title': promo.promo_title,
            'code': promo.promo_code,
            'from_date': promo.promo_startdt,
            'to_date': promo.promo_enddt,
            'percentage': promo.promodisc_amt
        })
    return jsonify({'promotions': promotion_list})

@app.route('/view_promotions')
def view_promotions():
    today = datetime.now().date()

    # Filter promotions based on the current date
    promotions = Promotion.query.filter(
        Promotion.promo_startdt <= today,
        Promotion.promo_enddt >= today
    ).all()

    return render_template('veiw_promotions.html', promotions=promotions)

@app.route('/delete_promotion/<string:code>', methods=['DELETE'])
def delete_promotion(code):
    promotion = Promotion.query.filter_by(promo_code=code).first_or_404()
    db.session.delete(promotion)
    db.session.commit()
    return jsonify({'message': 'Promotion deleted successfully.'})

@app.route('/modify_promotion/<string:code>', methods=['PUT'])
def modify_promotion(code):
    data = request.json
    promotion = Promotion.query.filter_by(promo_code=code).first_or_404()

    title = data.get('title')
    start_date = data.get('from_date')
    end_date = data.get('to_date')
    discount_amount = data.get('percentage')

    if not title or not start_date or not end_date or not discount_amount:
        return jsonify({'error': 'All fields are required.'}), 400

    promotion.promo_title = title
    promotion.promo_startdt = start_date
    promotion.promo_enddt = end_date
    promotion.promodisc_amt = discount_amount

    db.session.commit()
    return jsonify({'message': 'Promotion modified successfully.'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
