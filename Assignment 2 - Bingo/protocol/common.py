import os
import pickle
import random

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


class Deck:
    
    def __init__(self, decksize):
        self.decksize = decksize
        self.deck = [(i + 1).to_bytes(16, 'big') for i in range(decksize)]

    def shuffle(self):
        random.shuffle(self.deck)
        return self.deck

    def encrypt(self, symmkey):
        self.deck = [self.encrypt_int(symmkey, number) for number in self.deck]
        return self.deck

    def decrypt(self, symmkey):
        self.deck = [self.decrypt_int(symmkey, number) for number in self.deck]
        return self.deck

    def encrypt_int(self, symmkey, n):
        cipher = Cipher(algorithms.AES(symmkey), modes.ECB())
        encryptor = cipher.encryptor()
        return encryptor.update(n) + encryptor.finalize()

    def decrypt_int(self, symmkey, n):
        cipher = Cipher(algorithms.AES(symmkey), modes.ECB())
        decryptor = cipher.decryptor()
        return decryptor.update(n) + decryptor.finalize()

    def printdeck(self):
        print([int.from_bytes(i, 'big') for i in self.deck])

    def dic(self):
        return {"decksize": self.decksize, "deck": self.deck}


class Card:
    
    def __init__(self, decksize):
        self.decksize = decksize
        self.size = self.decksize // 4
        self.numbers = []

    def gen_card(self):
        self.numbers = random.sample(range(1, self.decksize + 1), self.size)
        return self.numbers

    def verify(self, decksize=None):
        if decksize == None: decksize == self.decksize
        if type(self.numbers) != list:
            return False
        if any([type(i) != int for i in self.numbers]):
            return False
        if len(self.numbers) != len(set(self.numbers)):
            return False
        if decksize // 4 != len(self.numbers):
            return False
        return True

    def result(self, deck: Deck):
        
        card_numbers = self.numbers
       
        print("| Card: ",card_numbers)
        for i in range(len(deck)):
            if deck[i] in card_numbers:
                card_numbers.remove(deck[i])
                if len(card_numbers) == 0:
                    return i

    def cheat(self):
        idxs = random.sample(range(0, len(self.numbers)), 2)
        self.numbers[idxs[0]] = self.numbers[idxs[1]]




def create_keys():
    private_key = get_private_key(1024)
    public_key = private_key.public_key()
    return public_key, private_key

def private_key_bytes(key):
    return key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    )

def public_key_bytes(key):
    return key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

def get_private_key(size):
    return rsa.generate_private_key(
        public_exponent=65537,
        key_size=size
    )

def verify_pk(data, signature, public_key):
    try:
        public_key.verify(
            signature,
            data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True
    except Exception as e:
        print("Invalid Signature")
        print(e)
        return False

def sign(msg, private_key):
    try:
        msg = pickle.dumps(msg.dic())
    except:
        msg = pickle.dumps(msg)
    return msg, private_key.sign(
        msg,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )

def compute_result(deck : Deck, player_cards : dict):
    winners = []
    best = 0
    readable_deck = [int.from_bytes(number, 'big') for number in deck.deck]
    print("Deck ->", readable_deck)
    for player in player_cards.keys():
        print("Player : ",player,end=' ')
        card : Card = player_cards[player]
        result = card.result(readable_deck)
        if best == 0 or result < best:
            best = result
            winners = [player]
        elif result == best:
            winners.append(player)
    
    return_deck = Deck(len(readable_deck))
    return_deck.deck = [number.to_bytes(4, 'big') for number in readable_deck]
    return winners, return_deck

def translateKeys(user_list):
    new_user_list = {}
    if type(user_list['playarea'][1]) == bytes:
        for user in user_list.keys():
            sequence = user_list[user][0]
            key = serialization.load_pem_public_key(user_list[user][1])
            new_user_list[user] = [sequence, key]
    else : 
        for user in user_list.keys():
            sequence = user_list[user][0]
            key = public_key_bytes(user_list[user][1])
            new_user_list[user] = [sequence, key]
    return new_user_list