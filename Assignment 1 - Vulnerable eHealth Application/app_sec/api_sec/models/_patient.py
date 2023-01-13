from typing import Any, Dict
from ._model import Model
from dataclasses import dataclass
from flask_login import UserMixin

@dataclass
class Patient(UserMixin, Model):
    name: str
    email: str
    password: str
    phone: str
    profile_pic: str

    @property
    def serialize(self)-> Dict[str, Any]:   
        serial = super().serialize
        serial.update({
            'name': self.name,
            'email': self.email,
            'password':self.password,
            'phone': self.phone,
            'profile_pic': self.profile_pic
        })
        return serial