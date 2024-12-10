from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship, validates
from datetime import datetime, timezone
from app.db.base import Base
import re


class Client(Base):
    __tablename__ = 'clients'

    id = Column(Integer, primary_key=True, index=True)
    nom_complet = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    telephone = Column(String(20), nullable=True)
    nom_entreprise = Column(String(100), nullable=True)
    date_creation = Column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    date_derniere_mise_a_jour = Column(
        DateTime, default=datetime.now, onupdate=datetime.now
    )
    id_commercial = Column(Integer, ForeignKey('collaborateurs.id'))
    commercial = relationship("Collaborateur", back_populates="clients")
    contrats = relationship("Contrat", back_populates="client")

    @validates("email")
    def validate_email(self, key, value):
        if not re.match(r"[^@]+@[^@]+\.[^@]+", value):
            raise ValueError(f"Email invalide : {value}")
        return value

    @validates("nom_complet")
    def validate_nom_complet(self, key, value):
        if not value.strip():
            raise ValueError("Le nom complet ne peut pas être vide.")
        return value
