# Pinterest Data Pipeline

## Table of Contents
1. [Project Description](#project-description)
2. [Installation Instructions](#installation-instructions)
3. [Usage Instructions](#usage-instructions)
4. [File Structure](#file-structure)
5. [License Information](#license-information)

## Project Description
The Pinterest Data Pipeline project is designed to emulate user postings on Pinterest and capture this data for further analysis. The project leverages AWS services, including VPC, EC2, and MSK (Managed Streaming for Kafka), to create a robust and scalable data pipeline. The primary aim of this project is to understand the intricacies of data flow, from user postings on Pinterest to data storage and analysis.

### What it does:
The project processes data related to Pinterest posts, their geolocations, and the users who made these posts. The main script called `user_posting_emulation.py` outputs the following data in this format:
    - pinterest_data contains data about posts being updated to Pinterest
    - geolocation_data contains data about the geolocation of each Pinterest post found in pinterest_data
    - user_data contains data about the user that has uploaded each post found in pinterest_data
 It uses a combination of AWS services, Kafka, and other tools to create a pipeline that takes in data, processes it, stores it in a structured manner and mounted on Databricks for further analysis.

### Aim of the project:
The primary goal of this project is to provide hands-on experience with setting up and managing a data pipeline. It offers insights into how large-scale applications like Pinterest handle vast amounts of data, ensuring it's processed efficiently and stored securely.

### What I learned:
Through the development and implementation of this project, several key learnings were achieved:

- **AWS Service Integrations:** Gained hands-on experience in integrating various AWS services to create a cohesive data pipeline.
- **Kafka Cluster Management:** Learned the intricacies of setting up and managing a Kafka cluster, ensuring data is streamed efficiently.
- **Data Pipeline Design:** Understood the importance of designing a robust and scalable data pipeline, ensuring data integrity and availability.
- **MSK Cluster Setup:** Grasped the process of setting up an MSK cluster on AWS, understanding its role in data streaming.
- **Kafka Setup on EC2:** Delved into the details of setting up Kafka on an EC2 instance, ensuring seamless data streaming to the MSK cluster.
- **S3 Storage:** Learned the process of storing data in S3 buckets, ensuring data durability and availability.
- **API Gateway Creation:** Understood the significance of creating an API gateway to stream data to the MSK cluster.
- **Databricks for Data Analysis:** Gained insights into using Databricks for querying batch data stored in S3.

## Installation Instructions

#### Prerequisites
- Python 3.x
- Required Python Packages (SQLAlchemy, PyYAML, PyMySQL)
- Knowledge of Linux OS/ Windows WSL and AWS services

First start by cloning the repository to your local machine.
```bash
    git clone https://github.com/RyanJKS/pinterest-data-pipeline.git
```

### AWS Setup (IAM, VPC & EC2)
1. Create an AWS account (For this project, the region was set to 'us-east-1') 

2. Create an IAM user using the Principle of Least Priviledge
> Note: The IAM User's username will be denoted as <UserID> to align with common naming conventions used by companies in the software development lifecycle.

3. Create a VPC and launch an EC2 instance within its subnet.
- Configure the security group of the VPC and EC2 to allow internet access.
- Save the key-pair `.pem` file after creating the EC2 instance in your local machine
> Make a note of the EC2 User's ARN and it will be denoted as `<EC2-ARN>`.

4. IAM Role Creation: Create the role named `<UserID>-ec2-access-role`
> Make a note of the AWS Role ARN and it will be denoted as `<awsRoleARN>`

5. Configure EC2 client to use AWS IAM for cluster authentication:
- Navigate to the IAM console and under “Roles”, select recently created role.
- Go to the "Trust relationships" tab and select "Edit trust policy".
- Click on "Add a principal" and choose "IAM roles" as the Principal type.
- Replace ARN with `<awsRoleARN>`
> Note: These steps are crucial in order to allow IAM authentication to the MSK cluster.

6. Ensure the EC2 key-pair is acquired and use it to launch an instance on your local machine using an SSH client whilst being in the directory with the key-pair `.pem` file.


### MSK Cluster
1. Create an MSK Cluster on the AWS console called `pinterest-msk-cluster`. It is a service used to buld and run applications that use Apache Kafka to process data
> Make a note of **Bootstrap servers string** and **Plaintext Apache Zookeeper connection** after creating the cluster as it will be used later.

**Optional:** You can also get these string if you run the following commands after replacing the `ClusterArn` with the information found the MSK Cluster console information.

```bash
aws kafka describe-cluster --cluster-arn ClusterArn
aws kafka get-bootstrap-brokers --cluster-arn ClusterArn
```


### Kafka Setup
1. Install Java and download Kafka (version 2.12-2.8.1 was used for this project) in your EC2 machine.
```bash
sudo yum install java-1.8.0
```
```bash
wget https://archive.apache.org/dist/kafka/2.8.1/kafka_2.12-2.8.1.tgz
tar -xzf kafka_2.12-2.8.1.tgz
```
2. Install the ==IAM MSK authentication package== in the `kafka_2.12-2.8.1/libs` on your client EC2 machine. This package is necessary to connect to MSK clusters that require IAM authentication.

```bash
wget https://github.com/aws/aws-msk-iam-auth/releases/download/v1.1.5/aws-msk-iam-auth-1.1.5-all.jar
```
3. Create enviroment variable `CLASSPATH` in the `bash.rc` file in order to ensure that the Amazon MSK IAM libraries are easily accessible to the Kafka client. Add the following line in the `bash.rc` file and after that run the `source` command to apply the changes to the current session: `source ~/.bashrc`.

```bash
export CLASSPATH=/home/ec2-user/kafka_2.12-2.8.1/libs/aws-msk-iam-auth-1.1.5-all.jar
```

4. Configure Kafka client to use AWS IAM. Navigate to `kafka_2.12-2.8.1/bin` and create a `client.properties` file which should contain the following information.
> Note: Replace the `<awsRoleARN>` with the previously saved string in Role Creation.

```bash
# Sets up TLS for encryption and SASL for authN.
security.protocol = SASL_SSL

# Identifies the SASL mechanism to use.
sasl.mechanism = AWS_MSK_IAM

# Binds SASL client implementation.
sasl.jaas.config = software.amazon.msk.auth.iam.IAMLoginModule required awsRoleArn="<awsRoleARN>";

# Encapsulates constructing a SigV4 signature based on extracted credentials.
# The SASL client bound by "sasl.jaas.config" invokes this class.
sasl.client.callback.handler.class = software.amazon.msk.auth.iam.IAMClientCallbackHandler
```

5. Create Kafka Topics. Navigate to `kafka_2.12-2.8.1/bin` and run the following command, replacing **BootstrapServerString** with the connection string previously save and `<topic_name> with the following:

```bash
./kafka-console-producer.sh --bootstrap-server BootstrapServerString --producer.config client.properties --group students --topic <topic_name>
```
Topic names:
- `<UserID>.pin` for the Pinterest posts data
- `<UserID>.geo` for the post geolocation data
- `<UserID>.user` for the post user data

**Optional:** Run a Kafka Consumer in order to check the incoming messages to the cluster for later when communicating through an API.

```bash
./kafka-console-consumer.sh --bootstrap-server BootstrapServerString --consumer.config client.properties --group students --topic <topic_name> --from-beginning
```

### S3
1. Create an S3 bucket with name `<user-UserID>-bucket>`.
2. Create an IAM role that allows you to write to this bucket or a VPC Endpoint to S3

### MSK Connect
> This is a feature of MSK that allows users to stream data to and from their MSK-hosted Apache Kafka clusters.

1. Create a custom plugin, which will contain the code that defines the logic of our connector. The name should be in this format `<UserID>-plugin`

- Connect to EC2 instance and download the ==Confluent.io Amazon S3 Connector== in a folder called `kafka-connect-s3`.
- Copy the files in the S3 bucket. This plugin will act as a sink connector that exports data from Kafka topics to S3 objects in either JSON, Avro or Bytes format.

```bash
# assume admin user privileges
sudo -u ec2-user -i
# create directory where we will save our connector 
mkdir kafka-connect-s3 && cd kafka-connect-s3
# download connector from Confluent
wget https://d1i4a15mxbxib1.cloudfront.net/api/plugins/confluentinc/kafka-connect-s3/versions/10.0.3/confluentinc-kafka-connect-s3-10.0.3.zip
# copy connector to our S3 bucket
aws s3 cp ./confluentinc-kafka-connect-s3-10.0.3.zip s3://<user-<UserID>-bucket>/kafka-connect-s3/
```
- After uploading the connector to the S3 bucket, copy the S3 zip file's S3 URI.
- Navigate to MSK on AWS Console and select "Create Custom Plugin" under "MSK Connect" where you paste the "S3 URI" in the shown input text field.

2. Create a connector. The name should be in this format `<UserID>-connector`

- In the MSK console, select "Connectors" under the "MSK Connect" section on the left side of the console. Choose Create connector.
- Select the plugin you created and your MSK cluster from the cluster list.
- In the "Connector configuration" settings copy the following configuration:
>Note: Replace the `<UserID>` with the correct string.

```bash
connector.class=io.confluent.connect.s3.S3SinkConnector
# same region as our bucket and cluster
s3.region=us-east-1
flush.size=1
schema.compatibility=NONE
tasks.max=3
# include nomeclature of topic name, given here as an example will read all data from topic names starting with msk.topic....
topics.regex=<UserID>.*
format.class=io.confluent.connect.s3.format.json.JsonFormat
partitioner.class=io.confluent.connect.storage.partitioner.DefaultPartitioner
value.converter.schemas.enable=false
value.converter=org.apache.kafka.connect.json.JsonConverter
storage.class=io.confluent.connect.s3.storage.S3Storage
key.converter=org.apache.kafka.connect.storage.StringConverter
s3.bucket.name=<user-<UserID>-bucket>
```
- In the "Access Permission" tab, select the IAM role that is used for authentication to the MSK cluster which is in the format `<UserID>-ec2-access-role`

After creating the plugin-connector pair, data passing through the IAM authenticated cluster, will be automatically stored in the designated S3 bucket.

### API Gateway
Create an API in order to stream data from the `user_posting_emulation.py` script to MSK cluster and then store the data in the S3 bucket.
1. Navigate to API Gateway on AWS console and create a REST API.
2. Create a resource that allows you to build a PROXY integration for your API. Click on the "Resources" section.

The figure below shows how it should be set up.

<div align="center">
  <img src="/images/api-create-resource.png" alt="API_Resource">
</div>

3. Configure this resource by going to "ANY" in the "Resources" section. Click on "Edit integration". We will use an integration type of "HTTP" in this project and a more detailed explanation of proxy integrations can be found [here](https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html).
> Make a note of the EC2 instance Public IPv4 DNS which will be referred as `<EC2-Public-DNS>`.

The figure below shows how it should be set up.

<div align="center">
  <img src="/images/api-configure-reource.png" alt="API_Resource_Configure">
</div>

4. Create a stage with a meaningful stage name such as "test" or "dev" and deploy the API.
> Make a note of the invoke url which will be referred as `<invoke_url>`.

### Kafka REST Proxy
In order to consume data using MSK from the API created, we will need to download some additional packages on a client EC2 machine, that will be used to communicate with the MSK cluster.

1. Download the ==Confluent.io Amazon S3 Connector package== to consume data using MSK from the API, on the EC2 instance, using the command below. More information about this package can be found [here](https://github.com/aws/aws-msk-iam-auth).

```bash
sudo wget https://packages.confluent.io/archive/7.2/confluent-7.2.0.tar.gz
tar -xvzf confluent-7.2.0.tar.gz 
```
2. Configure the REST proxy to communicate with the MSK cluter and perform IAM authentication.
- Navigate to `confluent-7.2.0/etc/kafka-rest` and modify the file `kafka-rest.properties` where it should contain the code below.
- Note: You need to replace the `<ZookeeperString>, <BoostrapServerString> and <awsRoleARN>` with the appropriate strings that you took note of earlier.

```bash
id=kafka-rest-test-server

# The host and port for the REST Proxy to listen on.
listeners=http://0.0.0.0:8082

#Zookeeper and Bootstrap strings
zookeeper.connect=<ZookperString>
bootstrap.servers=<BootstrapServerString>

# Sets up TLS for encryption and SASL for authN.
client.security.protocol = SASL_SSL

# Identifies the SASL mechanism to use.
client.sasl.mechanism = AWS_MSK_IAM

# Binds SASL client implementation.
client.sasl.jaas.config = software.amazon.msk.auth.iam.IAMLoginModule required awsRoleArn="<awsRoleARN>";

# Encapsulates constructing a SigV4 signature based on extracted credentials.
# The SASL client bound by "sasl.jaas.config" invokes this class.
client.sasl.client.callback.handler.class = software.amazon.msk.auth.iam.IAMClientCallbackHandler
```

3. Start the REST proxy.
- Navigate to `confluent-7.2.0/bin` and run the following command:

```bash
./kafka-rest-start /home/ec2-user/confluent-7.2.0/etc/kafka-rest/kafka-rest.properties
```
> Note: If everything works so far, you should see the **INFO Server started, listening for requests...** in your EC2 console. Which means the resources are setup to receive data from the API and store it in the S3 bucket.

### Databricks
1. Create a Databricks account in order to query the batch data that are in the S3 bucket.
2. Ensure proper access from Databricks account to S3 bucket.
3. Create a cluster under the "Compute" section.

The figure below shows how it should be set up.

<div align="center">
  <img src="/images/databricks-compute-config.png" alt="Databricks_Compute_Configure">
</div>

4. Connect S3 bucket to Databricks
- Create an access key and a secret access key for Databricks in AWS
    - This can be found under IAM User -> "Security Credentials"
    - Download the keys in a file named `authentication_credentials.csv`
- Mount AWS S3 bucket to Databricks.
    - Upload the file on Databricks and check if the file has been uploaded by running this command in a notebook
    ```bash
    dbutils.fs.ls("/FileStore/tables/")
    ```
    - Run the code below in a notebook to read the AWS keys to databricks
    ```python
    # pyspark functions
    from pyspark.sql.functions import *
    # URL processing
    import urllib

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
    ```

    - Extract and encode the access keys using `urllib.parse.quote`, by running the following command.
    ```python
    # Get the AWS access key and secret key from the spark dataframe
    ACCESS_KEY = aws_keys_df.where(col('User name')=='databricks-user').select('Access key ID').collect()[0]['Access key ID']
    SECRET_KEY = aws_keys_df.where(col('User name')=='databricks-user').select('Secret access key').collect()[0]['Secret access key']
    # Encode the secrete key
    ENCODED_SECRET_KEY = urllib.parse.quote(string=SECRET_KEY, safe="")
    ```
    - Mount S3 bucket using **S3 Bucket Name** into a desired mount name `mnt/s3-bucket` using `dbutils.fs.mount()`.
    ```python
    # AWS S3 bucket name
    AWS_S3_BUCKET = "<user-<UserID>-bucket>"
    # Mount name for the bucket
    MOUNT_NAME = "/mnt/s3_bucket"
    # Source url
    SOURCE_URL = "s3n://{0}:{1}@{2}".format(ACCESS_KEY, ENCODED_SECRET_KEY, AWS_S3_BUCKET)
    # Mount the drive
    dbutils.fs.mount(SOURCE_URL, MOUNT_NAME)
    ```
>If successful, the code will output **True** and you will only need to mount it once before accessing it on Databricks at any time.

5. Read JSON files from mounted S3 bucket
- Read the contents inside the S3 bucket as JSON and store it in a dataframe. The following command will output the following 3 dataframes for each topics:
    - `df_pin` for the pinterest post data
    - `df_geo` for the geolocation data
    - `df_user` for the user data.

> Note: Each path to the JSON objects should be the same as seen in your S3 bucket (e.g `topics/<UserID>.pin/partition=0/`).

```python
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
    return spark.read.format(file_type) \
        .option("inferSchema", infer_schema) \
        .load(file_location)

df_pin = create_spark_dataframe(pin_file_location)
df_geo = create_spark_dataframe(geo_file_location)
df_user = create_spark_dataframe(user_file_location)

# Display Spark dataframe to check its content
display(df_pin)
display(df_geo)
display(df_user)
```

**Optional:** To unmount the S3 bucket, run the following command:
```python
dbutils.fs.unmount("/mnt/s3_bucket")
```


## Usage Instructions

1. In the `user_posting_emulation.py` script, replace the `invoke_url` with your own url that you have saved previously.
2. Run the script to begin emulating user postings and send the data to the S3 bucket where it is then available on Databricks for analysis.



## File Structure

|-- Pinterest Data Pipeline
    Local Machine
    |-- user_posting_Emulation.py

    EC2 Instance
    |-- kafka_folder
        |-- bin
            |-- client.properties
        |-- libs
            |-- aws-msk-iam-auth-1.1.5-all.jar
    |-- kafka-connect-s3
        |-- confluentinc-kafka-connect-s3-10.0.3.zip
    |-- confluent-7.2.0
        |-- etc
            |-- kafka-rest
                |-- kafka-rest.properties



## License Information
This project is owned by AiCore and was part of an immersive program with specialisation, Data Engineering. AiCore is a specialist ai & data career accelerator from which I completed several industry-level projects to gain vital experience and be qualified in the use of several technologies.