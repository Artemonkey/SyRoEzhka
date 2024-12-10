FROM python:3.10.15-bookworm

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV ONCALL_EXPORTER_API_URL=http://oncall.default.svc.cluster.local:8080/api/v0
EXPOSE 9092

CMD [ "python", "./prober.py" ]