# SIO 2nd Assignment - Bingo Secure Game

| NMec   | Email                 | Name             | Role                                   |
| ------ | --------------------- | ---------------- | -------------------------------------- |
| 102491 | raquelparadinha@ua.pt | Raquel Paradinha | Trabalha em pressão e depressão        |
| 103234 | paulojnpinto02@ua.pt  | Paulo Pinto      | Trabalha sem pressão e com depressão\* |
| 103341 | miguelamatos@ua.pt    | Miguel Matos     | Trabalha sem pressão nem depressão     |
| 104142 | tiagogcarvalho@ua.pt  | Tiago Carvalho   | Trabalha em pressão e sem depressão    |

\* e sem terminal também

# NOTES

## Game Flow

1. Connect with CC (both player and caller)
2. Lock playing area
3. Everyone generates their own card
4. Everyone commits their card to caller, signing them
5. Everyone validates commited cards
6. Caller shuffles, encrypts using a symmetric key and signs deck
7. Everyone, in order of registration, shuffles, encrypts using a symmetric key and signs same deck
8. Callers finally signs deck
9. Everyone + caller provide their symmetric keys for deck decryption, in order too
10. Everyone can now compute the winners, as they have both cards and decrypted deck
