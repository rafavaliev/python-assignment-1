from src import models
from src.measurements.prediction_math import calculate_probability_v1, calculate_mean, calculate_standard_deviation
from src.measurements.prediction_model import ReadmissionPredictionModel
from src.measurements.repository import MeasurementRepository


class SlowReadmissionPredictionModel(ReadmissionPredictionModel):
    """
    This prediction model on each new measurement goes to the database to fetch values
        and then calculates the probability of readmission.

    It fetches from DB:
    * last blood pressure O(1) (if index is created)
    * mean respiratory rate O(n)
    * standard deviation  of temperature O(n)
    """

    def __init__(self, measurement_repo: MeasurementRepository):
        self.measurement_repo = measurement_repo

    def calculate(self, patient: models.Patient, last_measurement: models.Measurement) -> float:
        age = patient.age
        last_blood_pressure = self.get_last_blood_pressure(patient.id)
        mean_respiratory_rate = self.get_mean_respiratory_rate(patient.id)
        standard_deviation_temperature = self.get_standard_deviation_temperature(patient.id)

        prob = calculate_probability_v1(
            age=age,
            last_blood_pressure=last_blood_pressure,
            mean_respiratory_rate=mean_respiratory_rate,
            standard_deviation_temperature=standard_deviation_temperature
        )
        return prob

    def get_mean_respiratory_rate(self, patient_id: int) -> float:
        ms = self.measurement_repo.get_all_measurements(patient_id=patient_id, measurement_type="respiratory_rate",
                                                        offset=0, limit=1000)
        if not ms or len(ms) == 0:
            return 0
        values = [m.value for m in ms]

        return calculate_mean(values)

    def get_last_blood_pressure(self, patient_id: int) -> float:
        m = self.measurement_repo.get_last_measurement(patient_id=patient_id, measurement_type="blood_pressure")
        return m.value if m else 0

    def get_standard_deviation_temperature(self, patient_id: int) -> float:
        ms = self.measurement_repo.get_all_measurements(patient_id=patient_id, measurement_type="temperature",
                                                        offset=0, limit=1000)
        if not ms or len(ms) == 0:
            return 0
        values = [m.value for m in ms]

        return calculate_standard_deviation(values)
