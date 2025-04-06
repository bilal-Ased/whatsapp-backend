# models.py
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()

class Contact(Base):
    __tablename__ = "contacts"
    id = Column(Integer, primary_key=True)
    phone_number = Column(String(20), unique=True, nullable=False)
    name = Column(String(100))
    email = Column(String(200), unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    messages = relationship("WhatsappMessage", back_populates="contact")


class WhatsappMessage(Base):
    __tablename__ = "whatsapp_messages"
    id = Column(Integer, primary_key=True)
    contact_id = Column(Integer, ForeignKey("contacts.id", ondelete="CASCADE"))
    message_id = Column(String(100), unique=True, nullable=False)
    direction = Column(Enum("incoming", "outgoing", name="message_direction"), nullable=False)
    message_body = Column(Text)
    type = Column(String(20), default="text")
    sent_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

    contact = relationship("Contact", back_populates="messages")
