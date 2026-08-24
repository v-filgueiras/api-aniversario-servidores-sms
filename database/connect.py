from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Adicionado .rvfwutfabnfcgwhdylqo no usuario para autenticar no Supavisor
DATABASE_URL = "postgresql://postgres.rvfwutfabnfcgwhdylqo:emeOw8aXIFB7tx79@aws-1-sa-east-1.pooler.supabase.com:6543/postgres?sslmode=require"

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Testa a conexão antes de usar para evitar desconexões
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()