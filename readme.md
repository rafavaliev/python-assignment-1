# Python assignment

![tests](https://github.com/rafavaliev/python-assignment/actions/workflows/py.yml/badge.svg)

Stream patient data(semi-static data like age and semi-realtime data like hear_rate or blood_pressure) from CSV to a
service. On the service side calculate probability of the client readmission and save it to database.

# Assignment

This was a home assignment from a company I will not disclose. Commits are squashed.

I will include *NOT* the original task description. The idea was to stream medical data of patients in intensive care
unit(IC/ICU) and generate
probability of the patient readmission.

### Files structure

    .
    ├── alembic     # Alembic migrations(not finished)
    ├── data
    │   ├── admission.csv
    │   ├── signal.csv
    │   └── age.csv
    ├── src
    │   ├── config  # Config files
    │   │   ├── cache.py    # Redis config
    │   │   ├── database.py # SQLite config
    │   ├── measurements        # Measurements package
    │   ├── patient             # Patient package
    │   ├── dependencies.py     # FastAPI dependencies
    │   ├── main.py             # FastAPI app
    │   ├── measurement_service.py # Service to create measurements
    │   ├── models.py           # Database models
    │   ├── patient_service.py  # Service to create patients and admissions
    │   ├── schemas.py          # Pydantic schemas
    │   └── test_patient_service.py # Tests for patient service
    ├── docker-compose.yml
    ├── Dockerfile
    ├── read_csv_and_load_to_the_app.py # Script to read CSV and stream data to the service
    ├── README.md
    ├── requirements.txt    # Python requirements

## What's done

1. Script to read CSV and stream data to the service
    * This script created patients, adds admissions and saved measurements together with calculated probability
2. API service
    * This service is responsible for creating patients, admissions and measurements
    * It also calculates probability of readmission and saves it to the database
    * It uses Redis as cache and SQLite as a database
    * Model to calculate readmission probability can be changed, see examples in endpoints `/v0/measurements`
      and `/v1/measurements`
    * Some tests for patient service and readmission probability calculation

## What's not done

1. Script that loads data to the service could be improved:
    * multiple threads to speed it up
    * more configurations like "how many patients to create" or "how many admissions to create" to not load all the data
      at once
2. API service could be improved
    * more tests
    * proper database like PostgreSQL
    * HTTPS
    * authentication (Now I assume only 1 hospital(client) uses our API and no one else) and multitenancy.
        * Model would need to be changed to have hospital_id property.
    * Possible queue when we save measurements, so if any of the dependencies is down we can retry later
    * Better business logic for calculating probability
        * I don't take admission dates into account. So if patient stayed at IC multuple times, probability would be
          calculated as it's only 1 admission
    * Better handling of system failures.
        * If Redis is down, our FastReadmissionPredictionModel will not work. I could make a fallback case to use
          SlowReadmissionPredictionModel, but it's not implemented.

## How to run

* Without docker: `uvicorn src.main:app --reload`
    * Visit 127.0.0.1:8000 (or any other port you choose) to see the app running
* `docker-compose build && docker-compose up`
    * Visit 127.0.0.1:80 (or any other port you choose) to see the app running

After API is ready, run `read_csv_and_load_to_the_app.py` to load data to the service.

### Requirements

* docker
* fastapi
* uvicorn[standard]
* everything else in requirements.txt

### Metrics

I exported prometheus metrics to the /metrics endpoint.

No Grafana dashboard created.

## Resources planning

### Calculations for NL

From the requirements:
'''
The IC continuously collects vast amounts of data, including physiological measurements like heart rate and blood
pressure taken per minute, as well as patient characteristics, clinical observations, and laboratory results like blood
values. You will be provided with three datasets containing IC data. (Note: artificial datasets are already implied by
the use of the word "datasets" in the original text)
'''

* Let's say we receive 5 different measurements per patient per minute.
* Amount of IC in the Netherlands: 1189 as per
  2005[ref](https://healthmanagement.org/c/icu/issuearticle/organisational-aspects-of-ic-in-the-netherlands). Let's
  round to 2k for the Netherlands.
* Amount of hospitals ~150.
* Average(during covid years) amount of IC patients per day : 20, which rounds to 20*365=7300 per
  year. [link](https://coronadashboard.government.nl/landelijk/intensive-care-opnames), Let's round this number to 8000

**Total requests per second calculations**
That gives us `2000(ICs) * 5(measurements) = 10000` measurements per minute, or 166 per second, with peak writes up to
500 RPS. We ignore amount of patients, because we receive data only per IC, even though patients change.

**Total storage calculations for 1 year**

* 10000 measurements per minute * 60 minutes * 24 hours * 365 days = 5_256_000_000 measurements per year.
* 1 measurement is 1 row in the database with: measurement id, measurement timestamp, parameter(blood pressure, heart
  rate, etc), measurement value, patient_id.
* Let's take 16 bytes for all IDs(measurement id, patient id), 16 bytes for timestamp, 1 byte for parameter type, 16
  bytes for value, which is 65 bytes in total. (It's a unoptimized value just for calculations)
* 5_256_000_000 * 65 bytes = 318 GB per year.
* Due to small amount of data for patients, ICs and hospitals, let's say it takes 1 GB total.
* Let's round to 350 GB per year.

### Calculations for the whole Europe

If we want to expand to the whole Europe:

* Amount of IC Amount of IC in Europe: 73585 as per
  2012 [link](https://link.springer.com/article/10.1007/s00134-012-2627-8), let's round to 75k for Europe.
* Same 5 measurements per IC per minute

**Total requests per second calculations**

`75000(ICs) * 5(measurements) = 375000` measurements per minute,
or 6250 per second, with peak writes up to 10k RPS.

**Total storage calculations for 1 year**

* 375000 measurements per minute * 60 minutes * 24 hours * 365 days = 197_100_000_000 measurements per year.
* Same 65 bytes per measurement.
* 197_100_000_000 * 65 bytes ~ 12 TB per year.

## Database migrations

not finished