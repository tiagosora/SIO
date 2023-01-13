from typing import Dict, Any
from dataclasses import dataclass

from ._model import Model
from ._patient import Patient

@dataclass
class Exam(Model):
    code: str
    patient: Patient
    test_results: str

    @property
    def serialize(self)-> Dict[str, Any]:
        return super().serialize.update({
                'code': self.code,
                'patient_id': self.patient_id,
                'test_results': self.test_results
            })