from sqlalchemy import Column, Integer, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship, validates
from datetime import datetime
from app.db.base import Base


class Contrat(Base):
    __tablename__ = 'contrats'

    id = Column(Integer, primary_key=True, index=True)
    id_client = Column(Integer, ForeignKey('clients.id'))
    montant_total = Column(Float, nullable=False)
    montant_restant = Column(Float, nullable=False)
    date_creation = Column(DateTime, default=datetime.now)
    statut = Column(Boolean, default=False)
    client = relationship("Client", back_populates="contrats")

    @validates("montant_total")
    def validate_montant_total(self, key, value):
        if value < 0:
            raise ValueError("Le montant total doit être positif.")
        return value

    @validates("montant_restant")
    def validate_montant_restant(self, key, value):
        if value < 0:
            raise ValueError("Le montant restant doit être positif.")
        if value > self.montant_total:
            raise ValueError(
                "Le montant restant ne peut pas dépasser le montant total."
            )
        return value
