from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, ForeignKey, DateTime, Text
import datetime

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    telegram_id: Mapped[int] = mapped_column(Integer, unique=True)
    language: Mapped[str] = mapped_column(String(10))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)

class Resume(Base):
    __tablename__ = "resumes"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    full_name: Mapped[str] = mapped_column(String(255))
    position: Mapped[str] = mapped_column(String(255))
    birth_date: Mapped[str] = mapped_column(String(50))
    phone: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(255))
    address: Mapped[str] = mapped_column(Text)
    education: Mapped[str] = mapped_column(Text)
    experience: Mapped[str] = mapped_column(Text)
    skills: Mapped[str] = mapped_column(Text)
    languages: Mapped[str] = mapped_column(Text)
    certificates: Mapped[str] = mapped_column(Text, nullable=True)
    additional_info: Mapped[str] = mapped_column(Text, nullable=True)
    photo_path: Mapped[str] = mapped_column(String(255), nullable=True)
    template: Mapped[str] = mapped_column(String(50))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)

class GeneratedFile(Base):
    __tablename__ = "generated_files"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    resume_id: Mapped[int] = mapped_column(ForeignKey("resumes.id"))
    file_path: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)

class BroadcastLog(Base):
    __tablename__ = "broadcast_logs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    message: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(50))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)