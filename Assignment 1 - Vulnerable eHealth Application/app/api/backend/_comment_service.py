from typing import Union

from ._db_service import DBService
from models import Comment

class CommentDBService(DBService):
    def __init__(self, db_config):
        super().__init__(db_config, 'comments')

    def deserialize(self, data) -> Union[Comment, None]:
        if ('id' and 'author' and 'email' and 'text') in data:
            id = int(data['id'])
            author = data['author']
            email = data['email']
            text = data['text']
            return Comment(id, author, email, text)
        return None

    def put(self, comment: Comment) -> None:
        data = comment.serialize
        self.db.command(f"INSERT INTO `comments` (`author`, `email`, `text`) VALUES ('{data['author']}', '{data['email']}', '{data['text']}')")