import pickle

import redis

from src import models
from src.measurements.prediction_model_fast import FastReadmissionCache


class FastReadmissionRedisCache(FastReadmissionCache):

    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client

    def get_last_blood_pressure(self, patient_id: int) -> models.Measurement:
        key = f'patient:{patient_id}:last_blood_pressure'
        read = self.redis_client.get(key)
        if not read:
            return None
        m = pickle.loads(read)
        return m

    def save_last_blood_pressure(self, patient_id: int, measurement: models.Measurement):
        key = f'patient:{patient_id}:last_blood_pressure'
        self.redis_client.set(key, pickle.dumps(measurement))

    def get_mean_respiratory_rate(self, patient_id: int) -> (float, int):
        key = f'patient:{patient_id}:mean_respiratory_rate'
        val = self.redis_client.get(key)
        if not val:
            return 0.0, 0
        read = pickle.loads(val)
        return read['mean'], read['count']

    def save_mean_respiratory_rate(self, patient_id: int, mean: float, count: int) -> (float, int):
        key = f'patient:{patient_id}:mean_respiratory_rate'
        self.redis_client.set(key, pickle.dumps({'mean': mean, 'count': count}))

    def get_standard_deviation_temperature(self, patient_id: int) -> (float, float, int):
        key = f'patient:{patient_id}:standard_deviation_temperature'
        val = self.redis_client.get(key)
        if not val:
            return 0.0, 0.0, 0
        read = pickle.loads(val)
        return read['mean'], read['variance'], read['count']

    def save_standard_deviation_temperature(self, patient_id: int, mean: float, variance: float, count: int):
        key = f'patient:{patient_id}:standard_deviation_temperature'
        self.redis_client.set(key, pickle.dumps({'mean': mean, 'variance': variance, 'count': int(count)}))
