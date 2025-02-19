from sqlalchemy import Column, Integer, String, ForeignKey, Text, Date
from sqlalchemy.orm import relationship, validates
from app.db.base import Base


class Evenement(Base):
    __tablename__ = 'evenements'

    id = Column(Integer, primary_key=True, index=True)
    id_contrat = Column(Integer, ForeignKey('contrats.id'))
    id_support = Column(Integer, ForeignKey('collaborateurs.id'))
    date_debut = Column(Date, nullable=False)
    date_fin = Column(Date, nullable=False)
    lieu = Column(String(255), nullable=False)
    nombre_participants = Column(Integer, nullable=False)
    notes = Column(Text, nullable=True)

    contrat = relationship("Contrat")
    support = relationship("Collaborateur", back_populates="evenements")

    @validates("date_debut", "date_fin")
    def validate_dates(self, key, value):
        if key == "date_fin" and self.date_debut and value <= self.date_debut:
            raise ValueError(
                "La date de fin doit être postérieure à la date de début."
            )
        return value

    @validates("lieu")
    def validate_lieu(self, key, value):
        if not value.strip():
            raise ValueError("Le lieu ne peut pas être vide.")
        return value

    @validates("nombre_participants")
    def validate_nombre_participants(self, key, value):
        if value < 1:
            raise ValueError("Le nombre de participants doit être au moins 1.")
        return value
