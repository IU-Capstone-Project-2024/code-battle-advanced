#!/bin/bash

minikube delete
minikube start

minikube dashboard &

docker build -t web_app:v8 ./webapp_container
minikube image load web_app:v8
minikube kubectl -- apply -f ./mongo-configs/mongodb-pv.yaml
minikube kubectl -- apply -f ./mongo-configs/mongodb-pvc.yaml
minikube kubectl -- apply -f ./mongo-configs/mongodb-secrets.yaml

minikube kubectl -- apply -f ./mongo-configs/mongodb-deployment.yaml
minikube kubectl -- apply -f ./mongo-configs/web-app-client.yaml

minikube kubectl -- apply -f ./mongo-configs/mongodb-nodeport-svc.yaml
minikube kubectl -- apply -f ./mongo-configs/web-app-nodeport-svc.yaml


