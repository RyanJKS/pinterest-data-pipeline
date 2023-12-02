import sqlalchemy
from sqlalchemy import text


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
    
    def fetch_data(self, query):
        engine = self.create_db_connector()
        with engine.connect() as connection:
            result = connection.execute(text(query))
            return [dict(row) for row in result]
