from __future__ import annotations

import csv
import time

import requests


def stream_patients_csv(url: str, path: str):
    # Open the CSV file and process in line by line
    with open(path, "r") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            print("patient: ", row["pat_id"], row["age"])
            # Send POST request to create patient
            resp = requests.post("{0}/patients/".format(url),
                                 headers={
                                     'Content-Type': 'application/json'
                                 },
                                 json={
                                     "id": int(row["pat_id"]),
                                     "age": round(float(row["age"])),
                                 })
            if resp.status_code != 201:
                print(str(resp.status_code), resp.text)


def stream_admission_csv(url: str, path: str):
    # Open the CSV file and process in line by line
    with open(path, "r") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            print("admission for: ", row["pat_id"])
            # Send POST request to create patient
            resp = requests.post("{0}/patients/{1}/admissions".format(url, row["pat_id"]),
                                 headers={
                                     'Content-Type': 'application/json'
                                 },
                                 json={
                                     "patient_id": int(row["pat_id"]),
                                     "date_admission": row["date_admission"],
                                     "date_discharge": row["date_discharge"],
                                 })
            if resp.status_code != 201:
                print(str(resp.status_code), resp.text)


def stream_signal_csv(url: str, csv_path: str):
    # Open the CSV file and process in line by line
    with open(csv_path, "r") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            print("signal for: ", row["pat_id"])
            # Send POST request to create patient
            resp = requests.post("{0}/measurements".format(url),
                                 headers={
                                     'Content-Type': 'application/json'
                                 },
                                 json={
                                     "patient_id": int(row["pat_id"]),
                                     "day": row["day"],
                                     "hour": row["hour"],
                                     "parameter": row["parameter"],
                                     "value": float(row["value"]),
                                 })
            if resp.status_code != 201:
                print(str(resp.status_code), resp.text)


if __name__ == "__main__":
    url = "http://localhost:80/v1"
    start = time.monotonic()
    csv_path = "data/age.csv"
    stream_patients_csv(url, csv_path)
    end = time.monotonic()
    print(f"loaded patients in {end - start:.6f} seconds")

    start = time.monotonic()
    csv_path = "data/admission.csv"
    stream_admission_csv(url, csv_path)
    end = time.monotonic()
    print(f"loaded admissions in {end - start:.6f} seconds")

    start = time.monotonic()
    csv_path = "data/signal.csv"
    stream_signal_csv(url, csv_path)
    end = time.monotonic()
    print(f"loaded signals in {end - start:.6f} seconds")
