from abc import ABCMeta, abstractmethod

from src import models


class ReadmissionPredictionModel(metaclass=ABCMeta):
    """
        Prediction model calculates the probability of readmission for a patient.
    """

    @abstractmethod
    def calculate(self, patient: models.Patient, last_measurement: models.Measurement) -> float:
        """
        Calculates the probability of readmission for a patient.

        It uses statis data of a patient and a new measurement.
        Depending on a model, other data can be used.
        """
        pass
