from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import validates
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Session
from argon2 import PasswordHasher, exceptions
import re
from app.db.base import Base

ph = PasswordHasher()


class Departement(Base):
    __tablename__ = "departements"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(50), unique=True, nullable=False)

    collaborateurs = relationship(
        "Collaborateur", back_populates="departement"
    )


class Collaborateur(Base):
    __tablename__ = 'collaborateurs'

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(50), nullable=False)
    prenom = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    login = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)

    # Département du collaborateur
    departement_id = Column(
        Integer, ForeignKey("departements.id"), nullable=False
    )
    departement = relationship("Departement", back_populates="collaborateurs")

    # Relation avec Client
    clients = relationship("Client", back_populates="commercial")
    evenements = relationship("Evenement", back_populates="support")

    @validates("email")
    def validate_email(self, key, value):
        if not re.match(r"[^@]+@[^@]+\.[^@]+", value):
            raise ValueError(f"Email invalide : {value}")
        return value

    @validates("login")
    def validate_login(self, key, value):
        if " " in value:
            raise ValueError("Le login ne doit pas contenir d'espaces.")
        if len(value) < 3:
            raise ValueError("Le login doit comporter au moins 3 caractères.")
        return value

    @staticmethod
    def set_password(password: str) -> str:
        """Hache un mot de passe avec Argon2."""
        return ph.hash(password)

    def verify_password(self, password: str, db: Session = None) -> bool:
        """
        Vérifie si un mot de passe correspond au hash et rehash si nécessaire.
        """
        try:
            ph.verify(self.password_hash, password)
            if ph.check_needs_rehash(self.password_hash):
                self.password_hash = ph.hash(password)
                if db:
                    db.commit()  # Sauvegarde automatique dans la DB
                print("Password hash upgraded for better security.")
            return True
        except exceptions.VerifyMismatchError:
            return False
