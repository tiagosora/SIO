from dataclasses import dataclass

@dataclass
class Model():
    id: int

    @property
    def serialize(self):
        return { 'id': self.id }