from sqlalchemy import text
import sqlalchemy
import yaml


class AWSDBConnector:
    """
    A connector class to create a connection to an AWS RDS instance.
    """
    def __init__(self, yaml_file_path='db_creds.yaml'):
        """
        Initializes the database connection parameters.
        """
        self.db_creds = self.read_db_creds(yaml_file_path)
        
    def read_db_creds(self, yaml_file_path) -> dict:
        """
        The function `read_db_creds` reads the contents of a YAML file containing database credentials and
        returns them as a dictionary.
        :return: a dictionary containing the data read from the 'db_creds.yaml' file.
        """
        try:
            with open(yaml_file_path, 'r') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            raise Exception(f"YAML file {yaml_file_path} not found")
        except yaml.YAMLError as e:
            raise Exception(f"Error reading YAML file: {e}")
    
    def create_db_connector(self):
        """
        Creates a database engine using SQLAlchemy.
        
        Returns:
            engine: A SQLAlchemy engine instance connected to the database.
        """
        USER = self.db_creds['USER']
        PASSWORD = self.db_creds['PASSWORD']
        ENDPOINT = self.db_creds['HOST']
        PORT = self.db_creds['PORT']
        DATABASE = self.db_creds['DATABASE']
        
        engine = sqlalchemy.create_engine(f"mysql+pymysql://{USER}:{PASSWORD}@{ENDPOINT}:{PORT}/{DATABASE}?charset=utf8mb4")
        return engine
    
    def fetch_data(self, query):
        engine = self.create_db_connector()
        with engine.connect() as connection:
            result = connection.execute(text(query))
            return [dict(row) for row in result]
