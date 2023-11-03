# Databricks notebook source- Checks what files have been uploaded
dbutils.fs.ls("/FileStore/tables/")

# COMMAND ----------

# pyspark functions
from pyspark.sql.functions import *
# URL processing
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
# Encode the secrete key
ENCODED_SECRET_KEY = urllib.parse.quote(string=SECRET_KEY, safe="")

# COMMAND ----------

    # AWS S3 bucket name
    AWS_S3_BUCKET = "user-0a3db223d459-bucket"
    # Mount name for the bucket
    MOUNT_NAME = "/mnt/s3_bucket"
    # Source url
    SOURCE_URL = "s3n://{0}:{1}@{2}".format(ACCESS_KEY, ENCODED_SECRET_KEY, AWS_S3_BUCKET)
    # Mount the drive
    dbutils.fs.mount(SOURCE_URL, MOUNT_NAME)

# COMMAND ----------

display(dbutils.fs.ls("/mnt/s3_bucket/../.."))

# COMMAND ----------

# File location and type
file_type = "json"
# Ask Spark to infer the schema
infer_schema = "true"

# Asterisk(*) indicates reading all the content of the specified file that have .json extension
pin_file_location = "/mnt/s3_bucket/topics/0a3db223d459.pin/partition=0/*.json"
geo_file_location = "/mnt/s3_bucket/topics/0a3db223d459.geo/partition=0/*.json"
user_file_location = "/mnt/s3_bucket/topics/0a3db223d459.user/partition=0/*.json"

# Function to read JSON data from a given file location in mounted S3 bucket and return dataframe
def create_spark_dataframe(file_location):
    dataframe = spark.read.format(file_type) \
        .option("inferSchema", infer_schema) \
        .load(file_location)
    return dataframe

df_pin = create_spark_dataframe(pin_file_location)
df_geo = create_spark_dataframe(geo_file_location)
df_user = create_spark_dataframe(user_file_location)

# Display Spark dataframe to check its content
display(df_pin)
display(df_geo)
display(df_user)

# COMMAND ----------


