import pickle
from socket import socket

from cc.pteid import PTeID
from protocol.common import *


class Message:

    def __init__(self, command : str, sender : int):
        self.command = command
        self.sender = sender

    def __repr__(self):
        return f'"command": "{self.command}", "sender" : "{self.sender}"'

    def dic(self):
        return {"command":self.command, "sender" : self.sender}

    def getcommand(self):
        return self.command

class AuthorizationRequestMessage(Message):

    def __init__(self, command : str, sender : str, user_type: str, nickname, pk, cert):
        super().__init__(command, sender)
        self.user_type = user_type
        self.nickname = nickname
        self.pk = pk
        self.cert = cert

    def __repr__(self):
        return f'{{{super().__repr__()}, "user_type": "{self.user_type}", "nickname": "{self.nickname}", "pk": "{self.pk}", "cert": "{self.cert}"}}'

    def dic(self):
        return {"command":super().getcommand(), "sender" : self.sender, "user_type": self.user_type, "nickname": self.nickname, "pk": self.pk, "cert": self.cert}


class ValidAuthorizationMessage(Message):
    
    def __init__(self, command : str, sender : int, pk):
        super().__init__(command, sender)
        self.pk = pk

    def __repr__(self):
        return f'{{{super().__repr__()}, "pk": "{self.pk}"}}'

    def dic(self):
        return {"command":super().getcommand(), "sender" : self.sender, "pk": self.pk}

class InvalidAuthorizationMessage(Message):
    
    def __init__(self, command : str, sender : int):
        super().__init__(command, sender)

    def __repr__(self):
        return f'{{{super().__repr__()}}}'

    def dic(self):
        return {"command":super().getcommand(), "sender" : self.sender}

class InvalidAuthenticationMessage(Message):
    
    def __init__(self, command : str, sender : int, error: str):
        super().__init__(command, sender)
        self.error = error

    def __repr__(self):
        return f'{{{super().__repr__()}, "error": "{self.error}"}}'

    def dic(self):
        return {"command":super().getcommand(), "sender" : self.sender, "error": self.error}

class StartMessage(Message):

    def __init__(self, command : str, sender : int, deck_size : int ):
        super().__init__(command, sender)
        self.deck_size = deck_size

    def __repr__(self):
        return f'{{{super().__repr__()}}}'

    def dic(self):
        return {"command":super().getcommand(), "sender" : self.sender, "deck_size" : self.deck_size}


class CardResquestMessage(Message):
    
    def __init__(self, command : str, sender : int):
        super().__init__(command, sender)

    def __repr__(self):
        return f'{{{super().__repr__()}}}'

    def dic(self):
        return {"command":super().getcommand(), "sender" : self.sender}

class CardShareMessage(Message):
    
    def __init__(self, command : str, sender : int, card):
        super().__init__(command, sender)
        self.card = card

    def __repr__(self):
        return f'{{{super().__repr__()}, "card": "{self.card}"}}'

    def dic(self):
        return {"command":super().getcommand(), "sender" : self.sender, "card":self.card}

class DeckSendMessage(Message):
    def __init__(self, command : str, sender : int, deck):
        super().__init__(command, sender)
        self.deck = deck

    def __repr__(self):
        return f'{{{super().__repr__()}, "deck": "{self.deck}"}}'

    def dic(self):
        return {"command":super().getcommand(), "sender" : self.sender, "deck":self.deck}

class DeckShareMessage(Message):
    def __init__(self, command : str, sender : int, deck, deck_signature, symkey):
        super().__init__(command, sender)
        self.deck = deck
        self.deck_signature = deck_signature
        self.symkey = symkey

    def __repr__(self):
        return f'{{{super().__repr__()}, "deck": "{self.deck}", "deck_signature": "{self.deck_signature}", "symkey": "{self.symkey}"}}'

    def dic(self):
        return {"command":super().getcommand(), "sender" : self.sender, "deck":self.deck, "deck_signature":self.deck_signature, "symkey":self.symkey}

class KeyShareMessage(Message):
    
    def __init__(self, command : str, sender : int, key):
        super().__init__(command, sender)
        self.key = key

    def __repr__(self):
        return f'{{{super().__repr__()}, "key": "{self.key}"}}'

    def dic(self):
        return {"command":super().getcommand(), "sender" : self.sender, "key":self.key}


class AuditLogRequestMessage(Message):

    def __init__(self, command : str, sender : int):
        super().__init__(command, sender)

    def __repr__(self):
        return f'{{{super().__repr__()}}}'

    def dic(self):
        return {"command":super().getcommand(), "sender" : self.sender}

class AuditLogResponseMessage(Message):
    
    def __init__(self, command : str, sender : int, audit_logs):
        super().__init__(command, sender)
        self.audit_logs = audit_logs

    def __repr__(self):
        return f'{{{super().__repr__()}, "audit_logs": "{self.audit_logs}"}}'

    def dic(self):
        return {"command":super().getcommand(), "sender" : self.sender, "audit_logs":self.audit_logs}

class UserListRequestMessage(Message):
    
    def __init__(self, command : str, sender : int):
        super().__init__(command, sender)

    def __repr__(self):
        return f'{{{super().__repr__()}}}'

    def dic(self):
        return {"command":super().getcommand(), "sender" : self.sender}

class UserListResponseMessage(Message):
    
    def __init__(self, command : str, sender: str, users_list : dict, user_list_sig):
        super().__init__(command, sender)
        self.users_list = users_list
        self.user_list_sig = user_list_sig

    def __repr__(self):
        return f'{{{super().__repr__()}, "users_list": "{self.users_list}", "user_list_sig": "{self.user_list_sig}"}}'

    def dic(self):
        return {"command":super().getcommand(), "sender" : self.sender, "users_list":self.users_list, "user_list_sig": self.user_list_sig}

class UserListSigningMessage(Message):

    def __init__(self, command: str, sender: str, final_user_list, user_list_sig):
        super().__init__(command, sender)
        self.user_list_sig = user_list_sig
        self.final_user_list = final_user_list

    def __repr__(self):
        return f'{{{super().__repr__()}, "final_user_list": "{self.final_user_list}", "user_list_sig": "{self.user_list_sig}"}}'

    def dic(self):
        return {"command":super().getcommand(), "sender" : self.sender, "final_user_list": self.final_user_list, "user_list_sig":self.user_list_sig}

class KickMessage(Message):

    def __init__(self, command: str, sender: str, nick):
        super().__init__(command, sender)
        self.nick = nick

    def __repr__(self):
        return f'{{{super().__repr__()}, "nick": "{self.nick}"}}'

    def dic(self):
        return {"command":super().getcommand(), "sender" : self.sender, "nick": self.nick}

class ResultsSendMessage(Message):
    def __init__(self, command : str, sender : int, deck, winners):
        super().__init__(command, sender)
        self.deck = deck
        self.winners = winners

    def __repr__(self):
        return f'{{{super().__repr__()}, "deck": "{self.deck}", "winners": "{self.winners}"}}'

    def dic(self):
        return {"command":super().getcommand(), "sender" : self.sender, "deck" : self.deck, "winners" : self.winners}
    

class BingoProto:

    @classmethod
    def authorizationRequest(cls, sender: str, user_type: str, nickname : str, pk, cert):
        return AuthorizationRequestMessage("authorizationRequest", sender, user_type, nickname, pk, cert)

    @classmethod
    def validAuthorization(cls, sender: str, pk):
        return ValidAuthorizationMessage("validAuthorization", sender, pk)
    
    @classmethod
    def invalidAuthorization(cls, sender: str):
        return InvalidAuthorizationMessage("invalidAuthorization", sender)

    @classmethod
    def invalidAuthentication(cls, sender: str, error: str):
        return InvalidAuthenticationMessage("invalidAuthentication", sender, error)

    @classmethod
    def start(cls, sender: str, deck_size: int):
        return StartMessage("start", sender, deck_size)

    @classmethod
    def cardResquest(cls, sender: str):
        return CardResquestMessage("cardResquest", sender)

    @classmethod
    def cardShare(cls, sender: str, card):
        return CardShareMessage("cardShare", sender, card)
    
    @classmethod
    def deckSend(cls, sender: str, deck : Deck):
        return DeckSendMessage("deckSend", sender, deck)

    @classmethod
    def deckShare(cls, sender: str, deck, deck_signature, symkey):
        return DeckShareMessage("deckShare", sender, deck, deck_signature, symkey)

    @classmethod
    def keyShare(cls, sender: str, key):
        return KeyShareMessage("keyShare", sender, key)

    @classmethod
    def auditLogRequest(cls, sender: str):
        return AuditLogRequestMessage("auditLogRequest", sender)

    @classmethod
    def auditLogResponse(cls, sender: str, audit_logs):
        return AuditLogResponseMessage("auditLogResponse", sender, audit_logs)

    @classmethod
    def userListRequest(cls, sender: str):
        return UserListRequestMessage("userListRequest", sender)

    @classmethod
    def userListResponse(cls, sender: str, user_list : dict, user_list_sig):
        new_user_list = translateKeys(user_list)
        return UserListResponseMessage("userListResponse", sender, new_user_list, user_list_sig)

    @classmethod
    def userListSigning(cls, sender: str, final_user_list, user_list_sig):
        return UserListSigningMessage("userListSigning", sender, final_user_list, user_list_sig)
    
    @classmethod
    def kick(cls, sender: str, nick):
        return KickMessage("kick", sender, nick)

    @classmethod
    def resultsSend(cls, sender: str, deck : Deck, winners: list):
        return ResultsSendMessage("resultsSend", sender, deck, winners)

    @classmethod
    def process_msg(cls, msg : dict):
        command = msg["command"]
        sender = msg["sender"]

        if command == "authorizationRequest":
            user_type = msg["user_type"]
            nickname = msg["nickname"]
            pk = msg["pk"]
            cert = msg["cert"]
            return cls.authorizationRequest(sender, user_type, nickname, pk, cert)

        elif command == "validAuthorization":
            pk = msg["pk"]
            return cls.validAuthorization(sender, pk)
        
        elif command == "invalidAuthorization":
            return cls.invalidAuthorization(sender)

        elif command == "invalidAuthentication":
            error = msg["error"]
            return cls.invalidAuthentication(sender, error)

        elif command == "start":
            deck_size = msg["deck_size"]
            return cls.start(sender, deck_size)

        elif command == "cardResquest":
            return cls.cardResquest(sender)

        elif command == "cardShare":
            card = msg["card"]
            return cls.cardShare(sender, card)

        elif command == "deckSend":
            deck = msg["deck"]
            return cls.deckSend(sender, deck)

        elif command == "deckShare":
            deck = msg["deck"]
            deck_signature = msg["deck_signature"]
            symkey = msg["symkey"]
            return cls.deckShare(sender, deck, deck_signature, symkey)

        elif command == "keyShare":
            key = msg["key"]
            return cls.keyShare(sender, key)

        elif command == "auditLogRequest":
            return cls.auditLogRequest(sender)

        elif command == "auditLogResponse":
            audit_logs = msg["audit_logs"]
            return cls.auditLogResponse(sender, audit_logs)

        elif command == "userListRequest":
            return cls.userListRequest(sender)

        elif command == "userListResponse":
            users_list = msg["users_list"]
            user_list_sig = msg["user_list_sig"]
            return cls.userListResponse(sender, users_list, user_list_sig)

        elif command == "userListSigning":
            sig = msg["user_list_sig"]
            finalUserList = msg["final_user_list"]
            return cls.userListSigning(sender, finalUserList, sig)

        elif command == "kick":
            nick = msg["nick"]
            return cls.kick(sender, nick)

        elif command == "resultsSend":
            deck = msg["deck"]
            winners = msg["winners"]
            return cls.resultsSend(sender, deck, winners)
            

        
    @classmethod
    def recv_msg(cls, connection: socket, public_key=None):
        try:
            headerBytes = connection.recv(2)
            header = int.from_bytes(headerBytes,'big')
            data = connection.recv(header)

            header2Bytes = connection.recv(2)
            header2 = int.from_bytes(header2Bytes,'big')
            signature = connection.recv(header2)
            
            msg = pickle.loads(data)

            return cls.process_msg(msg), data, signature
        except Exception as e:
            # pass
            print("Raising Error on Message Recv")
            print("Error:", e)
            raise BingoProtoBadFormat()

    @classmethod
    def send_msg(cls, connection: socket, msg, signature):
        
        header = len(msg).to_bytes(2, 'big')
        header2 = len(signature).to_bytes(2, 'big')

        try:
            connection.send(header + msg + header2 + signature)
        except Exception as e:
            print("Raising Error on Message Send")
            print(e)
            raise BingoProtoBadFormat()

class BingoProtoBadFormat(Exception):

    def __init__(self, original_msg: bytes=None) :
        self._original = original_msg

    @property
    def original_msg(self):
        return self._original.decode("utf-8") 