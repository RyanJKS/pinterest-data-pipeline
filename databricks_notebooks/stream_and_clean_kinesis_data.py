# Databricks notebook source
########################################################## MILESTONE 9: STREAM PROCESSING: AWS KINESIS ##########################################################

# COMMAND ----------

# MAGIC %run "/Users/rjhelan@outlook.com/data_cleaning_tools"

# COMMAND ----------

# The above cell is for importing cleaning functions from "data_cleaning_tools"
# Import necessary libraries
from pyspark.sql import DataFrame
from pyspark.sql.streaming import StreamingQuery
from pyspark.sql.types import *
from pyspark.sql.functions import *
import urllib

# COMMAND ----------

# Specify file type to be csv
file_type = "csv"
# Indicates file has first row as the header
first_row_is_header = "true"
# Indicates file has comma as the delimeter
delimiter = ","
# Read the CSV file to spark dataframe
aws_keys_df = spark.read.format(file_type)\
.option("header", first_row_is_header)\
.option("sep", delimiter)\
.load("/FileStore/tables/authentication_credentials.csv")

# COMMAND ----------

# Get the AWS access key and secret key from the spark dataframe
ACCESS_KEY = aws_keys_df.where(col('User name')=='databricks-user').select('Access key ID').collect()[0]['Access key ID']
SECRET_KEY = aws_keys_df.where(col('User name')=='databricks-user').select('Secret access key').collect()[0]['Secret access key']
# Encode the secret key
ENCODED_SECRET_KEY = urllib.parse.quote(string=SECRET_KEY, safe="")

# COMMAND ----------

# Task 4: Read data from Kinesis streams in Databricks

# COMMAND ----------

# Function to create data streams using kinesis stream names
def create_data_streams(kinesis_stream_name, schema):
    df = spark \
    .readStream \
    .format('kinesis') \
    .option('streamName', kinesis_stream_name) \
    .option('initialPosition','earliest') \
    .option('region','us-east-1') \
    .option('awsAccessKey', ACCESS_KEY) \
    .option('awsSecretKey', SECRET_KEY) \
    .load()

    # Deserialize the data column of the dataframe to a string
    df = df.selectExpr("CAST(data AS STRING) jsonData")

    # Parse the JSON string into a structured format using a predefined schema
    df = df.select(from_json("jsonData", schema).alias("data")).select("data.*")

    return df

# COMMAND ----------

# Function to create schemas using predefined columns name in each data streams
def create_schema(field_names):
    fields = []
    for field_name in field_names:
        # Each field has a name and is string type
        field = StructField(field_name, StringType(), True)
        fields.append(field)
    
    return StructType(fields)

# COMMAND ----------

# Predefined column names in each data stream from kinesis
pin_fields = ["category", "description", "downloaded", "follower_count", "image_src", "index", "is_image_or_video", "poster_name", "save_location", "tag_list", "title", "unique_id"]
geo_fields = ["country", "ind", "latitude", "longitude", "timestamp"]
user_fields = ["age", "date_joined", "first_name", "ind", "last_name"]

# Create schemas
pin_schema = create_schema(pin_fields)
geo_schema = create_schema(geo_fields)
user_schema = create_schema(user_fields)

# Create variables with similar name as Data streams when created on AWS Console
pin_kinesis_name = 'streaming-0a3db223d459-pin'
geo_kinesis_name = 'streaming-0a3db223d459-geo'
user_kinesis_name = 'streaming-0a3db223d459-user'

# COMMAND ----------

# Create data streams
df_pin = create_data_streams(pin_kinesis_name, pin_schema)
df_geo = create_data_streams(geo_kinesis_name, geo_schema)
df_user = create_data_streams(user_kinesis_name, user_schema)

# COMMAND ----------

# Task 5: Transform Kinesis streams in Databricks

# COMMAND ----------

# Clean the streaming data in the same way you have previously cleaned the batch data.
df_pin_cleaned = clean_df_pin(df_pin)
df_geo_cleaned = clean_df_geo(df_geo)
df_user_cleaned = clean_df_user(df_user)

# COMMAND ----------

# Task 6: Write the streaming data to Delta Tables

# COMMAND ----------

def save_to_delta_table(df: DataFrame, table_name: str)-> StreamingQuery:
    """
    Writes a streaming DataFrame to a Delta table
    
    Args:
    df (DataFrame): The streaming DataFrame to write.
    table_name (str): The name of the Delta table to write to.
    
    Returns:
    StreamingQuery: The handle to the streaming query.
    """
    # Attempt to write the stream to the Delta table
    try:
        stream_query = df.writeStream \
            .format("delta") \
            .outputMode("append") \
            .option("checkpointLocation", "/tmp/kinesis/_checkpoints/") \
            .table(table_name)
        return stream_query
    except Exception as e:
        print(f"An error occurred while writing the stream to Delta table {table_name}: {e}")

# COMMAND ----------

# Delta table names for each dataframes
pin_table_name =  "0a3db223d459_pin_table"
geo_table_name =  "0a3db223d459_geo_table"
user_table_name =  "0a3db223d459_user_table"

# Save to delta table
save_to_delta_table(df_pin_cleaned, pin_table_name)
save_to_delta_table(df_geo_cleaned, geo_table_name)
save_to_delta_table(df_user_cleaned, user_table_name)

# COMMAND ----------

# Run this cell to delete checkpoint before re-starting to save files in delta table
dbutils.fs.rm("/tmp/kinesis/_checkpoints/", True)

# COMMAND ----------


