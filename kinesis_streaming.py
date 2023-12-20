from db.aws_db_connector import AWSDBConnector
from utils.data_transformations import datetime_converter
from time import sleep
import random
import requests
import json


def process_and_send(data, stream_name, partition_key, base_url, headers):
    """
    Processes and sends data to a specified URL with given headers.

    Args:
        data (dict): The data to be sent.
        stream_name (str): The name of the stream to which data is being sent.
        partition_key (str): The partition key for the data stream.
        base_url (str): The base URL for the data stream.
        headers (dict): The headers to be used in the request.

    Returns:
        int: The status code of the HTTP response.
    """
    data = datetime_converter(data)
    payload = json.dumps({
        "StreamName": stream_name,
        "Data": data,
        "PartitionKey": partition_key
    })

    stream_url = base_url + stream_name + '/record'
    response = requests.request("PUT", stream_url, headers=headers, data=payload, timeout=30)
    print(response.json())
    #print(f"Data sent to {stream_name} with status code: {response.status_code}")

    return response.status_code


def run_kinesis_processing():
    aws_connector = AWSDBConnector()

    invoke_url='https://mvwqj6m1rk.execute-api.us-east-1.amazonaws.com/dev/streams/'
    headers = {'Content-Type': 'application/json'}
    pin_streaming_name = 'streaming-0a3db223d459-pin'
    geo_streaming_name = 'streaming-0a3db223d459-geo'
    user_streaming_name = 'streaming-0a3db223d459-user'

    while True:
        sleep(random.randrange(0, 2))
        random_row = random.randint(0, 11000)
        pin_result = aws_connector.fetch_data(f"SELECT * FROM pinterest_data LIMIT {random_row}, 1")
        geo_result = aws_connector.fetch_data(f"SELECT * FROM geolocation_data LIMIT {random_row}, 1")
        user_result = aws_connector.fetch_data(f"SELECT * FROM user_data LIMIT {random_row}, 1")

        # Call the function for each data type
        process_and_send(pin_result, pin_streaming_name, 'partition-1', invoke_url, headers)
        process_and_send(geo_result, geo_streaming_name, 'partition-2', invoke_url, headers)
        process_and_send(user_result, user_streaming_name, 'partition-3', invoke_url, headers)

if __name__ == "__main__":
    run_kinesis_processing()