from ._model import Model
from dataclasses import dataclass

@dataclass
class Comment(Model):
    author: str
    email: str
    text: str

    @property
    def serialize(self):
        serial = super().serialize
        serial.update({
                'author': self.author,
                'email': self.email,
                'text': self.text
            })
        return serial