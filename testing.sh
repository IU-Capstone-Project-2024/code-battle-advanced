docker build -t web_app:v8 ./webapp-container
minikube image load web_app:v8
minikube kubectl -- apply -f ./kubernetes-configs
