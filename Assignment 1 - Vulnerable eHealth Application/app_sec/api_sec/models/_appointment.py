from datetime import date
from typing import Any, Dict
from ._model import Model
from ._patient import Patient
from ._doctor import Doctor
from ._department import Department
from dataclasses import dataclass

@dataclass
class Appointment(Model):
    patient: Patient       # TODO para comentar tem de estar loggado ou pode ser qualquer um?
    doctor: Doctor # Doctor, Diagnostic, Psychological 
    department: Department # Departments, Diagnostic, Psychological
    date: date
    message: str

    @property
    def serialize(self)-> Dict[str, Any]:
        
        serial = super().serialize
        serial.update({
            'patient_id': self.patient.id,
            'doctor_id': self.doctor.id,
            'department_id': self.department.id,
            'date': self.date.isoformat(),
            'message': self.message
        })
        print("serializeiiii ", serial)
        return serial