from abc import ABCMeta, abstractmethod

import redis as redis

import math

from src import models
from src.measurements.prediction_math import calculate_mean_and_variance_online, calculate_mean_online, \
    calculate_probability_v1
from src.measurements.prediction_model import ReadmissionPredictionModel
from src.schemas import MeasurementType


class FastReadmissionCache(metaclass=ABCMeta):
    """
    Cache saves data necessary for fast readmission prediction model.
    """

    @abstractmethod
    def get_last_blood_pressure(self, patient_id: int) -> models.Measurement:
        pass

    @abstractmethod
    def save_last_blood_pressure(self, patient_id: int, measurement: models.Measurement):
        pass

    @abstractmethod
    def get_mean_respiratory_rate(self, patient_id: int) -> (float, int):
        pass

    @abstractmethod
    def save_mean_respiratory_rate(self, patient_id: int, mean: float, count: int):
        pass

    @abstractmethod
    def get_standard_deviation_temperature(self, patient_id: int) -> (float, float, int):
        pass

    @abstractmethod
    def save_standard_deviation_temperature(self, patient_id: int, mean: float, variance: float, count: int):
        pass


class FastReadmissionPredictionModel(ReadmissionPredictionModel):
    """
    This prediction model on each new measurement goes to the cache and
    calculates the probability of readmission only for the new increment, so it's always O(1) for each new request

    It fetches from cache:
    * last blood pressure O(1)
    * mean and count for respiratory rate calculation O(1)
    * mean, variance and count for standard deviation calculation of temperature O(1)
    """

    def __init__(self, cache: FastReadmissionCache):
        self.cache = cache

    def calculate(self, patient: models.Patient, last_measurement: models.Measurement) -> float:
        """
        We calculate the probability only using the latest increment and the cached data.
        TODO: If cache down, we should fallback to SlowReadmissionPredictionModel
        """
        age = patient.age
        last_blood_pressure = self.get_last_blood_pressure(patient.id, last_measurement)
        mean_respiratory_rate = self.get_mean_respiratory_rate(patient.id, last_measurement)
        standard_deviation_temperature = self.get_standard_deviation_temperature(patient.id, last_measurement)

        prob = calculate_probability_v1(
            age=age,
            last_blood_pressure=last_blood_pressure,
            mean_respiratory_rate=mean_respiratory_rate,
            standard_deviation_temperature=standard_deviation_temperature
        )
        return prob

    def get_last_blood_pressure(self, patient_id: int, last_measurement: models.Measurement) -> float:
        """
        Returns the last blood pressure measurement(that one in cache or the new one)
        """
        last_cached_blood_pressure = self.cache.get_last_blood_pressure(patient_id)
        if last_measurement.type != MeasurementType.BLOOD_PRESSURE:
            if not last_cached_blood_pressure:
                return 0.0
            return last_cached_blood_pressure.value

        # If there is nothing in cache, save and return new value
        if not last_cached_blood_pressure:
            self.cache.save_last_blood_pressure(patient_id, last_measurement)
            return last_measurement.value

        # If somehow cached value is newer than the last measurement, use it
        if last_cached_blood_pressure.time_created > last_measurement.time_created:
            return last_cached_blood_pressure.value
        self.cache.save_last_blood_pressure(patient_id, last_measurement)
        return last_measurement.value

    def get_mean_respiratory_rate(self, patient_id: int, last_measurement: models.Measurement) -> float:
        # Calculate mean value of respiratory rate
        # IF there is nothing in cache, mean and count are 0s
        (mean, count) = self.cache.get_mean_respiratory_rate(patient_id)
        if last_measurement.type != MeasurementType.RESPIRATION_RATE:
            return mean
        (new_mean, new_count) = calculate_mean_online(mean, count, last_measurement.value)
        self.cache.save_mean_respiratory_rate(patient_id, new_mean, new_count)
        return new_mean

    def get_standard_deviation_temperature(self, patient_id: int, last_measurement: models.Measurement) -> float:
        (mean, variation, count) = self.cache.get_standard_deviation_temperature(patient_id)
        if last_measurement.type != MeasurementType.TEMPERATURE:
            return math.sqrt(variation / (count - 1)) if count > 1 else 0

        (new_mean, new_variation, new_count) = calculate_mean_and_variance_online(mean, variation, count,
                                                                                  last_measurement.value)
        self.cache.save_standard_deviation_temperature(patient_id, new_mean, new_variation, new_count)
        return math.sqrt(new_variation / (new_count - 1)) if count > 1 else 0
