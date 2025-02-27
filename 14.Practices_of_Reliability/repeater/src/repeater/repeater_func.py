import requests
import time


server_error_codes = [500, 502, 503, 504]


class ConnectionError(Exception):
    pass

# microservice availability checker. Repeater type.
def GetData(service_url: str) -> str | ConnectionError:
    request_data = requests.get(url=service_url)
    if request_data.status_code == 200:
        return request_data.text
    # retry request when server sent bad responce
    elif request_data.status_code in server_error_codes:
        for retry in range(3):
            # exponential delay for next retries
            time.sleep(retry)
            request_data = requests.get(url=service_url)
            if request_data.status_code == 200:
                return request_data.text
            elif request_data.status_code in server_error_codes:
                continue
    # After 3 retries raise an error
    raise ConnectionError("Microservice connection error.")

# print(GetData('https://httpbin.org/status/200'))
print(GetData('https://httpbin.org/status/500'))
# print(GetData('https://www.tbank.ru/'))
