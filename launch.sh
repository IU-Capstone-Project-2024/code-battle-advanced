#!/bin/bash

minikube delete
minikube start --vm-driver=docker --registry-mirror="https://mirror.gcr.io"

minikube dashboard &

minikube addons enable metrics-server &

python3 -m grpc_tools.protoc   --proto_path=./contest-container   --python_out=./contest-container   --pyi_out=./contest-container   --grpc_python_out=./contest-container   ./contest-container/contest.proto
cp ./contest-container/contest_pb2.py ./contest-container/contest_pb2.pyi ./contest-container/contest_pb2_grpc.py -t ./judge-container
cp ./contest-container/contest_pb2.py ./contest-container/contest_pb2.pyi ./contest-container/contest_pb2_grpc.py -t ./webapp-container

docker build --network host -t web_app:v8 ./webapp-container
docker build --network host -t judge:latest ./judge-container
docker build --network host -t init_database:latest ./init-container
docker build --network host -t contest:latest ./contest-container
minikube image load web_app:v8
minikube image load judge
minikube image load init_database
minikube image load contest

minikube kubectl -- apply -f ./kubernetes-configs

