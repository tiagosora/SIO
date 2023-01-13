from typing import Union

from ._db_service import DBService
from models import Department

class DepartmentDBService(DBService):
    def __init__(self, db_config):
        super().__init__(db_config, 'departments')

    def deserialize(self, data) -> Union[Department, None]:
        if ('id' and 'name') in data:
            id = int(data['id'])
            name = data['name']
            return Department(id, name)
        return None