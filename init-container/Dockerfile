FROM python:3.11.9-slim-bullseye

USER root

RUN pip install pymongo pathlib bcrypt

COPY ./init_database.py /init_database.py
COPY ./data /data

CMD ["python3", "/init_database.py"]

