from datetime import datetime
from typing import List

from src import models, schemas
from src.patient.exceptions import PatientAlreadyExistsException, PatientNotFoundException
from src.patient.repository import PatientRepository
from src.schemas import PatientOut


class PatientService:

    def __init__(self, patient_repo: PatientRepository):
        self.patient_repo = patient_repo

    def get_patient(self, patient_id: int) -> PatientOut or None:
        patient = self.patient_repo.get_by_id(patient_id=patient_id)
        if not patient:
            raise PatientNotFoundException(patient_id)

        return PatientOut.from_orm(patient)

    def get_patients(self, offset: int = 0, limit: int = 100) -> List[PatientOut]:
        patients = self.patient_repo.get_all(offset=offset, limit=limit)
        return [PatientOut.from_orm(patient) for patient in patients if patient.id > 0]

    def save_patient(self, patient: schemas.PatientIn) -> PatientOut:
        try:
            p = self.get_patient(patient_id=patient.id)
            if p:
                raise PatientAlreadyExistsException(patient.id)
        except PatientNotFoundException:
            pass
        patient = models.Patient(**patient.dict())
        patient = self.patient_repo.save(patient=patient)
        return PatientOut.from_orm(patient)

    def save_admission(self, patient_id: int, admission: schemas.AdmissionIn) -> schemas.AdmissionOut:
        """
        Add an admission of a patient
        :param patient_id:
        :param admission:
        :return:
        """
        patient = self.patient_repo.get_by_id(patient_id=patient_id)
        if not patient:
            raise PatientNotFoundException(patient_id)

        adm_db = models.Admission()
        adm_db.patient_id = patient_id
        adm_db.date_admission = datetime.strptime(admission.date_admission, '%d/%m/%Y').date()
        if admission.date_discharge:
            adm_db.date_discharge = datetime.strptime(admission.date_discharge, '%d/%m/%Y').date()

        adm = self.patient_repo.save_admission(admission=adm_db)
        return schemas.AdmissionOut.from_orm(adm)

    def get_admissions(self, patient_id: int, offset: int = 0, limit: int = 100) -> List[schemas.AdmissionOut]:
        patient = self.patient_repo.get_by_id(patient_id=patient_id)
        if not patient:
            raise PatientNotFoundException(patient_id)

        admissions = self.patient_repo.get_all_admissions(patient_id=patient_id, offset=offset, limit=limit)
        return [schemas.AdmissionOut.from_orm(adm) for adm in admissions]
