FROM python:3.10.15-bookworm

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV ONCALL_EXPORTER_URL=http://oncall.default.svc.cluster.local:8080
<<<<<<< HEAD
EXPOSE 9092

CMD [ "python", "./prober.py" ]
=======
# ENV ONCALL_EXPORTER_LOG_LEVEL=10
EXPOSE 9092

CMD [ "python", "./prober.py" ]
>>>>>>> 8c4c1c3889567a10cfc12ed1e5b3b362a4b1337b
