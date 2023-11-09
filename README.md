# Pinterest Data Pipeline

## Table of Contents
1. [Project Description](#project-description)
2. [Installation Instructions](#installation-instructions)
3. [Usage Instructions](#usage-instructions)
4. [File Structure](#file-structure)
5. [License Information](#license-information)

## Project Description
The Pinterest Data Pipeline project is designed to emulate the process of gathering and storing user posting data, similar to what platforms like Pinterest might do. The aim is to understand how data can be efficiently collected, processed, and stored in a cloud environment, specifically using AWS services. By diving into this project, I gained a hands-on experience with various AWS services and data processing tools which in turn gave me a taste of what it's like to work on real-world data engineering tasks.

Below is a visual representation of the project's architecture:

<div align="center">
  <img src="/images/CloudPinterestPipeline.png" alt="CloudPinterestPipeline">
</div>


### Project Aim:
The primary goal of this project is to provide hands-on experience with setting up and managing a data pipeline. It offers insights into how large-scale applications like Pinterest handle vast amounts of data, ensuring it's processed efficiently and stored securely. The aim is to create a robust data pipeline that enables me to:

- **Collect Pinterest Data:** Set up a system to capture data from Pinterest, including posts, geolocation information, and user data.

- **Process Data with Kafka:** Use Apache Kafka to efficiently process the incoming data, ensuring smooth data flow and scalability.

- **Store Data in S3:** Store the processed data in an Amazon S3 bucket, making it readily accessible for further analysis.

- **Enable API Integration:** Create an API to stream data to the Kafka cluster and subsequently store it in the S3 bucket.

- **Analyze Data with Databricks:** Connect Databricks to my S3 bucket to perform batch data analysis on the collected Pinterest data.

- **Orchestrate Workflows with MWAA:** Use Managed Workflows for Apache Airflow (MWAA) to orchestrate complex workflows using Directed Acyclic Graphs (DAGs), enhancing the automation and monitoring of the data pipeline.

- **Integrate Kinesis Data Streams:** Expand the pipeline to include real-time data handling with AWS Kinesis Data Streams.

### What I learned:
Through the development and implementation of this project, I have gained hands-on experience with several important concepts and tools used in the world of data engineering and cloud computing:

- **AWS Services:** I have become familiar with Amazon Web Services, including IAM, VPC, EC2, and S3, and understand how to set up roles and permissions.

- **Apache Kafka:** I learned how to install, configure, and use Kafka on an EC2 instance for real-time data streaming and processing.

- **MSK Cluster:** I explored Amazon Managed Streaming for Apache Kafka (MSK) to create and manage Kafka clusters on AWS.

- **API Gateway:** I understood how to create and configure an API using AWS API Gateway for data streaming.

- **Kafka REST Proxy:** I set up a Kafka REST Proxy for easy communication with my Kafka cluster, and learned about IAM authentication.

- **Apache Spark:** I learned how to make a clusters, mount S3 buckets, assume IAM roles, store data in metastore, clean and query data for analysis in databricks.

- **Databricks:** I used Databricks to analyze and query data stored in my S3 bucket, gaining insights from the collected Pinterest data.

- **Apache Airflow (MWAA):** I've learned to create and manage an Airflow environment, orchestrate workflows using DAGs, and integrate with Databricks for workload automation, which has significantly enhanced my understanding of workflow management in cloud environments.

- **AWS Kinesis Data Streams:** Acquired skills in real-time data streaming and management using AWS Kinesis.

#### Databricks Cleaning and Analysis
In this project, data cleaning was performed in **Databricks** using **Spark**, followed by the application of **SQL** queries for insightful analysis. Here is a list of tasks executed, along with a few examples of the extracted information.

> Note: Task 1-3 was for cleaning the data and more details can be found in `data_cleaning.py` file

- Task 4: Find the most popular category in each country
- Task 5: Find which was the most popular category each year

Query: 
```sql
SELECT
    YEAR(geo.timestamp) AS post_year,
    pin.category,
    COUNT(*) AS category_count
FROM global_temp.df_geo_temp_view AS geo
JOIN global_temp.df_pin_temp_view AS pin
    ON geo.ind = pin.ind
WHERE
    YEAR(geo.timestamp) BETWEEN 2018 AND 2022
GROUP BY
    YEAR(geo.timestamp), pin.category
ORDER BY
    post_year DESC, category_count DESC
```
Output:
| post_year       | category    | category_count  | 
|:-------------:|:-------------:| :-------------:| 
| 2022           |    beauty   |    8           |
| 2022           | christmas    |   8           |
| 2021           | finance      | 23            |

- Task 6: Find the user with most followers in each country
- Task 7: Find the most popular category for different age groups
- Task 8: Find the median follower count for different age groups

Query:
```sql
WITH AgeGroupCategories AS (
    SELECT
        CASE
            WHEN users.age >= 18 AND users.age <= 24 THEN '18-24'
            WHEN users.age >= 25 AND users.age <= 35 THEN '25-35'
            WHEN users.age >= 36 AND users.age <= 50 THEN '36-50'
            WHEN users.age > 50 THEN '50+'
        END AS age_group,
        pin.follower_count
    FROM global_temp.df_user_temp_view AS users
    JOIN global_temp.df_pin_temp_view AS pin 
        ON users.ind = pin.ind
)
SELECT
    age_group,
    percentile_approx(follower_count, 0.5) AS median_follower_count
FROM AgeGroupCategories
GROUP BY age_group
ORDER BY age_group;
```

Output:
| age_group     | median_follower_count | 
|:-------------:|:--------------------: | 
| 18-24         | 171000                |
| 25-35         | 46000                 |
| 36-50         | 3000                  |
| 50+           | 3000                  |

- Task 9: Find how many users have joined each year?
- Task 10: Find the median follwoer count of users based on thei joining year
- Task 11: Find the median follower count of users based on their joining year and age group

## Installation Instructions

#### Prerequisites
- Python 3.x
- Required Python Packages (SQLAlchemy, PyMySQL)
- Knowledge of Linux OS/ Windows WSL and AWS services

First start by cloning the repository to your local machine.
```bash
git clone https://github.com/RyanJKS/pinterest-data-pipeline.git
```

### AWS Setup (IAM, VPC & EC2)
1. Create an AWS account (For this project, the region was set to 'us-east-1') 

2. Create an IAM user using the Principle of Least Priviledge
> Note: The IAM User's username will be denoted as `<UserID>` to align with common naming conventions used by companies in the software development lifecycle.

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
2. Install the <mark>IAM MSK authentication package</mark> in the `kafka_2.12-2.8.1/libs` on your client EC2 machine. This package is necessary to connect to MSK clusters that require IAM authentication.

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

5. Create Kafka Topics. Navigate to `kafka_2.12-2.8.1/bin` and run the following command, replacing **BootstrapServerString** with the connection string previously save and `<topic_name>` with the following:

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

- Connect to EC2 instance and download the <mark>Confluent.io Amazon S3 Connector</mark> in a folder called `kafka-connect-s3`.
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

1. Download the <mark>Confluent.io Amazon S3 Connector package</mark> to consume data using MSK from the API, on the EC2 instance, using the command below. More information about this package can be found [here](https://github.com/aws/aws-msk-iam-auth).

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

4. IAM Authentication credentials in Databricks
- Download the access key and a secret access key for Databricks in AWS
    - This can be found under IAM User -> "Security Credentials"
    - Download the keys in a file named `authentication_credentials.csv`
    - Upload the file on Databricks.

5. Mount S3 bucket and querying data in Databricks
    - Run the code found in `mount_s3_to_databricks.py` in a notebook in databricks.
    
    - This code within the file serves the following purposes:
        - It reads AWS access keys from a notebook in Databricks and encodes them using the `urllib.parse.quote` function.

        - It mounts an AWS S3 bucket with a specified name (`S3 Bucket Name`) into a desired mount location (`mnt/s3-bucket`) using `dbutils.fs.mount()`. You need to replace `AWS_S3_Bucket` with your chosen bucket name in the code. If successful, the code will return `True`. You will only need to perform this mount operation once to access the S3 bucket in Databricks.


### Managed Workflows for Apache Airflow (MWAA)
Create an Airflow environment to orchestrate complex workflows using **Directed Acyclic Graphs (DAGs)**. These workflows will manage tasks like data processing, analysis, and storage.

Step 1: S3 Bucket Configuration for MWAA
- Create an S3 bucket named `mwaa-dags-bucket` and create a folder called `dags` in this bucket. Ensure the following settings:
    - Region set to `us-east-1`.
    - Public access blocked for security.
    - Enable bucket versioning to keep track of and manage deployments.

> Note: Make a note of the S3 bucket's URI for later use.

Step 2: MWAA Environment Setup
- In the AWS console, initiate the creation of an MWAA environment called Databricks-Airflow-env.
    - **Networking:** Choose "Create MWAA VPC" option for automatic VPC and subnet creation.
    - **Web Server Access:** Set the webserver access mode to a private network for enhanced security.
    - **Security:** Choose "Create new security group" to define security rules specific to this environment.
    - **Environment Size:** Select a size that can comfortably sustain your projected workload.

Step 3: Airflow UI Access
- Post-environment creation, access the Airflow UI through the AWS Console using the "Open Airflow UI" button. This interface will display all DAGs present in the mwaa-dags-bucket.

Step 4: Integration with Databricks
- For orchestrating Databricks workloads:
    - Generate an API access token in Databricks Create and make a note of this token which will be denoted as `<token_id>`.
    - Within the Airflow UI, navigate to Admin > Connections.
    - Edit the `databricks_default` connection:
        - **Host:** Input your Databricks account URL.
        - **Extra:** Include the following
        ```json
            {"token": "<token_id>", "host": "<url_from_host_column>"}
        ```

    - **Connection Type:** Choose 'Databricks' from the dropdown.

Step 5: Airflow Provider Package (If Required)

If the connection type, "Databricks", is not available, you will need to install additional packages using *Airflow Provider Package*. Create and upload `requirements.txt` file in the S3 `mwaa-dags-bucket` which consists of the python dependency in the MWAA environemnet.

1. The `requirements.txt` should contain the following:
```bash
--constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.6.3/constraints-3.10.txt"

apache-airflow-providers-snowflake==4.2.0
apache-airflow-providers-mysql==5.1.1
apache-airflow[databricks]
```

2. In order to test if the `requirements.txt` file works correctly before uploading it to the MWAA environment, you can build a **docker** image locally  using cli on your machine. This allows you to run a local Airflow environment to develop/test DAGs, custom plugins and dependencies before deploying them to the cloud. Follow the commands below for testing:

    - Clone the `aws-mwaa-local-runner` repo, navigate to the `aws-mwaa-local-runner` folder and build a docker image
    ```bash
    git clone https://github.com/aws/aws-mwaa-local-runner.git

    cd aws-mwaa-local-runner

    ./mwaa-local-env build-image
    ```
    - Once the image is built, run the local Airflow Enviroment using the command below:
    ```bash
    ./mwaa-local-env start
    ```
    - Navigate to `requirements/` where you will find an intial `requirements.txt` file. You need to add the following in that file:
    ```bash
    apache-airflow[databricks]
    ```
    - Test that the `requirements.txt` file works without running Airflow by using the following command:
    ```bash
    ./mwaa-local-env test-requirements
    ```
    - If everything ran successfully, you can now upload the `requirements.txt` file to the MWAA environment.

3. Navigate to the MWAA console and select your **Environment**. Once you're on the environment page select **Edit**. Under the DAG code in Amazon S3, update your Requirements file field by selecting the path corresponding to the `requirements.txt` file you have just uploaded to the S3 bucket.


### AWS Kinesis Data Streams

Step 1: Create Data Streams
- Navigate to the Kinesis console and create three data streams with the specified names:
    - `streaming-<UserID>-pin`
    - `streaming-<UserID>-geo`
    - `streaming-<UserID>-user`

Step 2: Set Up IAM Role
- Create an IAM role (`<UserID-kinesis-role>`) with **AmazonKinesisFullAccess** policy and set up trust relationships. Refer to the trust relationship as shown below.

<div align="center">
  <img src="/images/kinesis-role-relationships.png" alt="Kinesis_Role_Relationships">
</div>

> Make a note of the ARN of this role which will be denoted as `<awsKinesisARN>`

Step 3: Integrate API Gateway with Kinesis
- Select your previously created REST API in [API Gateway](#api-gateway)and create a resource named `streams` at path "/" and leave the rest as default settings.

Step 4: Defining Methods
- Add a 'GET' method with an **Action Name**, `ListStreams`, to the `streams` resource with Kinesis integration. Replace the `ARN` at **Execution role** with the your `<awsKinesisARN>`. The image below shows the setup configuration for a method.

<div align="center">
  <img src="/images/kinesis-method.png" alt="Kinesis_GET_Method">
</div>

- Configure the **Integration Request** with the necessary **headers** and **mapping template**. 
- The **headers** should be defined as shown below.

<div align="center">
  <img src="/images/api-headers.png" alt="Kinesis_GET_Method">
</div>

- The **Mapping Template** should be defined as shown below.

<div align="center">
  <img src="/images/mapping-template.png" alt="Mapping_Template">
</div>

Step 5: Define Stream-Specific Methods
- Under the `streams` resource, create a `{stream-name}` resource.
- Set up 'GET', 'POST', and 'DELETE' methods with **Action Name** `DescribeStream`, `CreateStream`, and `DeleteStream`, respectively. Refer back to Step 4 for method setup details. Further adjustments are needed when creating the mapping template and they are shown below.
    - For 'GET' and 'DELETE', insert this in the template body:
    ```json
    { "StreamName": "$input.params('stream-name')" }
    ```
    - For 'POST', insert this in the template body:
    ```java
    {
    "ShardCount": #if($input.path('$.ShardCount') == '') 5 #else $input.path('$.ShardCount') #end,
    "StreamName": "$input.params('stream-name')"
    }
    ```

Step 6: Add Record Handling Methods
- Under `{stream-name}` resource, create `record` and `records` resources.
- Implement 'PUT' methods for both, using the **Action Name** `PutRecord` and `PutRecords`. Refer back to Step 4 for the method setup pattern. Further adjustments are needed when creating the mapping template and they are shown below.
    - For `record` resource's method, insert this in the template body.
    ```json
    {
        "StreamName": "$input.params('stream-name')",
        "Data": "$util.base64Encode($input.json('$.Data'))",
        "PartitionKey": "$input.path('$.PartitionKey')"
    }
    ```
    - For `records` resource's method, insert this in the template body.
    ```java
    {
        "StreamName": "$input.params('stream-name')",
        "Records": [
        #foreach($elem in $input.path('$.records'))
            {
                "Data": "$util.base64Encode($elem.data)",
                "PartitionKey": "$elem.partition-key"
            }#if($foreach.hasNext),#end
            #end
        ]
    }
    ```

Step 7: Deploy and Verify API Structure
- Deploy the API to apply and activate the changes. Confirm the API structure is correct and matches the expected setup as shown below.

<div align="center">
  <img src="/images/api-structure.png" alt="API_Structure">
</div>


## Usage Instructions

### Key Scripts
- `user_posting_emulation.py`: Contains a script that extracts pinterest data from MySQL database and uploads it to an S3 bucket though an API Gateway that goes through an MSK cluster on EC2 instance. The data sent are as follows:
    - `pinterest_data` contains data about posts being updated to Pinterest
    - `geolocation_data` contains data about the geolocation of each Pinterest post found in pinterest_data 
    - `user_data` contains data about the user that has uploaded each post found in pinterest_data
- `user_posting_emulation_streaming.py`: Contains a script that streams real-time data to AWS Kinesis
- `mount_s3_to_databricks.py`: Contains a script which needs to be run on databricks in order to mount the S3 bucket onto databricks and do further analysis.
- `data_cleaning.py`: Contains a script that reads JSON files from the mounted S3 bucket, stores the contents as dataframes and performs cleaning operations.
- `data_cleaning_tools.py`: Contains a script of functions used in `data_cleaning.py` and `stream_and_clean_kinesis_data.py` to clean dataframes.
- `stream_and_clean_kinesis_data.py`: Contains a script to read real-time kinesis data, cleans the data and saves in delta table on databricks.
- `data_query.py`: Contains a script to query the cleaned data for useful information. The full list of task is shown above in [Additional Information](#additional-information) section
- `0a3db223d459_dag.py`: A Dag file which runs the `data_cleaning` notebook file on databricks daily.


### Usage

After completing the installation and setup of all required services, proceed with the following steps to use the data pipeline:

**Data Emulation and Streaming to S3:**
1. Script Configuration: In the `user_posting_emulation.py` script, replace the `invoke_url` with the url created in the **API Gateway**. This links the script to your API endpoint.

2. Starting the REST Proxy: Ensure that your Kafka REST Proxy is active on your EC2 instance. Refer to the [Kafka REST Proxy](#kafka-rest-proxy) section for details on starting the proxy.

3. Run the script: Execute the script to send data to your S3 bucket, which Databricks will use for analysis. Use the command line to run the script:

```python
python3 user_posting_emulation.py
```
If the code outputs a status code "200", it indicates successful data transmission to the S3 bucket. You can verify in the AWS S3 Console under the `<user-UserID-bucket>` bucket.

**Data Processing and Analysis with Databricks:**
1. Script Upload: In your Databricks workspace, upload the scripts located within the `databricks_notebook` folder.

2. Execution Order: Execute the notebooks in the following sequence for data processing:

    - `data_cleaning_tools.py`: To get the data cleaning utilities.
    - `data_cleaning.py`: To apply the cleaning process to the datasets.
    - `data_query.py`: To perform various data analyses and view the results.

If all the notebook ran successfully, it will show the anticipated results from the `data_query.py` notebook for each of the queries.

**Workflow Orchestration with MWAA:**
1. DAG Deployment: Transfer your DAG file, such as `0a3db223d459_dag.py`, to the `mwaa-dags-bucket/dags` folder in your S3 bucket. This will synchronize the file with the Airflow UI.

2. Airflow UI Interaction: Access the Airflow UI from the MWAA section of the AWS console. Here, locate and unpause your DAG to initiate the workflow based on its schedule and configuration.

> Note: Customize the DAG file to fit your environment, paying particular attention to parameters like **notebook_path** and **existing_cluster_id**.

**Real-Time Data Handling with Kinesis:**
1. Kinesis Streaming Script: Modify the `invoke_url` in the `user_posting_emulation_streaming.py` script, similarly to how you updated the `user_posting_emulation.py` script.

2. Run the script: Run the script on your local machine to begin streaming data to your Kinesis data stream:

```python
python3 user_posting_emulation_streaming.py
```

3. Databricks Streaming Notebook: On Databricks, run the `stream_and_clean_kinesis_data.py`` notebook. This will process and display the real-time data stream, cleaning it and storing the output in Delta tables for subsequent use.

By following these detailed steps, you can effectively emulate data generation, process and analyze data in batch and real-time, and orchestrate complex workflows using the comprehensive data pipeline you've established.


## File Structure

|-- Pinterest Data Pipeline

    Local Machine
    |-- dags
        |-- 0a3db223d459_dag.py
    |-- databricks_notebooks
        |-- data_cleaning_tools.py
        |-- data_cleaning.py
        |-- data_query.py
        |-- mount_s3_to_databricks.py
        |-- stream_and_clean_kinesis_data.py
    |-- README.md
    |-- user_posting_emulation_streaming.py
    |-- user_posting_emulation.py
 

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