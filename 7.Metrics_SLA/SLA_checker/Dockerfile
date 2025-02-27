FROM python:3.10.15-bookworm

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PROMETHEUS_API_URL=http://prometheus.default.svc.cluster.local:9090
ENV LOG_LEVEL=10
# ENV MYSQL_HOST=http://oncall-mysql.default.svc.cluster.local:3306
EXPOSE 80

CMD [ "python", "./sla_check.py" ]
