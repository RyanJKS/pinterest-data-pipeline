# Databricks notebook source
###################################################### MILESTONE 7: BATCH PROCESSING: SPARK ON DATABRICKS - PART 1 ##############################################################

# COMMAND ----------

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

# COMMAND ----------

# Function to clean the pin DataFrame
def clean_df_pin(df_pin: DataFrame) -> DataFrame:
    """
    Cleans the pin DataFrame according to specified transformations.
    Parameters:df_pin (DataFrame): Spark DataFrame to be cleaned.
    Returns: DataFrame: Cleaned Spark DataFrame.
    """
    # Replace empty entries and entries with no relevant data in each column with None
    markers_to_replace = ["", "No description available Story format", "No description available", "N,o, ,T,a,g,s, ,A,v,a,i,l,a,b,l,e", "User Info Error", "No Title Data Available", "Image src error."]

    # Iterate over all columns and replace the markers with None
    for column_name in df_pin.columns:
        df_pin = df_pin.withColumn(column_name, when(col(column_name).isin(markers_to_replace), None).otherwise(col(column_name)))

    # Perform the necessary transformations on the follower_count to ensure every entry is a number
    df_pin = df_pin.withColumn("follower_count",
    # Remove 'k' and multiply by 1,000
    when(col("follower_count").contains("k"), (regexp_replace(col("follower_count"), "k", "").cast("int") * 1000))
    # Remove 'M' and multiply by 1,000,000
    .when(col("follower_count").contains("M"), (regexp_replace(col("follower_count"), "M", "").cast("int") * 1000000))
    # If no 'k' or 'M', just cast to int
    .otherwise(col("follower_count").cast("int"))
    )
    
    # Ensure numeric data type for columns below
    df_pin = df_pin.withColumn("downloaded", col("downloaded").cast("int"))
    df_pin = df_pin.withColumn("index", col("index").cast("int"))

    # Include only location path
    df_pin = df_pin.withColumn("save_location", regexp_replace(col("save_location"), "Local save in ", ""))

    # Rename the index column to ind
    df_pin = df_pin.withColumnRenamed("index", "ind")

    # Reorder the DataFrame columns
    column_order = [
        "ind",
        "unique_id",
        "title",
        "description",
        "follower_count",
        "poster_name",
        "tag_list",
        "is_image_or_video",
        "image_src",
        "save_location",
        "category"
    ]

    df_pin = df_pin.select(column_order)

    return df_pin

df_pin_cleaned = clean_df_pin(df_pin)

# COMMAND ----------

# Task 2: Clean the DataFrame that contains information about geolocation.

# COMMAND ----------

# Function to clean the geo DataFrame
def clean_df_geo(df_geo: DataFrame) -> DataFrame:
    # Create new column with values from latitude and longitude in array
    df_geo = df_geo.withColumn("coordinates", array(col("latitude"), col("longitude")))

    df_geo = df_geo.drop("latitude","longitude")

    df_geo = df_geo.withColumn("timestamp",to_timestamp(col("timestamp")))

    column_order = ["ind", "country", "coordinates", "timestamp"]
    df_geo = df_geo.select(column_order)

    return df_geo

df_geo_cleaned = clean_df_geo(df_geo)

# COMMAND ----------

# Task 3: Clean the DataFrame that contains information about users.

# COMMAND ----------

# Function to clean df_user DataFrame
def clean_df_user(df_user: DataFrame) -> DataFrame:

    df_user = df_user.withColumn("user_name", concat(col("first_name"), lit(" "), col("last_name")))
    df_user = df_user.drop("first_name", "last_name")

    df_user = df_user.withColumn("date_joined", to_timestamp(col("date_joined")))

    column_order = ["ind", "user_name", "age", "date_joined"]
    df_user = df_user.select(column_order)
    
    return df_user

df_user_cleaned = clean_df_user(df_user)

# COMMAND ----------

#  Register the DataFrame as a global temp view to access across notebooks
df_pin_cleaned.createOrReplaceGlobalTempView("df_pin_temp_view")
df_geo_cleaned.createOrReplaceGlobalTempView("df_geo_temp_view")
df_user_cleaned.createOrReplaceGlobalTempView("df_user_temp_view")

# COMMAND ----------


