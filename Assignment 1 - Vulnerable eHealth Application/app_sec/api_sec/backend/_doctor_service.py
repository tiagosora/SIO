from typing import Union

from ._db_service import DBService
from ._department_service import DepartmentDBService
from models import Doctor, Department

class DoctorDBService(DBService):
    def __init__(self, db_config):
        super().__init__(db_config, 'doctors')

    def deserialize(self, data) -> Union[Doctor, None]:
        if ('id' and 'name' and 'email' and 'password' and 'phone' and 'department_id' and 'profile_pic') in data:
            id = int(data['id'])
            name = data['name']
            email = data['email']
            password = data['password']
            phone = data['phone']
            department = DepartmentDBService(self.db_config).get("id", data['department_id'], True).id
            profile_pic = data['profile_pic']
            return Doctor(id, name, email, password, phone, department, profile_pic)
        return None
