#!/bin/bash

minikube delete
minikube start

minikube dashboard &

minikube addons enable metrics-server &

docker build -t web_app:v8 ./webapp-container
docker build -t judge:latest ./judge-container
minikube image load web_app:v8
minikube image load judge

minikube kubectl -- apply -f ./kubernetes-configs

