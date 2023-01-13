#!/bin/python

import fcntl
import os
import selectors
import socket
import sys

from cryptography.hazmat.primitives import serialization

sys.path.append('')
from cc.pteid import PTeID
from playingArea.logging import LogReader
from protocol.common import *
from protocol.protocol import BingoProto


class Caller:
    
    def __init__(self, port, nickname, deck_size, card):
        self.host = 'localhost'
        self.port = port
        self.deck_size = deck_size
        self.cc_card = card
        self.user_type = "caller"

        self.nickname = nickname
        self.cc = PTeID()

        self.public_key, self.private_key = create_keys() # (public key, private key)
        self.symm_key = os.urandom(32)

        self.deck = None
        self.winners = None

        self.userList = {}                              # { nickname : [ sequence , pk ] }
        self.playersSymKeys = { 0 : self.symm_key }     # { sequencePlayer:int : symKey }
        self.player_cards = {}                          # { nickname : card }
        self.no_cheaters = []                           # [ nickname ]
        self.resultsRecieved = 0

        self.playAreaSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.playAreaSock.connect((self.host, self.port))
            self.playAreaSock.setblocking(True)
        except Exception as e:
            sys.exit(f"\nERROR: Wrong choice of port.\n{e}")

        msg = BingoProto.authorizationRequest(self.nickname, self.user_type, self.nickname, public_key_bytes(self.public_key), self.cc.cert.public_bytes(encoding=serialization.Encoding.PEM))
        bmsg = pickle.dumps(msg.dic())        
        signature = self.cc.signature(bmsg)
        BingoProto.send_msg(self.playAreaSock, bmsg, signature)

        msg, data, signature = BingoProto.recv_msg(self.playAreaSock)
        if (not msg) or msg.command != "validAuthorization":
            print("Invalid Authorization")
            self.playAreaSock.close()
            exit(0)
        else:
            playAreaPk = serialization.load_pem_public_key(msg.pk)
            self.userList["playarea"] = [-1, playAreaPk]
        
        print("Type Start to begin the game!\n")

        self.sel = selectors.DefaultSelector()
        self.sel.register(self.playAreaSock, selectors.EVENT_READ, self.read)

    def read(self, conn, mask):
        try:
            msg, data, signature = BingoProto.recv_msg(conn)
            if msg and verify_pk(data, signature, self.userList[msg.sender][1]):
                print("\n" + "-" * 30, "New Message Received", "-" * 30)

                if msg.command == "invalidAuthentication":
                    error_msg = msg.error
                    print(error_msg)
                    print("-" * 82)
                    self.playAreaSock.close()
                    exit(0)

                if msg.command == "auditLogResponse":
                    lr = LogReader()
                    lr.displayLogs(msg.audit_logs)

                elif msg.command == "userListResponse":
                    self.userList = msg.users_list
                    print("You received the user's list!")
                    for user, lst in self.userList.items():
                        print("Sequence: ",lst[0]," | User: ",user," | Key: ",lst[1])

                if msg.command == "deckSend":
                    print("You received the deck from the last player and encrypted it!")
                    self.deck : Deck = msg.deck
    

                    sign_deck, deck_signature = sign(self.deck, self.private_key)

                    msg = BingoProto.deckShare(self.nickname, sign_deck, deck_signature, self.symm_key)
                    msg, signature = sign(msg, self.private_key)
                    BingoProto.send_msg(self.playAreaSock, msg, signature)
                    print("Sending the signed deck and your symmetric key to everyone!")

                elif msg.command == "cardShare":
                    if msg.card.verify(self.deck_size):
                        self.player_cards[msg.sender] = msg.card
                        print("You received and validated " + msg.sender + "'s player card!")
                    else:
                        print("ALERT! You received " + msg.sender + "'s card, it has a bad card!")
                        self.kick(msg.sender)

                    if len(self.userList.keys()) - 2 == len(self.player_cards.keys()): 
                        self.allCardsReceived = True
                        print("You received all the player's cards!")

                        self.deck = Deck(self.deck_size)
                        self.deck.shuffle()
                        self.deck.encrypt(self.symm_key)
                        print("Deck was generated")

                        msg = BingoProto.deckSend(self.nickname, self.deck)
                        msg, signature = sign(msg, self.private_key)
                        BingoProto.send_msg(self.playAreaSock, msg, signature)
                        self.deck = None
                        print("Deck sent to next player")
                        #AQUI

                elif msg.command == "keyShare":
                    sequence = self.userList[msg.sender][0]
                    self.playersSymKeys[sequence] = msg.key
                    print("You received ",msg.sender,"'s symmetric key!")

                    if len(self.userList)-1 == len(self.playersSymKeys): 
                        print("You have received all the player's symmetric keys!")
                        print("You may now decrypt the deck and check the winners!")

                        sequence = sorted([seq[0] for seq in self.userList.values() if seq[0] > -1], reverse=True)
        
                        print(self.playersSymKeys)
                        try:
                            for seq in sequence:
                                next_symkey = self.playersSymKeys[seq]
                                self.deck.decrypt(next_symkey)

                            self.winners, self.deck = compute_result(self.deck, self.player_cards)
                            print("Our Winners: ",self.winners)

                        except:
                            print("ALERT! Someone screwed up the deck! The game is invalid!")

                elif msg.command == "resultsSend":
                    self.resultsRecieved += 1
                    if (set(self.winners) == set(msg.winners)):
                        if (self.deck.deck == msg.deck.deck):
                            self.no_cheaters.append(msg.sender)
                            print(self.no_cheaters)
                        else:
                            print("This player didn't agree with the deck: ", msg.sender)
                            self.kick(msg.sender)
                    else:
                        print("This player didn't agree with the winners: ", msg.sender)
                        self.kick(msg.sender)

                    if self.resultsRecieved == len(self.playersSymKeys)-1:
                        print("\n",self.winners)
                        print(self.no_cheaters,"\n")
                        if all(winner in self.no_cheaters for winner in self.winners):
                            print("Final Winners: ", self.winners)
                        else:
                            print("After the disqualifications, the winners are: ", end=" ")
                            print([winner for winner in self.winners if winner in self.no_cheaters])

                elif msg.command == "kick":
                    print("ALERT! " + msg.nick + " was kicked from the session.")
                    if msg.nick == self.nickname: exit(1)

                print("-" * 82)

        except Exception as e:
            print('Mensagem inválida recebida, desconectando', conn) 
            print("Erro:", e)
            print("-" * 82)
            self.sel.unregister(conn)
            conn.close()
            exit(0)

    def user_stdin(self, stdin , mask):
        user_input = list(stdin.read().strip().split(" "))
        user_input[0] = user_input[0].upper()
        print("-" * 33, "New User Input", "-" * 33)
        if (user_input[0] == "logs".upper()):
            print("Requesting for Audit Log ")
            msg = BingoProto.auditLogRequest(self.nickname)
            msg, signature = sign(msg, self.private_key)
            BingoProto.send_msg(self.playAreaSock, msg, signature)
            
        elif (user_input[0] == "users".upper()):
            print("Requesting Users List")
            msg = BingoProto.userListRequest(self.nickname)
            msg, signature = sign(msg, self.private_key)
            BingoProto.send_msg(self.playAreaSock, msg, signature)

        elif (user_input[0] == "start".upper()):
            print("Requesting Users List")
            msg = BingoProto.userListRequest(self.nickname)
            msg, signature = sign(msg, self.private_key)
            BingoProto.send_msg(self.playAreaSock, msg, signature)

            msg, data, signature = BingoProto.recv_msg(self.playAreaSock)
            verify_pk(data, signature, self.userList[msg.sender][1])
            self.userList = msg.users_list
            print("Received User list!")
            for user, lst in self.userList.items():
                print("Sequence: ",lst[0]," | User: ",user," | Key: ",lst[1])

            if len(self.userList) < 2:
                print("Not enough players to start game")
            else:
                print("Commiting player data")
                finalUserList = translateKeys(self.userList)
                _, sig = sign(finalUserList, self.private_key)
                msg = BingoProto.userListSigning(self.nickname, finalUserList, sig)
                msg, signature = sign(msg, self.private_key)
                BingoProto.send_msg(self.playAreaSock, msg, signature)

                print("Starting Game")
                msg = BingoProto.start(self.nickname, self.deck_size)
                msg, signature = sign(msg, self.private_key)
                BingoProto.send_msg(self.playAreaSock, msg, signature)

        elif (user_input[0] == "kick".upper()):
            nick = user_input[1]
            if nick in self.userList.keys():
                self.kick(nick)
            else: print(nick + " is not a player!")

        else:
            print("ERROR: Unknown Command!")
            
        print("-" * 82)

    def loop(self):
        orig_fl = fcntl.fcntl(sys.stdin, fcntl.F_GETFL)
        fcntl.fcntl(sys.stdin, fcntl.F_SETFL, orig_fl | os.O_NONBLOCK)

        self.sel.register(sys.stdin, selectors.EVENT_READ, self.user_stdin)

        while True:
            print("logs, users, kick, start")
            sys.stdout.write('> ')
            sys.stdout.flush()
            events = self.sel.select()
            for key, mask in events:
                callback = key.data
                callback(key.fileobj, mask)

    def kick(self, nick):
        print("Kicking " + nick)
        msg = BingoProto.kick(self.nickname, nick)
        msg, signature = sign(msg, self.private_key)
        BingoProto.send_msg(self.playAreaSock, msg, signature)
        print("Updating and signing user list")
        del self.userList[nick]
        finalUserList = translateKeys(self.userList)
        _, sig = sign(finalUserList, self.private_key)
        msg = BingoProto.userListSigning(self.nickname, finalUserList, sig)
        msg, signature = sign(msg, self.private_key)
        BingoProto.send_msg(self.playAreaSock, msg, signature)
    
def main():
    if len(sys.argv) != 5:
        print('Usage: %s port nickname deck_size card'%(sys.argv[0]))
        sys.exit( 1 )

    port  = int(sys.argv[1])
    nickname = str(sys.argv[2])
    deck_size  = int(sys.argv[3]) 
    card = str(sys.argv[4])

    caller = Caller(port, nickname, deck_size, card)
    caller.loop()
    
if __name__ == '__main__':
    main()
    