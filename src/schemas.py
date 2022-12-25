import datetime
from enum import Enum
from typing import Union

from pydantic import BaseModel, Field


class PatientIn(BaseModel):
    id: int = Field(gte=0, description="The ID of the patient in the hospital", example=42)
    age: int = Field(gte=0, description="Age of the patient", example=26)


class PatientOut(BaseModel):
    id: int = Field(description="The ID of the patient in the hospital", example=42)
    age: int = Field(description="Age of the patient", example=26)

    class Config:
        orm_mode = True


class ReadmissionProbabilityOut(BaseModel):
    patient_id: int = Field(description="The ID of the patient in the hospital", example=42)
    time_created: datetime.datetime = Field( description="The timestamp of the prediction", example="2021-01-01T00:00:00Z")
    probability: float = Field(description="The probability of readmission", example=0.44)

    class Config:
        orm_mode = True


class AdmissionIn(BaseModel):
    patient_id: int = Field(gte=0, description="The ID of the patient in the hospital", example=42)
    date_admission: str = Field(description="The date the patient is admitted to the IC", example="18/07/2014")
    date_discharge: Union[str, None] = Field(description="The date the patient is discharged from the IC", example="19/07/2014")


class AdmissionOut(BaseModel):
    patient_id: int = Field(gte=0, description="The ID of the patient in the hospital", example=42)
    date_admission: datetime.date = Field(description="The date the patient is admitted to the IC")
    date_discharge: Union[datetime.date, None] = Field(description="The date the patient is discharged from the IC")

    class Config:
        orm_mode = True


class MeasurementType(str, Enum):
    BLOOD_PRESSURE: str = "blood_pressure"
    RESPIRATION_RATE: str = "respiration_rate"
    TEMPERATURE: str = "temperature"
    HEART_RATE: str = "heart_rate"


class MeasurementIn(BaseModel):
    patient_id: int = Field(gte=0, description="The ID of the patient in the hospital", example=42)
    day: str = Field(description="The date of the measurement", example="2021-01-01")
    hour: int = Field(gte=0, lte=24, description="The hour of the measurement", example=7)
    parameter: MeasurementType = Field(description="The type of the measurement", example="blood_pressure")
    value: float = Field(gte=0.0, description="Measurement value", example=120.0)


class MeasurementOut(BaseModel):
    id: int = Field(description="The ID of the measurement", example=12)
    patient_id: int = Field(description="The ID of the patient in the hospital", example=42)
    time_created: datetime.datetime = Field(description="The timestamp of the measurement", example="2021-01-01T00:00:00Z")
    type: MeasurementType = Field(description="The parameter of the measurement", example="blood_pressure")
    value: float = Field(description="Measurement value", example=120.0)

    class Config:
        orm_mode = True
