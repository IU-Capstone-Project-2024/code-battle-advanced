FROM python:3.11.9-slim-bullseye

USER root

RUN python3 -m pip install --upgrade setuptools
#Installing relevant python packages
RUN pip install pymongo redis protobuf pathlib grpcio==1.64.1

RUN apt-get update -y
RUN apt-get upgrade -y
RUN apt-get install -y apt-utils
RUN apt-get install -y bc
RUN apt-get install -y time 
RUN apt-get install -y g++
RUN apt-get install -y openjdk-11-jdk

COPY ./worker.py /worker.py
COPY ./judge.sh /judge.sh

COPY ./contest_pb2.py /contest_pb2.py
COPY ./contest_pb2.pyi /contest_pb2.pyi
COPY ./contest_pb2_grpc.py /contest_pb2_grpc.py

RUN mkdir /tasks
RUN mkdir /tasks/current

EXPOSE 5000

CMD ["python3", "/worker.py"]

