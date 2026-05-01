import os
import sys
from pathlib import Path

from dotenv import load_dotenv, find_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

env_path = Path(__file__).parent / ".env.test" if os.getenv('TESTING') == 'true' or 'pytest' in sys.argv[0] else Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)

DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')

print(f"DEBUG db_session.py: TESTING={os.getenv('TESTING')}, DB_NAME={DB_NAME}")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()