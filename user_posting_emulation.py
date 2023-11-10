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
    """
    A connector class to create a connection to an AWS RDS instance.
    """

    def __init__(self):
        """
        Initializes the database connection parameters.
        """
        self.HOST = "pinterestdbreadonly.cq2e8zno855e.eu-west-1.rds.amazonaws.com"
        self.USER = 'project_user'
        self.PASSWORD = ':t%;yCY3Yjg'
        self.DATABASE = 'pinterest_data'
        self.PORT = 3306
        
    def create_db_connector(self):
        """
        Creates a database engine using SQLAlchemy.
        
        Returns:
            engine: A SQLAlchemy engine instance connected to the database.
        """
        engine = sqlalchemy.create_engine(f"mysql+pymysql://{self.USER}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.DATABASE}?charset=utf8mb4")
        return engine


new_connector = AWSDBConnector()

def datetime_converter(data):
    """
    Converts datetime objects to ISO format, and recursively applies to lists and dictionaries.
    
    Args:
        data (datetime|list|dict): The data to convert.
        
    Returns:
        The data in a format that can be serialized to JSON.
    """
    if isinstance(data, datetime.datetime):
        return data.isoformat()
    elif isinstance(data, dict):
        return {key: datetime_converter(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [datetime_converter(item) for item in data]
    else:
        return data

def run_infinite_post_data_loop():

    invoke_url='https://mvwqj6m1rk.execute-api.us-east-1.amazonaws.com/dev/topics/'
    headers = {'Content-Type': 'application/vnd.kafka.json.v2+json'}
    pin_topic = '0a3db223d459.pin'
    geo_topic = '0a3db223d459.geo'
    user_topic = '0a3db223d459.user'

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


            pin_payload = json.dumps({"records": [{"value": pin_result}]})
            geo_payload = json.dumps({"records": [{"value": geo_result}]})
            user_payload = json.dumps({"records": [{"value": user_result}]})

            pin_response = requests.request("POST",invoke_url+pin_topic, headers=headers, data=pin_payload, timeout=30)
            print(pin_response.status_code)

            geo_response = requests.request("POST",invoke_url+geo_topic, headers=headers, data=geo_payload)
            print(geo_response.status_code)

            user_response = requests.request("POST",invoke_url+user_topic, headers=headers, data=user_payload)
            print(user_response.status_code)

 
if __name__ == "__main__":
    run_infinite_post_data_loop()
    print('Working')
    