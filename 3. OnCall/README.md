## Семинар №3 "Развёртывание OnCall".
### 0. Предварительные требования
---
- данное руководство предполагает, что Вы знакомы с материалами семинара №2 "Ingress" и установили Nginx Ingress controller.
- перед развёртыванием необходимо локально собрать образ OnCall:
```bash
git clone https://github.com/linkedin/oncall.git
cd oncall

# Настроить переменные для использования демона Docker в Minikube
eval $(minikube docker-env)

docker build -t oncall:latest

# Если выполняете задания на ВМ, необходимо заменить Dockerfile и указать прокси-сервер для корректной сборки:
cp ../docker/Dockerfile Dockerfile
docker build -t oncall:latest --build-arg http_proxy=http://10.128.0.4:3128 --build-arg HTTP_PROXY=http://10.128.0.4:3128 --build-arg https_proxy=http://10.128.0.4:3128 --build-arg HTTPS_PROXY=http://10.128.0.4:3128 .
```
- загрузить образ в minikube
```bash
minikube image load oncall:latest
```
- добавить адрес будущей локальной инсталляции OnCall в /etc/hosts
```
127.0.0.1 oncall.local
```
### 1. Запуск MySQL
---
Создаём Secret с паролем к БД и Headless Service:
```bash
cd mysql
kubectl apply -f secret.yaml
kubectl apply -f service.yaml
```
Запускаем нагрузку MySQL
```bash
kubectl apply -f statefulset.yaml
```
Проверяем, запущен ли под:
```bash
kubectl get pod
```
```
NAME                     READY   STATUS    RESTARTS       AGE
mysql-0                  1/1     Running   0              10m
```
### 2. Запуск OnCall
---
Создаём ConfigMap с конфигом приложения и Service
```bash
cd oncall
kubectl apply -f config.yaml
kubectl apply -f service.yaml
```
Запускаем нагрузку OnCall
```bash
kubectl apply -f deployment.yaml
```
Проверяем, запущены ли поды
```bash
kubectl get pod
```

```
NAME                     READY   STATUS    RESTARTS       AGE
mysql-0                  1/1     Running   0              10m
oncall-94855d89d-6qggk   1/1     Running   0              10m
oncall-94855d89d-k78xm   1/1     Running   0              10m
```

Создаём Ingress для доступа к сервису:
```bash
kubectl apply -f ingress.yaml
```

Проверяем, создан ли ресурс Ingress
```bash
NAME             CLASS   HOSTS          ADDRESS        PORTS   AGE
oncall-ingress   nginx   oncall.local   192.168.49.2   80      5d2h
```

Делаем ingress доступным на хостовой машине, это связано с особенностями minikube. Не закрываем данное окно!!!

```bash
minikube tunnel
```

Проверяем доступность OnCall по адресу `oncall.local`

```bash
curl http://oncall.local
```

```bash
# Если выполняете задание на ВМ, можно применить туннелирование для доступа с локального компьютера:
ssh -N -L 127.0.0.1:80:<адрес ВМ>:80
```
