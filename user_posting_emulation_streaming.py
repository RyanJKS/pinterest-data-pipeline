import requests
from time import sleep
import random
from multiprocessing import Process
import boto3
import json
import sqlalchemy
from sqlalchemy import text
import datetime

random.seed(100)

class AWSDBConnector:

    def __init__(self):
        self.HOST = "pinterestdbreadonly.cq2e8zno855e.eu-west-1.rds.amazonaws.com"
        self.USER = 'project_user'
        self.PASSWORD = ':t%;yCY3Yjg'
        self.DATABASE = 'pinterest_data'
        self.PORT = 3306
        
    def create_db_connector(self):
        engine = sqlalchemy.create_engine(f"mysql+pymysql://{self.USER}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.DATABASE}?charset=utf8mb4")
        return engine


new_connector = AWSDBConnector()

def datetime_converter(data):
    if isinstance(data, datetime.datetime):
        return data.isoformat()
    elif isinstance(data, dict):
        return {key: datetime_converter(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [datetime_converter(item) for item in data]
    else:
        return data

def run_infinite_post_data_loop():

    invoke_url='https://mvwqj6m1rk.execute-api.us-east-1.amazonaws.com/dev/streams/'
    headers = {'Content-Type': 'application/json'}
    pin_streaming_name = 'streaming-0a3db223d459-pin'
    geo_streaming_name = 'streaming-0a3db223d459-geo'
    user_streaming_name = 'streaming-0a3db223d459-user'

    while True:
        sleep(random.randrange(0, 2))
        random_row = random.randint(0, 11000)
        engine = new_connector.create_db_connector()

        with engine.connect() as connection:

            pin_string = text(f"SELECT * FROM pinterest_data LIMIT {random_row}, 1")
            pin_selected_row = connection.execute(pin_string)
            
            for row in pin_selected_row:
                pin_result = dict(row._mapping)

            geo_string = text(f"SELECT * FROM geolocation_data LIMIT {random_row}, 1")
            geo_selected_row = connection.execute(geo_string)
            
            for row in geo_selected_row:
                geo_result = dict(row._mapping)

            user_string = text(f"SELECT * FROM user_data LIMIT {random_row}, 1")
            user_selected_row = connection.execute(user_string)
            
            for row in user_selected_row:
                user_result = dict(row._mapping)

            geo_result = datetime_converter(geo_result)
            user_result = datetime_converter(user_result)

            pin_payload = json.dumps({
                "StreamName": pin_streaming_name,
                "Data": pin_result,
                "PartitionKey": "partition-1"
                })

            geo_payload = json.dumps({
                "StreamName": geo_streaming_name,
                "Data": geo_result,
                "PartitionKey": "partition-2"
                })

            user_payload = json.dumps({
                "StreamName": user_streaming_name,
                "Data": user_result,
                "PartitionKey": "partition-3"
                })

            pin_stream_url = invoke_url + pin_streaming_name + '/record'
            pin_response = requests.request("PUT",pin_stream_url, headers=headers, data=pin_payload, timeout=30)
            print(pin_response.status_code)

            geo_stream_url = invoke_url + geo_streaming_name + '/record'
            geo_response = requests.request("PUT",geo_stream_url, headers=headers, data=geo_payload)
            print(geo_response.status_code)

            user_stream_url = invoke_url + user_streaming_name + '/record'
            user_response = requests.request("PUT",user_stream_url, headers=headers, data=user_payload)
            print(user_response.status_code)

 
if __name__ == "__main__":
    run_infinite_post_data_loop()
    print('Working')
    