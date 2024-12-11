import logging
import time
import requests
import sys
import signal
from prometheus_client import start_http_server, Gauge, Counter
from environs import Env

# PROBER_CREATE_USER_SCENARIO_TOTAL = Counter(
#     "prober_create_user_scenario_total", "Total count of runs the create user scenario to oncall API"
# )
# PROBER_CREATE_USER_SCENARIO_SUCCESS_TOTAL = Counter(
#     "prober_create_user_scenario_success_total", "Total count of success runs the create user scenario to oncall API"
# )
# PROBER_CREATE_USER_SCENARIO_SUCCESS_FAIL_TOTAL = Counter(
#     "prober_create_user_scenario_success_fail_total", "Total count of failed runs the create user scenario to oncall API"
# )
# PROBER_CREATE_USER_SCENARIO_DURATION_SECONDS = Gauge(
#     "prober_create_user_scenario_duration_seconds", "Duration in seconds of runs the create user scenario to oncall API"
# )
PROBER_CREATE_EVENT_SCENARIO_TOTAL = Counter(
    "prober_create_event_scenario_total", "Total count of runs the create event scenario to oncall API"
)
PROBER_CREATE_EVENT_SCENARIO_SUCCESS_TOTAL = Counter(
    "prober_create_event_scenario_success_total", "Total count of success runs the create event scenario to oncall API"
)
PROBER_CREATE_EVENT_SCENARIO_SUCCESS_FAIL_TOTAL = Counter(
    "prober_create_event_scenario_success_fail_total", "Total count of failed runs the create event scenario to oncall API"
)
PROBER_CREATE_EVENT_SCENARIO_SUCCESS_LOGIN_TOTAL = Counter(
    "prober_create_event_scenario_success_login_total", "Total count of success login runs while create event scenario to oncall API"
)
PROBER_CREATE_EVENT_SCENARIO_SUCCESS_LOGIN_FAIL_TOTAL = Counter(
    "prober_create_event_scenario_success_login_fail_total", "Total count of failed login runs while create event scenario to oncall API"
)
PROBER_CREATE_EVENT_SCENARIO_SUCCESS_LOGOUT_TOTAL = Counter(
    "prober_create_event_scenario_success_logout_total", "Total count of success logout runs while create event scenario to oncall API"
)
PROBER_CREATE_EVENT_SCENARIO_SUCCESS_LOGOUT_FAIL_TOTAL = Counter(
    "prober_create_event_scenario_success_logout_fail_total", "Total count of failed logout runs while create event scenario to oncall API"
)
PROBER_CREATE_EVENT_SCENARIO_DURATION_SECONDS = Gauge(
    "prober_create_event_scenario_duration_seconds", "Duration in seconds of runs the create event scenario to oncall API"
)

env = Env()
env.read_env()

class Config(object):
    oncall_exporter_url = env("ONCALL_EXPORTER_URL")
    oncall_exporter_scrape_interval = env.int("ONCALL_EXPORTER_SCRAPE_INTERVAL", 30)
    oncall_exporter_log_level = env.log_level("ONCALL_EXPORTER_LOG_LEVEL", logging.INFO)
    oncall_exporter_metrics_port = env.int("ONCALL_EXPORTER_METRICS_PORT", 9092)

class OncallProberClient:
    def __init__(self, config: Config) -> None:
        self.oncall_url = config.oncall_exporter_url
    
    def probe(self) -> None:
        # PROBER_CREATE_USER_SCENARIO_TOTAL.inc()
        # logging.debug("try create user")

        # username = "test_probe_user"

        # start = time.perf_counter()
        # create_request = None
        
        # try:
        #     create_request = requests.post('%s/users' % (self.oncall_url), json={
        #         "name": username
        #     })
        # except Exception as err:
        #     logging.error(err)
        #     PROBER_CREATE_USER_SCENARIO_SUCCESS_FAIL_TOTAL.inc()
        # finally:
        #     try:
        #         delete_request = requests.delete(
        #             '%s/users/%s' % (self.oncall_url, username)
        #         )
        #     except Exception as err:
        #         logging.debug(err)
        
        # if create_request and create_request.status_code == 201 and delete_request.status_code == 200:
        #     PROBER_CREATE_USER_SCENARIO_SUCCESS_TOTAL.inc()
        # else:
        #     PROBER_CREATE_USER_SCENARIO_SUCCESS_FAIL_TOTAL.inc()
        
        # duration = time.perf_counter() - start

        # PROBER_CREATE_USER_SCENARIO_DURATION_SECONDS.set(duration)

        PROBER_CREATE_EVENT_SCENARIO_TOTAL.inc()
        logging.debug("try create event")

        user = "jdoe"
        team = "Test Team"
        role = "primary"

        start = time.perf_counter()
        login_request = None
        create_request = None

        # Create a session 
        session = requests.Session()

        try:
            # Send POST request to log in
            login_request = session.post('%s/login' % (self.oncall_url), headers={
                                            'Content-Type': 'application/x-www-form-urlencoded'},
                                            data='username=jdoe&password=jdoe')
        except Exception as err:
            logging.error(err)
            PROBER_CREATE_EVENT_SCENARIO_SUCCESS_LOGIN_FAIL_TOTAL.inc()
        else:
            PROBER_CREATE_EVENT_SCENARIO_SUCCESS_LOGIN_TOTAL.inc()
        finally:
            try:
                # Create a event
                unixtimestamp = int(time.time())
                week_in_seconds = 604800
                create_request = session.post('%s/api/v0/events' % (self.oncall_url), json={
                    "start": unixtimestamp + week_in_seconds,
                    "end": unixtimestamp + 2 * week_in_seconds,
                    "user": user,
                    "team": team,
                    "role": role
                })
            except Exception as err:
                logging.debug(err)
                PROBER_CREATE_EVENT_SCENARIO_SUCCESS_FAIL_TOTAL.inc()
            finally:
                try:
                    # Delete the event
                    delete_request = session.delete('%s/api/v0/events/%s' % (self.oncall_url, create_request.text))
                except Exception as err:
                    logging.debug(err)
                finally:
                    try:
                        # Log out
                        logout_request = session.post('%s/logout' % (self.oncall_url))
                    except Exception as err:
                        logging.debug(err)
                        PROBER_CREATE_EVENT_SCENARIO_SUCCESS_LOGOUT_FAIL_TOTAL.inc()
                    else:
                        PROBER_CREATE_EVENT_SCENARIO_SUCCESS_LOGOUT_TOTAL.inc()
        
        # Check all response statuses
        if login_request.status_code == 200 and create_request.status_code == 201 \
            and delete_request.status_code == 200 \
            and logout_request.status_code == 200:
            PROBER_CREATE_EVENT_SCENARIO_SUCCESS_TOTAL.inc()
        else:
            PROBER_CREATE_EVENT_SCENARIO_SUCCESS_FAIL_TOTAL.inc()
        
        duration = time.perf_counter() - start

        PROBER_CREATE_EVENT_SCENARIO_DURATION_SECONDS.set(duration)

def setup_logging(config: Config):
    logging.basicConfig(
        stream=sys.stdout,
        level=config.oncall_exporter_log_level,
        format="%(asctime)s %(levelname)s:%(message)s"
    )

def main():
    config = Config()
    setup_logging(config)

    logging.info(
        f"Starting prober exporter on port: {config.oncall_exporter_metrics_port}"
    )
    start_http_server(config.oncall_exporter_metrics_port)
    client = OncallProberClient(config)

    while True:
        logging.debug(f"Run prober")
        client.probe()
        logging.debug(
            f"Waiting {config.oncall_exporter_scrape_interval} seconds for next loop"
        )
        time.sleep(config.oncall_exporter_scrape_interval)

def terminate(signal, frame):
    print("Terminating")
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGTERM, terminate)
    main()