#!/bin/python

import selectors
import socket
import subprocess
import sys
from datetime import datetime
from logging import Logger

from cryptography import x509
from cryptography.hazmat.backends import default_backend as db
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric.padding import PKCS1v15
from cryptography.hazmat.primitives.hashes import SHA1, Hash

sys.path.append('')
from playingArea import check_certs
from protocol.common import *
from protocol.protocol import BingoProto


class PlayingArea:

    def __init__(self, port):
        self._host = "localhost"
        self._port = port
        
        self.mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.mySocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.mySocket.bind((self._host, self._port))
        self.mySocket.listen(100)

        self.public_key, self.private_key = create_keys()
        self.gameHasStarted = False
        self.nickname = "playarea"
        self.callerIsSet = False
        
        self.userList = {"playarea" : [-1, self.public_key]}        # { nickname : [ sequence, pk ] }
        self.userListSignature = None
        self.certsList = []
        
        self.numberOfPlayers = 0
        self.conn_nickname = {}                                     # { conn : nickname }
        self.nickname_conn = {}                                     # { nickname : conn }

        self.logger = Logger()

        self.sel = selectors.DefaultSelector()
        self.sel.register(self.mySocket, selectors.EVENT_READ, self.accept)

    def accept(self, sock: socket.socket, mask):
        conn, addr = sock.accept()
        conn.setblocking(True)

        if (self.gameHasStarted):
            msg = BingoProto.invalidAuthorization(self.nickname)
            msg, signature = sign(msg, self.private_key)
            self.send_msg(conn, msg, signature)
            conn.close()

        # Wait Authorization Request Message
        msg, data, signature = BingoProto.recv_msg(conn)
        self.logger.log(msg, signature)
        try:
            assert msg.command == "authorizationRequest"
            user_type = msg.user_type
            nickname  = msg.nickname
            public_key = serialization.load_pem_public_key(msg.pk)
            cert = msg.cert
            if cert in self.certsList:
                print("Duplicated CC")
                error_msg = "There's already a user in the game with the given Citizen Card."
                msg = BingoProto.invalidAuthentication(self.nickname, error_msg) 
                msg, signature = sign(msg, self.private_key)
                self.send_msg(conn, msg, signature)
                conn.close()
                return 
            else: 
                self.certsList.append(cert)
        except: # Send Invalid Authorization Response
            msg = BingoProto.invalidAuthorization(self.nickname)
            msg, signature = sign(msg, self.private_key)
            self.send_msg(conn, msg, signature)
            conn.close()
            return

        # Validate CC
        if self.validate_cc(cert, pickle.dumps(msg.dic()), signature): # Send Valid Authorization Response
            print("Valid Portuguese Citizen Card added")
            msg = BingoProto.validAuthorization(self.nickname, public_key_bytes(self.public_key))
            msg, signature = sign(msg, self.private_key)
            self.send_msg(conn, msg, signature)
        else: # Send Invalid Authorization Response
            print("Invalid Portuguese Citizen Card added")
            msg = BingoProto.invalidAuthorization(self.nickname)
            msg, signature = sign(msg, self.private_key)
            self.send_msg(conn, msg, signature)
            conn.close()
            return

        # Set caller / Add player
        if nickname not in self.userList.keys():
            if user_type == "caller":
                if self.check_caller(cert) == True:
                    if self.callerIsSet == False:
                        sequence = 0
                        self.userList[nickname] = [sequence, public_key]
                        self.conn_nickname[conn] = nickname
                        self.nickname_conn[nickname] = conn
                        self.sel.register(conn, selectors.EVENT_READ, self.read)
                        self.callerIsSet = True
                        print("Caller Added")
                    else:
                        print("Duplicated Caller")
                        error_msg = "There's already a caller in this game. Please enter as a player."
                        msg = BingoProto.invalidAuthentication(self.nickname, error_msg) 
                        msg, signature = sign(msg, self.private_key)
                        self.send_msg(conn, msg, signature)
                        conn.close()
                else:
                    # CC invalid for caller
                    print("Invalid CC for Caller")
                    error_msg = "The Citizen Card provided is not valid for a caller."
                    msg = BingoProto.invalidAuthentication(self.nickname, error_msg) 
                    msg, signature = sign(msg, self.private_key)
                    self.send_msg(conn, msg, signature)
                    conn.close()
            else:
                self.numberOfPlayers += 1
                sequence = self.numberOfPlayers
                self.userList[nickname] = [sequence, public_key]
                self.conn_nickname[conn] = nickname
                self.nickname_conn[nickname] = conn
                self.sel.register(conn, selectors.EVENT_READ, self.read)
                print("Player Added")
        else:
            print("Duplicated Nickname")
            error_msg = "Nickname already in use. Please enter the game again with a new one."
            msg = BingoProto.invalidAuthentication(self.nickname, error_msg) 
            msg, signature = sign(msg, self.private_key)
            self.send_msg(conn, msg, signature)
            conn.close()

    def validate_cc(self, cert, msg, signature):
        cert = x509.load_pem_x509_certificate(cert)
        today = datetime.today()
        # Verificar validade do certificado
        if today < cert.not_valid_before or today > cert.not_valid_after:
            result = False
        # Verificar validade da assinatura
        else:
            md = Hash(SHA1(), backend=db())
            md.update(msg)
            digest = md.finalize()

            try:
                cert.public_key().verify(
                    signature,
                    digest,
                    PKCS1v15(),
                    SHA1()
                )
                result = True
            except:
                result = False
        return result

    def check_caller(self, cert):
        result = check_certs.certs(cert)
        return result

    def read(self, conn: socket.socket, mask):
        try:
            msg, data, sender_signature = BingoProto.recv_msg(conn)
            self.logger.log(msg, sender_signature)
            if msg and verify_pk(data, sender_signature, self.userList[msg.sender][1]):
                print("-" * 30, "New Message Received", "-" * 30)

                try:
                    if msg.command == "auditLogRequest":
                        logs = self.logger.get_logs()
                        msg = BingoProto.auditLogResponse(self.nickname, logs)
                        msg, signature = sign(msg, self.private_key)
                        self.send_msg(conn, msg, signature)

                    elif msg.command == "userListRequest":
                        print("Sending Users List")
                        msg = BingoProto.userListResponse(self.nickname, self.userList, self.userListSignature)
                        msg, signature = sign(msg, self.private_key)
                        self.send_msg(conn, msg, signature)

                    elif msg.command == "start":
                        print("Game is starting, sending the users list to all players!")
                        user_List_msg = BingoProto.userListResponse(self.nickname, self.userList, self.userListSignature)
                        user_List_msg, signature = sign(user_List_msg, self.private_key)
                        for other_conn in self.conn_nickname.keys():
                            if other_conn != conn:
                                self.send_msg(other_conn, user_List_msg, signature)

                        print("Redirecting start message to all players")
                        new_msg = pickle.dumps(msg.dic())
                        for other_conn in self.conn_nickname.keys():
                            if other_conn != conn:
                                self.send_msg(other_conn, new_msg, sender_signature)

                        self.gameHasStarted = True

                    elif msg.command == "userListSigning":
                        trans = translateKeys(msg.final_user_list)
                        if verify_pk(pickle.dumps(msg.final_user_list), msg.user_list_sig, trans[msg.sender][1]):
                            self.userListSignature = msg.user_list_sig
                            self.userList = trans

                            print("Users List changed, forwarding to every player!")
                            user_List_msg = BingoProto.userListResponse(self.nickname, self.userList, self.userListSignature)
                            user_List_msg, signature = sign(user_List_msg, self.private_key)
                            for player_conn in self.conn_nickname.keys():
                                if player_conn != conn:
                                    print(self.conn_nickname[player_conn])
                                    self.send_msg(player_conn, user_List_msg, signature)

                    elif msg.command == "deckSend":
                        print("Redirecting deckSend message to the next player")
                        
                        order = sorted([seq[0] for seq in self.userList.values() if seq[0] > -1])
                        sender_sequence = order[self.userList[msg.sender][0]]
                        try:
                            next_player_sequence = order[sender_sequence+1]
                        except:
                            next_player_sequence = 0

                        next_nickname = None
                        for nickname, lst in self.userList.items():
                            if lst[0] == next_player_sequence:
                                next_nickname = nickname

                        new_msg = pickle.dumps(msg.dic())
                        player_conn = self.nickname_conn[next_nickname]
                        self.send_msg(player_conn, new_msg, sender_signature)
                        
                    elif msg.command == "deckShare":
                        print("Redirecting deckShare message to all users")
                        new_msg = pickle.dumps(msg.dic())
                        [self.send_msg(pconn, new_msg, sender_signature) for pconn in self.conn_nickname.keys() if pconn != conn]

                    elif msg.command == "cardShare":
                        print("Redirecting cardShare message to all users")
                        new_msg = pickle.dumps(msg.dic())
                        [self.send_msg(pconn, new_msg, sender_signature) for pconn in self.conn_nickname.keys() if pconn != conn]

                    elif msg.command == "kick":
                        nick = msg.nick
                        print(nick + " was kicked from the session.")
                        msg = pickle.dumps(msg.dic())
                        [self.send_msg(pconn, msg, sender_signature) for pconn in self.conn_nickname.keys() if pconn != conn]
                        del self.conn_nickname[self.nickname_conn[nick]]
                        c = self.nickname_conn.pop(nick)
                        c.close()
                        if len(self.userList) <= 2:
                            print("We no longer have players for this. Play Area out.")
                            exit(1)

                    elif msg.command == "keyShare":
                        print("Redirecting keyShare message to all users")
                        new_msg = pickle.dumps(msg.dic())
                        [self.send_msg(pconn, new_msg, sender_signature) for pconn in self.conn_nickname.keys() if pconn != conn]

                    elif msg.command == "resultsSend":
                        print("Redirecting resultsSend message to the caller")
                        new_msg = pickle.dumps(msg.dic())
                        [self.send_msg(pconn, new_msg, sender_signature) for pconn in self.conn_nickname.keys() if pconn != conn]

                    else:
                        print("ERROR: Unknown Command!")

                except Exception as e:
                    print('Houve um problema no envio da mensagem!')
                    print("Erro:", e)
                
                print("-" * 82)
            
            else:
                print('ALERT! Invalid Signature, telling caller to kick the player!')
                self.userList.pop(self.conn_nickname[conn])
                self.nickname_conn.pop(self.conn_nickname[conn])
                self.conn_nickname.pop(conn)
                self.sel.unregister(conn)
                conn.close()

        except Exception as e:
            print('Mensagem inválida recebida, desconectando', conn) 
            print("Erro:", e)
            print("-" * 82)
            self.userList.pop(self.conn_nickname[conn])
            self.nickname_conn.pop(self.conn_nickname[conn])
            self.conn_nickname.pop(conn)
            self.sel.unregister(conn)
            conn.close()

    def loop(self):
        """Run until canceled."""
        print("Playing Area Running\n")
        while True:
            events = self.sel.select()
            for key, mask in events:
                callback = key.data
                callback(key.fileobj, mask)

    def send_msg(self, conn, msg, sig):
        BingoProto.send_msg(conn, msg, sig)
        msg = pickle.loads(msg)
        self.logger.log(msg, sig)


def main():
    if len(sys.argv) != 2:
        print('Usage: %s port'%(sys.argv[0]))
        sys.exit(1)

    port = int(sys.argv[1])

    playingArea = PlayingArea(port)
    playingArea.loop()

if __name__ == "__main__":
    main()


