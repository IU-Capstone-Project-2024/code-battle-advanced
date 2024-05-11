#!/bin/bash

minikube delete
minikube start

minikube dashboard &

docker build -t web_app:v8 ./webapp-container
docker build -t judge:latest ./judge-container
minikube image load web_app:v8
minikube image load judge

minikube kubectl -- apply -f ./kubernetes-configs/mongodb-pv.yaml
minikube kubectl -- apply -f ./kubernetes-configs/mongodb-pvc.yaml
minikube kubectl -- apply -f ./kubernetes-configs/mongodb-secrets.yaml
minikube kubectl -- apply -f ./kubernetes-configs/tasks-pv.yaml
minikube kubectl -- apply -f ./kubernetes-configs/tasks-pvc.yaml
minikube kubectl -- apply -f ./kubernetes-configs/submissions-pv.yaml
minikube kubectl -- apply -f ./kubernetes-configs/submissions-pvc.yaml

minikube kubectl -- apply -f ./kubernetes-configs/redis-pod.yaml
minikube kubectl -- apply -f ./kubernetes-configs/redis-service.yaml

minikube kubectl -- apply -f ./kubernetes-configs/judge-deployment.yaml

minikube kubectl -- apply -f ./kubernetes-configs/mongodb-deployment.yaml
minikube kubectl -- apply -f ./kubernetes-configs/web-app-client.yaml

minikube kubectl -- apply -f ./kubernetes-configs/mongodb-nodeport-svc.yaml
minikube kubectl -- apply -f ./kubernetes-configs/web-app-nodeport-svc.yaml

