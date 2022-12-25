from abc import ABCMeta, abstractmethod
from typing import List

from sqlalchemy.orm import Session

from src import models
from src.models import Admission


class MeasurementRepository(metaclass=ABCMeta):

    @abstractmethod
    def save_measurement(self, measurement: models.Measurement) -> models.Measurement:
        pass

    @abstractmethod
    def save_prediction(self, prediction: models.ReadmissionPrediction) -> models.ReadmissionPrediction:
        pass

    @abstractmethod
    def get_all_measurements(self, patient_id: int, measurement_type: str, offset: int = 0, limit: int = 100) -> List[
        models.Measurement]:
        pass

    @abstractmethod
    def get_all_predictions(self, patient_id: int, offset: int = 0, limit: int = 100) -> List[
        models.ReadmissionPrediction]:
        pass

    @abstractmethod
    def get_last_measurement(self, patient_id: int, measurement_type: str) -> models.Measurement:
        pass


class MeasurementSQLiteRepository(MeasurementRepository):

    def __init__(self, db_session):
        self.db: Session = db_session

    def save_measurement(self, measurement: models.Measurement) -> models.Measurement:
        self.db.add(measurement)
        self.db.commit()
        self.db.refresh(measurement)
        return measurement

    def save_prediction(self, prediction: models.ReadmissionPrediction) -> models.ReadmissionPrediction:
        self.db.add(prediction)
        self.db.commit()
        self.db.refresh(prediction)
        return prediction

    def get_all_measurements(self, patient_id: int, measurement_type: str, offset: int = 0, limit: int = 100) -> List[
        models.Measurement]:
        if not measurement_type:
            return self.db.query(models.Measurement).filter(models.Measurement.patient_id == patient_id).order_by(
                models.Measurement.time_created.desc()).offset(offset).limit(limit).all()
        return self.db.query(models.Measurement).filter(models.Measurement.patient_id == patient_id,
                                                        models.Measurement.type == measurement_type).order_by(
            models.Measurement.time_created.desc()).offset(offset).limit(limit).all()

    def get_last_measurement(self, patient_id: int, measurement_type: str) -> models.Measurement:
        if not measurement_type:
            return self.db.query(models.Measurement).filter(models.Measurement.patient_id == patient_id).order_by(
                models.Measurement.time_created).first()
        return self.db.query(models.Measurement).filter(models.Measurement.patient_id == patient_id,
                                                        models.Measurement.type == measurement_type).order_by(
            models.Measurement.time_created.desc()).first()

    def get_all_predictions(self, patient_id: int, offset: int = 0, limit: int = 100) -> List[
        models.ReadmissionPrediction]:
        return self.db.query(models.ReadmissionPrediction).filter(
            models.ReadmissionPrediction.patient_id == patient_id).order_by(
            models.ReadmissionPrediction.time_created.desc()).offset(offset).limit(
            limit).all()
