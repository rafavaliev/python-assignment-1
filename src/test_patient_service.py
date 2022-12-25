from typing import List
from unittest import TestCase

import pytest
import src.schemas as schemas
import src.models as models
from src.patient.exceptions import PatientAlreadyExistsException, PatientNotFoundException
from src.patient.repository import PatientRepository
from src.patient_service import PatientService


class MockPatientRepository(PatientRepository):

    def __init__(self):
        self.patients = []
        self.admissions = []
        self.patient_counter = 0
        self.admissions_counter = 0

    def get_by_id(self, patient_id: int) -> models.Patient or None:
        return next((patient for patient in self.patients if patient.id == patient_id), None)

    def get_all(self, offset: int = 0, limit: int = 100) -> List[models.Patient]:
        return self.patients[offset:offset + limit]

    def save(self, patient: models.Patient) -> models.Patient or None:
        self.patient_counter += 1
        patient.internal_id = self.patient_counter
        self.patients.append(patient)
        return patient

    def delete(self, patient: models.Patient) -> None:
        self.patients.remove(patient)

    def save_admission(self, admission: models.Admission) -> models.Admission:
        self.admissions_counter += 1
        admission.internal_id = self.admissions_counter
        self.admissions.append(admission)
        print(vars(admission))
        return admission

    def get_all_admissions(self, patient_id: int, offset: int = 0, limit: int = 100):
        return self.admissions[offset:offset + limit]


class TestPatientService(TestCase):

    def test_get_and_save_patient(self):
        # Test non-existing patient is not returned
        svc = PatientService(patient_repo=MockPatientRepository())
        patient: schemas.PatientOut = None
        with pytest.raises(PatientNotFoundException, match='Patient 1 is not found'):
            patient = svc.get_patient(patient_id=1)
        self.assertEqual(patient, None)

        # Save patient
        p = schemas.PatientIn(id=12, age=27)
        svc.save_patient(patient=p)

        # Test saved patient is returned
        patient = svc.get_patient(patient_id=12)
        self.assertEqual(patient.id, 12)
        self.assertEqual(patient.age, 27)

        # Test existing patient is not overwritten
        p = schemas.PatientIn(id=12, age=55)

        with pytest.raises(PatientAlreadyExistsException, match='Patient 12 already exists'):
            svc.save_patient(patient=p)

    def test_get_and_save_patient_admissions(self):
        # Test non-existing admissions are not returned
        svc = PatientService(patient_repo=MockPatientRepository())
        patient: schemas.PatientOut = None
        with pytest.raises(PatientNotFoundException, match='Patient 1 is not found'):
            patient = svc.get_admissions(patient_id=1)
        self.assertEqual(patient, None)

        # Save patient
        p = schemas.PatientIn(id=12, age=27)
        svc.save_patient(patient=p)

        # Test saved admissions are returned
        adm = svc.save_admission(patient_id=12, admission=schemas.AdmissionIn(patient_id=12, date_admission="18/07/2014", date_discharge="19/07/2014"))
        adm = svc.save_admission(patient_id=12, admission=schemas.AdmissionIn(patient_id=12, date_admission="20/07/2014" ))

        admissions = svc.get_admissions(patient_id=12)
        self.assertEqual(len(admissions), 2)
