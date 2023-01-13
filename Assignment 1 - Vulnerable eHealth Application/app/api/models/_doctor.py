from typing import Any, Dict
from ._model import Model
from ._department import Department
from dataclasses import dataclass

@dataclass
class Doctor(Model):
    name: str
    email: str
    password: str
    phone: str
    department: Department
    pic: str

    @property
    def serialize(self)-> Dict[str, Any]:
        return super().serialize.update({
                'name': self.name,
                'email': self.email,
                'password':self.password,
                'phone': self.phone,
                'department_id': self.department.id,
                'profile_pic': self.pic
            })