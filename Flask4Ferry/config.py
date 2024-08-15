import os

class Config:
    # Flask secret key
    SECRET_KEY = 'ganesh'
    
    # MySQL configuration
    MYSQL_HOST = '144.24.96.48'
    MYSQL_USER = 'khhoji'
    MYSQL_PASSWORD = 'Khhoji@123'
    MYSQL_DB = 'FerryOne'
    
    # SQLAlchemy configuration
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://khhoji:Khhoji%40123@144.24.96.48:3306/FerryOne'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


