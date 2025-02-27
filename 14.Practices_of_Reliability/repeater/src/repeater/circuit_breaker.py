import logging
import requests
import time


server_error_codes = [500, 502, 503, 504]
RequestIsBad = True


class ConnectionError(Exception):
    pass

# Microservice availability checker. Circuit Breaker type.
def GetDataWithCircuitBreaker(service_url: str) -> str | ConnectionError:
    logging.debug("Starting Circuit Breaker. Closed state.")
    while True:
        request_data = requests.get(url=service_url)
        if request_data.status_code == 200:
            continue
        # Retry request when server sent bad responce
        elif request_data.status_code in server_error_codes:
            for retry in range(3):
                # exponential delay for next retries
                time.sleep(retry)
                request_data = requests.get(url=service_url)
                if request_data.status_code == 200:
                    continue
                elif request_data.status_code in server_error_codes:
                    continue
                else:
                    ConnectionError("Microservice connection error.")
            # After 3 retries stop requests to reduce stress on service.
            logging.debug("Open state. Start timeout for 10 seconds.")
            RequestIsBad = True
            while RequestIsBad:
                time.sleep(10)
                logging.debug("Going Half-Open state. Test request.")
                # Doing one test request to define next state.
                request_data = requests.get(url=service_url)
                if request_data.status_code == 200:
                    logging.debug("Closed state.")
                    RequestIsBad = False
                    continue
                elif request_data.status_code in server_error_codes:
                    logging.debug("Stay in Open state. Start timeout for 10 seconds.")
                    continue
                else:
                    ConnectionError("Microservice connection error.")
        else:
            raise ConnectionError("Microservice connection error.")


# print(GetDataWithCircuitBreaker('https://httpbin.org/status/200'))
print(GetDataWithCircuitBreaker('https://httpbin.org/status/500'))
# print(GetDataWithCircuitBreaker('https://www.tbank.ru/'))