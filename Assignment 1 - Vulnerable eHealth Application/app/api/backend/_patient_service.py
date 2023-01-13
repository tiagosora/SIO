from typing import Union

from models import Patient

from ._db_service import DBService


class PatientDBService(DBService):
    def __init__(self, db_config):
        super().__init__(db_config, 'patients')

    def deserialize(self, data) -> Union[Patient, None]:
        if ('id' and 'name' and 'email' and 'password' and 'phone' and 'profile_pic') in data:
            id = int(data['id'])
            name = data['name']
            email = data['email']
            password = data['password']
            phone = data['phone']
            profile_pic = data['profile_pic']
            return Patient(id, name, email, password, phone, profile_pic)
        return None

    def put(self, patient: Patient):
        data = self.serialize(patient)
        if data['profile_pic'] is None:
            self.db.command(f"INSERT INTO `patients` (`name`, `email`, `password`, `phone`) VALUES ('{data['name']}', '{data['email']}', '{data['password']}', '{data['phone']}')")
        else: 
            self.db.command(f"INSERT INTO `patients` (`name`, `email`, `password`, `phone`, `profile_pic`) VALUES ('{data['name']}', '{data['email']}', '{data['password']}', '{data['phone']}', '{data['profile_pic']}')")
