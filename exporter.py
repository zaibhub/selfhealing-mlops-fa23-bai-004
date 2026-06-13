from prometheus_client import start_http_server, Gauge
import requests, time

TARGET_URL = "http://localhost:32500/api/latest-confidence"
METRIC = Gauge("prediction_confidence_score", "Latest model prediction confidence score")

def poll():
    while True:
        try:
            resp = requests.get(TARGET_URL, timeout=3)
            data = resp.json()
            METRIC.set(data.get("confidence", 1.0))
        except Exception:
            METRIC.set(1.0)
        time.sleep(5)

if __name__ == "__main__":
    start_http_server(8000)
    poll()
