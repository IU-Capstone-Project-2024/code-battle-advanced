FROM python:3.11.9-alpine3.20

USER root

#Installing MongoDB
RUN echo 'http://dl-cdn.alpinelinux.org/alpine/v3.6/main' >> /etc/apk/repositories
RUN echo 'http://dl-cdn.alpinelinux.org/alpine/v3.6/community' >> /etc/apk/repositories
RUN apk add py3-pip g++ linux-headers

RUN python3 -m pip install --upgrade setuptools

RUN pip3 install setuptools
#Installing relevant python packages
RUN pip3 install Flask-PyMongo markdown bcrypt redis pytz protobuf pathlib grpcio==1.64.1

COPY ./app.py /app.py
COPY ./templates /templates
COPY ./static /static
RUN mkdir -p /static

COPY ./contest_pb2.py /contest_pb2.py
COPY ./contest_pb2.pyi /contest_pb2.pyi
COPY ./contest_pb2_grpc.py /contest_pb2_grpc.py

EXPOSE 5000

ENTRYPOINT ["python3", "/app.py"]

