from typing import Union

from ._db_service import DBService
from ._patient_service import PatientDBService
from models import Patient, Exam
import logging as log

class ExamDBService(DBService):
    def __init__(self, db_config):
        super().__init__(db_config, 'exams')

    def deserialize(self, data) -> Union[Exam, None]:
        if ('id' and 'code' and 'patient_id' and 'test_results') in data:
            id = int(data['id'])
            code = data['code']
            patient = PatientDBService(self.db_config).get("id", data['patient_id'], True)
            test_results = data['test_results']
            return Exam(id, code, patient, test_results)
        return None

    def put(self, patient: Patient) -> None:
        data = self.serialize(patient)
        self.db.command(f"INSERT INTO `comments` (`code`, `patient_id`, `test_results`) VALUES ('{data['code']}, '{data['patient_id']}', '{data['test_results']}')")