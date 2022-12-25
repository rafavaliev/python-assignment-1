# For simplicity I use predefined FastAPI base image. In production I would use multi-stage build to reduce image size.
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY . /app

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "80"]