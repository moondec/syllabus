from sqlalchemy import Column, Integer, String, JSON, DateTime
from sqlalchemy.sql import func
from database import Base

class Syllabus(Base):
    __tablename__ = "syllabuses"

    id = Column(Integer, primary_key=True, index=True)
    subject_name = Column(String, index=True)
    field_of_study = Column(String)
    level = Column(String)
    semester = Column(String)
    legal_basis = Column(String, default="Uchwała nr 27/2025 Senatu Uniwersytetu Przyrodniczego w Poznaniu z dnia 26 marca 2025 roku")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
    data = Column(JSON) # Stores the full dictionary of syllabus fields

    def to_dict(self):
        return {
            "id": self.id,
            "subject_name": self.subject_name,
            "field_of_study": self.field_of_study,
            "level": self.level,
            "semester": self.semester,
            "legal_basis": self.legal_basis,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "data": self.data
        }
