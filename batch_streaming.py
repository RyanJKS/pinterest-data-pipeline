from db.aws_db_connector import AWSDBConnector
from utils.data_transformations import datetime_converter
from time import sleep
import random
import requests
import json


def process_and_send(data, url, headers):
    data = datetime_converter(data)
    payload = json.dumps({"records": [{"value": data}]})
    response = requests.request(method = 'POST', url=url, headers=headers, data=payload)
    print(f"Batch Data sent with status code: {response.status_code}")
    return response.status_code


def run_batch_processing():
    aws_connector = AWSDBConnector()

    invoke_url = 'https://mvwqj6m1rk.execute-api.us-east-1.amazonaws.com/dev/topics/'
    headers = {'Content-Type': 'application/vnd.kafka.json.v2+json'}

    while True:
        sleep(random.randrange(0, 2))
        random_row = random.randint(0, 11000)

        pin_result = aws_connector.fetch_data(f"SELECT * FROM pinterest_data LIMIT {random_row}, 1")
        geo_result = aws_connector.fetch_data(f"SELECT * FROM geolocation_data LIMIT {random_row}, 1")
        user_result = aws_connector.fetch_data(f"SELECT * FROM user_data LIMIT {random_row}, 1")

        process_and_send(pin_result, invoke_url + '0a3db223d459.pin', headers)
        process_and_send(geo_result, invoke_url + '0a3db223d459.geo', headers)
        process_and_send(user_result, invoke_url + '0a3db223d459.user', headers)

if __name__ == "__main__":
    run_batch_processing()
