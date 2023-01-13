from typing import Union

from datetime import date

from ._db_service import DBService
from ._patient_service import PatientDBService
from ._doctor_service import DoctorDBService
from ._department_service import DepartmentDBService
from models import Appointment, Patient, Doctor, Department

class AppointmentDBService(DBService):
    def __init__(self, db_config):
        super().__init__(db_config, 'appointments')

    def deserialize(self, data) -> Union[Appointment, None]:
        if('id' and 'patient_id' and 'department_id' and 'doctor_id' and 'date' and 'message') in data:
            id = int(data['id'])
            patient = PatientDBService(self.db_config).get("id", data['patient_id'], True)
            department = DepartmentDBService(self.db_config).get("id", data['department_id'], True)
            doctor = DoctorDBService(self.db_config).get("id", data['doctor_id'], True)
            date_ = data['date']
            message = data['message']
            return Appointment(id, patient, department, doctor, date_, message)
        return None

    def put(self, appointment: Appointment) -> None:
        data = self.serialize(appointment)
        self.db.command(f"INSERT INTO `appointments` (`patient_id`, `doctor_id`, `department_id`, `date`, `message`) VALUES ('{data['patient_id']}', '{data['doctor_id']}, '{data['department_id']}', '{data['date']}', '{data['message']}'")
