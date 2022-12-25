import datetime
import math

from src import models
from src.measurements.prediction_model_fast import FastReadmissionCache, FastReadmissionPredictionModel


class DummyFastReadmissionCache(FastReadmissionCache):

    def __init__(self):
        self._cache = {}

    def get_last_blood_pressure(self, patient_id: int) -> models.Measurement:
        key = f'patient:{patient_id}:last_blood_pressure'
        return self._cache.get(key)

    def save_last_blood_pressure(self, patient_id: int, measurement: models.Measurement):
        key = f'patient:{patient_id}:last_blood_pressure'
        self._cache[key] = measurement

    def get_mean_respiratory_rate(self, patient_id: int) -> (float, int):
        key = f'patient:{patient_id}:mean_respiratory_rate'
        val = self._cache.get(key)
        if val is None:
            return 0.0, 0
        return val['mean'], val['count']

    def save_mean_respiratory_rate(self, patient_id: int, mean: float, count: int) -> (float, int):
        key = f'patient:{patient_id}:mean_respiratory_rate'
        self._cache[key] = {'mean': mean, 'count': count}

    def get_standard_deviation_temperature(self, patient_id: int) -> (float, float, int):
        key = f'patient:{patient_id}:standard_deviation_temperature'
        val = self._cache.get(key)
        if val is None:
            return 0.0, 0.0, 0
        return val['mean'], val['variance'], val['count']

    def save_standard_deviation_temperature(self, patient_id: int, mean: float, variance: float, count: int):
        # print({'mean': mean, 'variance': variance, 'count': count})
        key = f'patient:{patient_id}:standard_deviation_temperature'
        self._cache[key] = {'mean': mean, 'variance': variance, 'count': int(count)}


def test_fast_model():
    test_cache = DummyFastReadmissionCache()
    model = FastReadmissionPredictionModel(cache=test_cache)

    p = models.Patient(id=1, age=50)

    # first measurement that's not in the formula
    prob = model.calculate(patient=p, last_measurement=models.Measurement(
        id=1,
        patient_id=1,
        time_created=datetime.datetime.now(),
        type="heart_rate",
        value=80,
    ))

    assert 0.007391541344281971 == prob

    # second measurement with mean value
    for i in range(10, 31):
        prob = model.calculate(patient=p, last_measurement=models.Measurement(
            id=1,
            patient_id=1,
            time_created=datetime.datetime.now(),
            type="respiration_rate",
            value=float(i),
        ))
    (mean, count) = test_cache.get_mean_respiratory_rate(1)
    assert 20.0 == mean
    assert 21 == count
    assert 0.013386917827664766 == prob

    # 3rd measurement with standard deviation
    for i in range(0, 100):
        temperature = 36 + i / 10 % 4
        prob = model.calculate(patient=p, last_measurement=models.Measurement(
            id=1,
            patient_id=1,
            time_created=datetime.datetime.now(),
            type="temperature",
            value=float(temperature),
        ))
    (mean, variance, count) = test_cache.get_standard_deviation_temperature(1)
    assert 100 == int(count)
    assert 37.74999999999998 == mean
    assert 129.25000000000077 == variance
    standard_deviation = math.sqrt(variance / count - 1)
    assert 0.5408326913196055 == standard_deviation
    assert 0.013692123437114881 == prob

    # 4th value with the latest blood pressure
    prob_with_latest_value = model.calculate(patient=p, last_measurement=models.Measurement(
        id=1,
        patient_id=1,
        time_created=datetime.datetime.now(),
        type="blood_pressure",
        value=120,
    ))
    blood_pressure_1 = test_cache.get_last_blood_pressure(1)

    prob_with_old_value = model.calculate(patient=p, last_measurement=models.Measurement(
        id=2,
        patient_id=1,
        time_created=datetime.datetime.now() - datetime.timedelta(minutes=1),
        type="blood_pressure",
        value=125,
    ))
    # Even if we insert new value but with old timestamp, only the newest value should be used
    blood_pressure_2 = test_cache.get_last_blood_pressure(1)
    assert blood_pressure_1.value == 120.0
    assert blood_pressure_2.value == 120.0
    assert prob_with_latest_value == prob_with_old_value
