#!/bin/bash

minikube delete
minikube start --vm-driver=docker --registry-mirror="https://mirror.gcr.io"

minikube dashboard &

minikube addons enable metrics-server &

docker build -t web_app:v8 ./webapp-container
docker build -t judge:latest ./judge-container
docker build -t init_database:latest ./init-container
minikube image load web_app:v8
minikube image load judge
minikube image load init_database

minikube kubectl -- apply -f ./kubernetes-configs

