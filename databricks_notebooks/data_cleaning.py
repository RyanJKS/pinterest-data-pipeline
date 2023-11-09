# Databricks notebook source
###################################################### MILESTONE 7: BATCH PROCESSING: SPARK ON DATABRICKS - PART 1 ##############################################################

# COMMAND ----------

# MAGIC %run "/Users/rjhelan@outlook.com/data_cleaning_tools"

# COMMAND ----------

# The above cell is for importing cleaning functions from "data_cleaning_tools"
# Import necessary libraries
from pyspark.sql import DataFrame
from pyspark.sql.functions import *

# COMMAND ----------

# Create Dataframes from data in S3 bucket
# File location and type
file_type = "json"
# Ask Spark to infer the schema
infer_schema = "true"

# Asterisk(*) indicates reading all the content of the specified file that have .json extension
# Note: The path to the JSON objects in your S3 bucket should match the structure seen in the file_location url: `topics/<UserID>.pin/partition=0/`
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

# COMMAND ----------

# Task 1: Clean the DataFrame that contains information about Pinterest posts
df_pin_cleaned = clean_df_pin(df_pin)

# Task 2: Clean the DataFrame that contains information about geolocation.
df_geo_cleaned = clean_df_geo(df_geo)

# Task 3: Clean the DataFrame that contains information about users.
df_user_cleaned = clean_df_user(df_user)

# COMMAND ----------

#  Register the DataFrame as a global temp view to access across notebooks
df_pin_cleaned.createOrReplaceGlobalTempView("df_pin_temp_view")
df_geo_cleaned.createOrReplaceGlobalTempView("df_geo_temp_view")
df_user_cleaned.createOrReplaceGlobalTempView("df_user_temp_view")

# COMMAND ----------


