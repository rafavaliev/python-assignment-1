import datetime

from src import schemas, models
from src.measurements.prediction_model import ReadmissionPredictionModel
from src.measurements.repository import MeasurementRepository
from src.patient.exceptions import PatientNotFoundException
from src.patient.repository import PatientRepository


def get_timestamp_from_date_and_hour(day: str, hour: int) -> datetime.datetime:
    t: datetime.datetime = datetime.datetime.strptime(day, '%Y-%m-%d')

    return t + datetime.timedelta(hours=hour)


class MeasurementService:

    def __init__(self,
                 patient_repo: PatientRepository,
                 measurement_repo: MeasurementRepository,
                 prediction_model: ReadmissionPredictionModel,
                 ):
        self.patient_repo = patient_repo
        self.measurement_repo = measurement_repo
        self.prediction_model = prediction_model

    def save_measurement(self, measurement: schemas.MeasurementIn) -> None:
        # Check that patient exists
        patient = self.patient_repo.get_by_id(patient_id=measurement.patient_id)
        if not patient:
            raise PatientNotFoundException(measurement.patient_id)

        # TODO: Depending on latencies and availability requirements, this code block can be moved to a queue layer

        # Save measurement to DB
        new_measurement = models.Measurement(
            patient_id=measurement.patient_id,
            type=measurement.parameter.value,
            value=measurement.value,
            time_created=get_timestamp_from_date_and_hour(measurement.day, measurement.hour)
        )
        self.measurement_repo.save_measurement(new_measurement)

        # Calculate probability of readmission
        # TODO: we need to check patients admissions, because measurements from prev admission can impact the outcome.
        # Now we just take all data for patient and calculate the probability of readmission
        probability = self.prediction_model.calculate(patient=patient, last_measurement=new_measurement)
        prediction = models.ReadmissionPrediction(patient_id=measurement.patient_id,
                                                  time_created=new_measurement.time_created,
                                                  probability=probability)
        # Save the prediction to DB
        self.measurement_repo.save_prediction(prediction)
