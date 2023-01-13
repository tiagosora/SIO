from typing import Any, Dict
from ._model import Model
from dataclasses import dataclass

@dataclass
class Department(Model):
    name: str     
    
    @property
    def serialize(self)-> Dict[str, Any]:
        serial = super().serialize
        serial.update({
            'name': self.name
        })
        return serial