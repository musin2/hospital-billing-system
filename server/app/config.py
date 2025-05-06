import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DEVELOPMENT_DATABASE_URI")
    if not SQLALCHEMY_DATABASE_URI:
        raise ValueError("The environment variable 'DEVELOPMENT_DATABASE_URI' is not set")
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY")  #Get secret key from .env file