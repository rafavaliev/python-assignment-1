import redis
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.config.cache import get_cache
from src.config.database import create_tables, get_db
from src.dependencies import PaginationParams, PaginationResponse
from src.measurements.cache import FastReadmissionRedisCache
from src.measurements.prediction_model_fast import FastReadmissionPredictionModel
from src.measurements.prediction_model_slow import SlowReadmissionPredictionModel
from src.measurements.repository import MeasurementSQLiteRepository
from src.measurement_service import MeasurementService
from src.patient.exceptions import PatientNotFoundException, PatientAlreadyExistsException
from src.patient.repository import PatientSQLiteRepository

from src.patient_service import PatientService
from src.schemas import MeasurementIn, ReadmissionProbabilityOut, MeasurementOut, MeasurementType, PatientOut, \
    AdmissionOut, AdmissionIn, PatientIn

from starlette_prometheus import metrics, PrometheusMiddleware

app = FastAPI(
    responses={404: {"description": "Not found"}},
)
app.add_middleware(PrometheusMiddleware)
app.add_route("/metrics", metrics)

# Create tables in the local SQLite database if they don't exist
create_tables()


# TODO: SSL/HTTPS is not set up
# TODO: Authentication is not set up. We assume that only 1 hospital uses our service, so patient_id is unique only under this hospital.

# Example of slow endpoint
@app.post("/v0/measurements", response_model=None, status_code=status.HTTP_201_CREATED)
def handle_measurement(m: MeasurementIn, db: Session = Depends(get_db)):
    """
        Save a measurement to the database and calculate the probability of readmission based on data in the database.
    """
    measurement_service = MeasurementService(
        patient_repo=PatientSQLiteRepository(db),
        measurement_repo=MeasurementSQLiteRepository(db),
        prediction_model=SlowReadmissionPredictionModel(measurement_repo=MeasurementSQLiteRepository(db)),
    )
    try:
        measurement_service.save_measurement(measurement=m)
    except PatientNotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Patient {m.patient_id} not found")
    return


@app.post("/v1/measurements", response_model=None, status_code=status.HTTP_201_CREATED)
def handle_measurement(m: MeasurementIn,
                       db: Session = Depends(get_db),
                       cache: redis.Redis = Depends(get_cache)
                       ):
    """
    Save a measurement to the database and calculate the probability of readmission based on data in the cache.
    """
    measurement_service = MeasurementService(
        patient_repo=PatientSQLiteRepository(db),
        measurement_repo=MeasurementSQLiteRepository(db),
        prediction_model=FastReadmissionPredictionModel(cache=FastReadmissionRedisCache(redis_client=cache)),
    )
    try:
        measurement_service.save_measurement(measurement=m)
    except PatientNotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Patient {m.patient_id} not found")
    return


@app.post("/v1/patients/", response_model=PatientOut, status_code=status.HTTP_201_CREATED)
def save_patient(p: PatientIn,
                 db: Session = Depends(get_db)):
    svc = PatientService(patient_repo=PatientSQLiteRepository(db))
    try:
        created_patient = svc.save_patient(patient=p)
    except PatientAlreadyExistsException:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Patient {p.id} already exists")
    return created_patient


@app.post("/v1/patients/{patient_id}/admissions", response_model=AdmissionOut, status_code=status.HTTP_201_CREATED)
def save_admission(patient_id: int, admission: AdmissionIn, db: Session = Depends(get_db)):
    svc = PatientService(patient_repo=PatientSQLiteRepository(db))
    try:
        return svc.save_admission(patient_id=patient_id, admission=admission)
    except PatientNotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Patient {patient_id} is not found")


@app.get("/v1/patients/{patient_id}/admissions", response_model=PaginationResponse[AdmissionOut])
def get_admissions(patient_id: int,
                   pagination: PaginationParams = Depends(PaginationParams),
                   db: Session = Depends(get_db)):
    svc = PatientService(patient_repo=PatientSQLiteRepository(db))
    try:
        svc.get_patient(patient_id=patient_id)
    except PatientNotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Patient {patient_id} is not found")
    items = svc.get_admissions(patient_id=patient_id, offset=pagination.offset, limit=pagination.limit)
    response = {}
    response.update({"total": len(items)})
    response.update({"limit": pagination.limit})
    response.update({"offset": pagination.offset})
    response.update({"items": items})
    return response


@app.get("/v1/patients/}", response_model=PaginationResponse[PatientOut])
def get_patients(db: Session = Depends(get_db),
                 pagination: PaginationParams = Depends(PaginationParams)):
    svc = PatientService(patient_repo=PatientSQLiteRepository(db))

    items = svc.get_patients(offset=pagination.offset, limit=pagination.limit)
    response = {}
    response.update({"total": len(items)})
    response.update({"limit": pagination.limit})
    response.update({"offset": pagination.offset})
    response.update({"items": items})
    return response


@app.get("/v1/patients/{patient_id}", response_model=PatientOut)
def get_patient(patient_id: int, db: Session = Depends(get_db)):
    svc = PatientService(patient_repo=PatientSQLiteRepository(db))
    try:
        return svc.get_patient(patient_id=patient_id)
    except PatientNotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Patient {patient_id} not found")


@app.get("/v1/patients/{patient_id}/measurements/{measurement_type}", response_model=PaginationResponse[MeasurementOut])
def get_patient_measurements(patient_id: int, measurement_type: MeasurementType,
                             pagination: PaginationParams = Depends(PaginationParams),
                             db: Session = Depends(get_db)):
    """
    Get all measurements of a patient by measurement type
    """
    svc = PatientService(patient_repo=PatientSQLiteRepository(db))
    try:
        svc.get_patient(patient_id=patient_id)
    except PatientNotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Patient {patient_id} not found")

    svc2 = MeasurementService(patient_repo=PatientSQLiteRepository(db),
                              measurement_repo=MeasurementSQLiteRepository(db))
    its = svc2.measurement_repo.get_all_measurements(
        patient_id=patient_id,
        measurement_type=measurement_type,
        offset=pagination.offset,
        limit=pagination.limit
    )
    items = []
    if len(its) > 0:
        items = [MeasurementOut.from_orm(m) for m in its]

    response = {}
    response.update({"total": len(items)})
    response.update({"limit": pagination.limit})
    response.update({"offset": pagination.offset})
    response.update({"items": items})
    return response


@app.get("/v1/patients/{patient_id}/readmission-probability",
         response_model=PaginationResponse[ReadmissionProbabilityOut])
def get_patient_readmission_probability(
        patient_id: int,
        pagination: PaginationParams = Depends(PaginationParams),
        db: Session = Depends(get_db)
):
    """
    Get the readmission probabilities for a patient over time.
    """
    svc = PatientService(patient_repo=PatientSQLiteRepository(db))
    try:
        p = svc.get_patient(patient_id=patient_id)
    except PatientNotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Patient {patient_id} not found")

    svc2 = MeasurementService(patient_repo=PatientSQLiteRepository(db),
                              measurement_repo=MeasurementSQLiteRepository(db), prediction_model=None)
    its = svc2.measurement_repo.get_all_predictions(patient_id=patient_id, offset=pagination.offset,
                                                    limit=pagination.limit)
    items = []
    if its and len(its) > 0:
        items = [ReadmissionProbabilityOut.from_orm(m) for m in its]

    response = {}
    response.update({"total": len(items)})
    response.update({"limit": pagination.limit})
    response.update({"offset": pagination.offset})
    response.update({"items": items})
    return response


@app.get("/v1/")
async def root():
    return {"message": "get schwifty!"}


@app.get("/")
async def root2():
    return {"message": "get schwifty!"}
