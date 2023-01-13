#!/bin/python

import fcntl
import os
import random as rand
import selectors
import socket
import sys

from cryptography.hazmat.primitives import serialization

sys.path.append('')
from cc.pteid import PTeID
from playingArea.logging import LogReader
from protocol.common import *
from protocol.protocol import BingoProto


class Player:

    def __init__(self, port, nickname, card):
        self.host = 'localhost'
        self.port = port
        self.cc_card = card
        self.user_type = "player"

        self.nickname = nickname
        self.cc = PTeID()

        self.public_key, self.private_key = create_keys() # (public key, private key)
        self.symm_key = os.urandom(32)
        
        self.userList = {}          # { nickname:str : [ sequence:int , pk ] }
        self.playersSymKeys = {}    # { sequencePlayer:int : symKey }
        self.player_cards = {}      # { nickname:str : card:Card}

        self.userListSignature = None
        self.callernick : str = None
        self.card : Card = None
        self.deck : Deck = None
        self.placeOfCheat = 0

        if rand.randint(1,10) == 1: 
            print("This player will cheat!")
            self.placeOfCheat = rand.randint(1,4)
            if self.placeOfCheat == 1:
                print("He will send an invalid public key!")
            if self.placeOfCheat == 2:
                print("He will send an invalid card to everyone!")
            if self.placeOfCheat == 3:
                print("He will change the deck to a own deck!")
            if self.placeOfCheat == 4:
                print("After the game, he will say he's the winner!")

        self.playAreaSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.playAreaSock.connect((self.host, self.port))
            self.playAreaSock.setblocking(True)
        except Exception as e:
            sys.exit(f"\nERROR: Wrong choice of port.\n{e}")

        if self.placeOfCheat == 1:
            self.public_key, _ = create_keys()

        msg = BingoProto.authorizationRequest(self.nickname, self.user_type, self.nickname, public_key_bytes(self.public_key), self.cc.cert.public_bytes(encoding=serialization.Encoding.PEM))
        bmsg = pickle.dumps(msg.dic())        
        signature = self.cc.signature(bmsg)
        BingoProto.send_msg(self.playAreaSock, bmsg, signature)
        
        msg, data, signature = BingoProto.recv_msg(self.playAreaSock)
        if msg.command == "invalidAuthentication":
                    error_msg = msg.error
                    print(error_msg)
                    print("-" * 82)
                    self.playAreaSock.close()
                    exit(0)
        elif (not msg) or msg.command != "validAuthorization":
            print("Invalid Authorization")
            self.playAreaSock.close()
            exit(0)
        else:
            playAreaPk = serialization.load_pem_public_key(msg.pk)
            self.userList["playarea"] = [-1, playAreaPk]
        
        print("The game is about to start. Wait patiently!\n")

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

                elif msg.command == "userListResponse":
                    trans = translateKeys(msg.users_list)
                    self.callernick = [nick for nick in msg.users_list.keys() if msg.users_list[nick][0] == 0][0]
                    if verify_pk(pickle.dumps(trans), msg.user_list_sig, msg.users_list[self.callernick][1]):
                        self.userList = msg.users_list
                        self.userListSignature = msg.user_list_sig
                        print("You received the user's list!")
                        for user, list in self.userList.items():
                            print("Sequence: ",list[0]," | User: ",user," | Key: ",list[1])
                    else:
                        print("ALERT! You received the user's list with a bad signature!")

                elif msg.command == "auditLogResponse":
                    lr = LogReader()
                    lr.displayLogs(msg.audit_logs)

                elif msg.command == "start":
                    print("The game game has started!")
                    print("Generating a new random card ...")
                    self.deck_size = msg.deck_size
                    self.card = Card(self.deck_size)
                    self.card.gen_card()

                    if self.placeOfCheat == 2:
                        self.card.cheat()

                    self.player_cards[self.nickname] = self.card
                    print("Your card: [", self.card.numbers,"]")
                    print("Sending the your card to everyone!")
                    msg = BingoProto.cardShare(self.nickname, self.card)
                    msg, signature = sign(msg, self.private_key)
                    BingoProto.send_msg(self.playAreaSock, msg, signature)

                elif msg.command == "cardShare":
                    if msg.card.verify(self.deck_size):
                        self.player_cards[msg.sender] = msg.card
                        print("You received and validated " + msg.sender + "'s player card!")
                    else:
                        print("ALERT! You received " + msg.sender + "'s card, it has a bad card!")

                elif msg.command == "deckSend":
                    print("You received the deck!")
                    deck : Deck = msg.deck

                    if self.placeOfCheat == 3:
                        deck = Deck(len(deck.deck))

                    deck.shuffle()
                    deck.encrypt(self.symm_key)
                    print("You shuffled and encrypted the deck!")
                    msg = BingoProto.deckSend(self.nickname, deck)
                    msg, signature = sign(msg, self.private_key)
                    BingoProto.send_msg(self.playAreaSock, msg, signature)
                    print("Sending the deck to the next player, wait for the final deck!")

                elif msg.command == "deckShare" and verify_pk(msg.deck, msg.deck_signature, self.userList[msg.sender][1]):
                    print("You received the final deck from the caller!")
                    print("You received the caller's symmetric key!")
                    my_sequence = self.userList[self.nickname][0]
                    self.playersSymKeys[my_sequence] = self.symm_key
                    self.playersSymKeys[0] = msg.symkey


                    deckDict : Deck = pickle.loads(msg.deck)
                    self.deck = Deck(len(deckDict["deck"]))
                    self.deck.deck = deckDict["deck"]
                    print("Sending your symmetric key to everyone!")
                    msg = BingoProto.keyShare(self.nickname, self.symm_key)
                    msg, signature = sign(msg, self.private_key)
                    BingoProto.send_msg(self.playAreaSock, msg, signature)

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

                            winners, deck = compute_result(self.deck, self.player_cards)

                            if self.placeOfCheat == 4:
                                winners = [self.nickname]

                            print("Winners: ",winners)
                            print("Sending the winners list to caller!")
                            msg = BingoProto.resultsSend(self.nickname, deck, winners)
                            msg, signature = sign(msg, self.private_key)
                            BingoProto.send_msg(self.playAreaSock, msg, signature)

                        except:
                            print("ALERT! Someone screwed up the deck! The game is invalid!")

                elif msg.command == "kick":
                    print("ALERT! " + msg.nick + " was kicked from the session.")
                    if msg.nick == self.nickname: exit(1)

            print("-" * 82)

        except Exception as e:
            print('Mensagem inválida recebida no read, desconectando', conn) 
            print("Erro:", e)
            print("-" * 82)
            self.sel.unregister(conn)
            conn.close()
            exit(0)

    def user_stdin(self, stdin, mask):
        user_input = list(stdin.read().upper().strip().split(" "))
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

    def loop(self):
        orig_fl = fcntl.fcntl(sys.stdin, fcntl.F_GETFL)
        fcntl.fcntl(sys.stdin, fcntl.F_SETFL, orig_fl | os.O_NONBLOCK)

        self.sel.register(sys.stdin, selectors.EVENT_READ, self.user_stdin)

        while True:
            print("logs, users")
            sys.stdout.write('> ')
            sys.stdout.flush()
            events = self.sel.select()
            for key, mask in events:
                callback = key.data
                callback(key.fileobj, mask)

def main():
    if len(sys.argv) != 4:
        print('Usage: %s port nickname card'%(sys.argv[0]))
        sys.exit( 1 )

    port = int(sys.argv[1])  
    nickname = str(sys.argv[2])
    card = str(sys.argv[3])

    player = Player(port, nickname, card)
    player.loop()
    
if __name__ == '__main__':
    main()
