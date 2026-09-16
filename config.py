class Config:
    SECRET_KEY = 'change-this-to-something-random-later'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@localhost/bike_marketplace_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
