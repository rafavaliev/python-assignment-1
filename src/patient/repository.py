from abc import ABCMeta, abstractmethod
from typing import List

from sqlalchemy.orm import Session

from src import models
from src.models import Admission


class PatientRepository(metaclass=ABCMeta):

    @abstractmethod
    def get_by_id(self, patient_id: int) -> models.Patient or None:
        pass

    @abstractmethod
    def get_all(self, offset: int = 0, limit: int = 100) -> List[models.Patient]:
        pass

    @abstractmethod
    def save(self, patient: models.Patient) -> models.Patient:
        pass

    @abstractmethod
    def delete(self, patient: models.Patient) -> None:
        pass

    @abstractmethod
    def save_admission(self, admission: models.Admission) -> models.Admission:
        pass

    @abstractmethod
    def get_all_admissions(self, patient_id: int, offset: int = 0, limit: int = 100):
        pass


class PatientSQLiteRepository(PatientRepository):

    def __init__(self, db_session):
        self.db: Session = db_session

    def get_by_id(self, patient_id: int) -> models.Patient or None:
        return self.db.query(models.Patient).filter(models.Patient.id == patient_id).first()

    def get_all(self, offset: int = 0, limit: int = 100) -> List[models.Patient]:
        return self.db.query(models.Patient).filter(models.Patient.id is not None).offset(offset).limit(limit).all()

    def save(self, patient: models.Patient) -> models.Patient or None:
        self.db.add(patient)
        self.db.commit()
        self.db.refresh(patient)
        return patient

    def delete(self, patient: models.Patient) -> None:
        self.db.delete(patient)
        self.db.commit()

    def save_admission(self, admission: models.Admission) -> models.Admission:
        self.db.add(admission)
        self.db.commit()
        self.db.refresh(admission)
        return admission

    def get_all_admissions(self, patient_id: int, offset: int = 0, limit: int = 100):
        return self.db.query(models.Admission) \
            .filter(models.Admission.patient_id == patient_id) \
            .offset(offset).limit(limit).all()
