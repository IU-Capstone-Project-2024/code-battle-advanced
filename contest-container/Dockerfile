FROM python:3.11.9-alpine3.20

USER root

#Installing MongoDB
RUN echo 'http://dl-cdn.alpinelinux.org/alpine/v3.6/main' >> /etc/apk/repositories
RUN echo 'http://dl-cdn.alpinelinux.org/alpine/v3.6/community' >> /etc/apk/repositories
RUN apk add py3-pip linux-headers

RUN python3 -m pip install --upgrade setuptools
#Installing relevant python packages
RUN pip install pymongo pathlib protobuf grpcio==1.64.1 

COPY ./server.py /server.py
COPY ./contest_pb2.py /contest_pb2.py
COPY ./contest_pb2.pyi /contest_pb2.pyi
COPY ./contest_pb2_grpc.py /contest_pb2_grpc.py

COPY ./cbamodule.py /cbamodule.py
COPY ./cbacontest.py /cbacontest.py

EXPOSE 5000

CMD ["python3", "/server.py"]

