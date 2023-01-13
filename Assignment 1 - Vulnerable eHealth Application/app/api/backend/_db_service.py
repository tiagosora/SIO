from abc import ABC, abstractmethod
from typing import Union, Any

from models._model import Model
from db import Database


class DBService(ABC):
    """
    DBService abstract class
    Base class for all services
    Each subclass is responsible for handling the business of a certain table
    """

    def __init__(self, db_config, table_name: str):
        """
            db: Database
            table_name: str
        
        constructor for a dbservice for a certain table
        returns nothing
        """
        self.db = Database(db_config)
        self.db_config = db_config
        self.table_name = table_name


    def serialize(self, model: Model):
        """
            model: Model

        serializes the model given
        returns a dic
        """
        return model.serialize


    @abstractmethod
    def deserialize(self, data):
        """
            model: dict

        deserializes the dic given into a model
        returns a model instance
        """
        return None


    def get(self, column: Union[str, None]=None, value: Union[str, None]=None, one=False) -> Union[None, Model, list]:
        """
            param: Any

        gets the db object(s) that match value in specified column
        if one is true, returns only 1st object
        returns a model subclass instance
        """
        if column is None: query_str = ''
        else: query_str = f"WHERE `{column}`='{value}'"

        data = self.db.query(f"SELECT * FROM `{self.table_name}` {query_str}", one)
        #print(data, '\n\n\n\n\n\n\n\n\n') # gostava de saber quem foi o génio que espetou aqui isto, Eu ass: PP

        if data is None: return None

        if type(data) != list:
            return self.deserialize(data)

        instances = [self.deserialize(item) for item in data if self.deserialize(item) is not None]
        return instances


    def get_all(self):
        """
        get all objects of this model subclass, without filter
        returns an iterable of the model subclass
        """
        return self.query(None)


    def query(self, query: Union[str, None], one: bool = False):
        """
            query: str | None
            one: bool = False

        get db objects, filtered by query
        if one == True, returns only the first object
        returns an iterable of model subclass or an instance of model subclass
        """
        query = '' if query is None else "WHERE " + query
        data = self.db.query(f"SELECT * FROM {self.table_name} {query}", one)
        
        if one:
            return self.deserialize(data)

        models = [self.deserialize(item) for item in data if self.deserialize(item) is not None]
        return models


    def exists(self, param: Any) -> bool:
        """
            param: Any

        checks if an object either with field matching param exists (depending on param type)
        returns a boolean
        """
        return self.get(param) is not None