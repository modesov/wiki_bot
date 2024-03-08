from sqlalchemy import BigInteger, String, DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB


class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())


class User(Base):
    __tablename__ = 'users'

    tg_id: Mapped[int] = mapped_column(BigInteger, nullable=False, unique=True)
    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    data: Mapped[str] = mapped_column(JSONB, nullable=False)


class Phrase(Base):
    __tablename__ = 'phrases'
    phrase: Mapped[str] = mapped_column(String(500), nullable=False, unique=True)


class UserPhrase(Base):
    __tablename__ = 'user_phrases'

    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    phrase_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
