FROM python:3.11.9-slim-bullseye

USER root

RUN python3 -m pip install --upgrade setuptools

RUN pip3 install setuptools
#Installing relevant python packages
RUN pip3 install Flask-PyMongo markdown bcrypt redis pytz protobuf pathlib grpcio==1.64.1 replicate python-dotenv requests

COPY ./app.py /app.py
COPY ./ai_images.py /ai_images.py
COPY ./templates /templates
COPY ./static /static
RUN mkdir -p /static

COPY ./contest_pb2.py /contest_pb2.py
COPY ./contest_pb2.pyi /contest_pb2.pyi
COPY ./contest_pb2_grpc.py /contest_pb2_grpc.py

EXPOSE 5000

ENTRYPOINT ["python3", "/app.py"]

