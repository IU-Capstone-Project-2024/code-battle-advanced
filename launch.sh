#!/bin/bash

docker build -t web_app:v5 ./webapp_container
minikube image load web_app:v5
minikube kubectl -- apply --force -f ./mongo-configs
