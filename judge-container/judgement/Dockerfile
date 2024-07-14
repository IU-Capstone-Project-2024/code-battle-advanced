FROM python:3.11.9-slim-bullseye

USER root

RUN python3 -m pip install --upgrade setuptools

RUN apt-get update -y
RUN apt-get upgrade -y
RUN apt-get install -y apt-utils
RUN apt-get install -y bc
RUN apt-get install -y time 
RUN apt-get install -y g++
RUN apt-get install -y openjdk-11-jdk

COPY . /

CMD ["bash", "/judge.sh"]

