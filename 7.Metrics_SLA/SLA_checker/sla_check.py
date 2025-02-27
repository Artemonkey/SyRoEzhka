import logging
import requests
import sys
import signal
import time
import mysql.connector
from datetime import datetime
from environs import Env


env = Env()
env.read_env()

class Config(object):
    prometheus_api_url = env("PROMETHEUS_API_URL")
    scrape_interval = env.int("SCRAPE_INTERVAL", 30)
    log_level = env.log_level("LOG_LEVEL", logging.INFO)

    mysql_host = env("MYSQL_HOST", 'oncall-mysql')
    mysql_port = env.int("MYSQL_PORT", 3306)
    mysql_user = env("MYSQL_USER", 'root')
    mysql_password = env("MYSQL_PASS", '1234')
    mysql_db_name = env("MYSQL_DB_NAME", 'sla')

class Mysql:
    def __init__(self, config: Config) -> None:
        logging.info("Connecting to db")

        self.connection = mysql.connector.connect(host=config.mysql_host, user=config.mysql_user,
                                                  passwd=config.mysql_password, auth_plugin='caching_sha2_password')

        self.table_name = 'indicators'

        logging.info('Starting migration')

        cursor = self.connection.cursor()
        cursor.execute('CREATE DATABASE IF NOT EXISTS %s' %
                       (config.mysql_db_name))
        cursor.execute('USE sla')
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS %s(
                       datetime datetime not null default NOW(),
                       name varchar(255) not null,
                       slo float(4) not null,
                       value float(4) not null,
                       is_bad bool not null default false
            )
        """ % (self.table_name))
        cursor.execute("""
            ALTER TABLE %s ADD INDEX (datetime)
        """ % (self.table_name))
        cursor.execute("""
            ALTER TABLE %s ADD INDEX (name)
        """ % (self.table_name))

    def save_indicator(self, name, slo, value, is_bad=False, time=None):
        cursor = self.connection.cursor()
        sql = f"INSERT INTO {self.table_name} (name, slo, value, is_bad, datetime) VALUES (%s, %s, %s, %s, %s)"
        val = (name, slo, value, int(is_bad), time)
        cursor.execute(sql, val)
        self.connection.commit()

class PrometheusRequest:
    def __init__(self, config: Config) -> None:
        self.prometheus_api_url = config.prometheus_api_url

    def lastValue(self, query, time, default):
        try:
            responce = requests.get(
                self.prometheus_api_url + '/api/v1/query', params={'query': query, 'time': time}
            )
            content = responce.json()
            if not content:
                return default
            if len(content['data']['result']) == 0:
                return default
            
            return content['data']['result'][0]['value'][1]
        except Exception as error:
            logging.error(error)
            return default
        
def setup_logging(config: Config):
    logging.basicConfig(
        stream=sys.stdout,
        level=config.log_level,
        format="%(asctime)s %(levelname)s:%(message)s"
    )

def main():
    config = Config()
    setup_logging(config)
    db = Mysql(config)
    prom = PrometheusRequest(config)
    logging.info(f"Starting sla checker")

    while True:
        logging.debug(f"Run sla checker")
        
        unixtimestamp = int(time.time())
        date_format = datetime.fromtimestamp(
            unixtimestamp).strftime('%Y-%m-%d %H:%M:%S')
        
        value = prom.lastValue(
            'increase(prober_create_event_scenario_success_total[1m])', unixtimestamp, 0)
        
        value = int(float(value))
        db.save_indicator(name='prober_create_event_scenario_success_total',
                          slo=4, value=value, is_bad=value < 3, time=date_format)
        
        value = prom.lastValue(
            'increase(prober_create_event_scenario_success_fail_total[1m])', unixtimestamp, 100)
        
        value = int(float(value))
        db.save_indicator(name='prober_create_event_scenario_success_fail_total',
                          slo=5, value=value, is_bad=value > 0, time=date_format)
        
        value = prom.lastValue(
            'increase(prober_create_event_scenario_success_login_fail_total[1m])', unixtimestamp, 100)
        
        value = int(float(value))
        db.save_indicator(name='prober_create_event_scenario_success_login_fail_total',
                          slo=0, value=value, is_bad=value > 0, time=date_format)
        
        value = prom.lastValue(
            '(prober_create_event_scenario_duration_seconds)', unixtimestamp, 2)
        
        value = int(float(value))
        db.save_indicator(name='prober_create_event_scenario_duration_seconds',
                          slo=1, value=value, is_bad=value > 1, time=date_format)
        
        logging.debug(
            f"Waiting {config.scrape_interval} seconds for next loop"
        )
        time.sleep(config.scrape_interval)

def terminate(signal, frame):
    print("Terminating")
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGTERM, terminate)
    main()
