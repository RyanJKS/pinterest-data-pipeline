# Databricks notebook source
###################################################### MILESTONE 6: BATCH PROCESSING: DATABRICKS ##############################################################

# COMMAND ----------

# Check if the 'authentication_credentials.csv' file has been uploaded
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

# Check if the s3 bucket is uploaded
display(dbutils.fs.ls("/mnt/s3_bucket/../.."))

# COMMAND ----------

# To unmount the S3 bucket, run the following command:
# dbutils.fs.unmount("/mnt/s3_bucket")
