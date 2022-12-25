from sqlalchemy import Column, Integer, DateTime, func, Float, String

from src.config.database import Base


class Patient(Base):
    __tablename__ = "patients"

    internal_id = Column(Integer, primary_key=True, index=True)
    id = Column(Integer, nullable=False)
    age = Column(Integer, nullable=False)

    def __repr__(self):
        return f"Patient(internal_id={self.internal_id}, id={self.id}, age={self.age})"


class Admission(Base):
    __tablename__ = "admissions"

    internal_id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, nullable=False)
    date_admission = Column(DateTime, nullable=False)
    date_discharge = Column(DateTime, nullable=True)


class ReadmissionPrediction(Base):
    __tablename__ = "readmission_predictions"

    internal_id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, nullable=False)
    time_created = Column(DateTime(timezone=True), nullable=False)
    probability = Column(Float, nullable=False)


class Measurement(Base):
    __tablename__ = "measurements"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, nullable=False)
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    type = Column(String, nullable=False)
    value = Column(Float, nullable=False)
