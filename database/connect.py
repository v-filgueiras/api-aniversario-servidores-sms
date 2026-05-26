from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


DATABASE_URL = (
    "postgresql://postgres.rvfwutfabnfcgwhdylqo:emeOw8aXIFB7tx79@aws-1-sa-east-1.pooler.supabase.com:6543/postgres?sslmode=require"
)

engine = create_engine(
    DATABASE_URL
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()