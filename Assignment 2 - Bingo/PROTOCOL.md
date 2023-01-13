# **Message Protocol**

This document describes the protocol our application utilizes to communicate between clients.

<br>

## **Audit Log Checks**

Both players and caller can request for the Playing Area's logs and user's list, using:

- Audit Request Message
- User List Request Message

The Playing Area then responds with:

- Audit Response Message
- User List Response Message

<br>

## **Game Flow**

The Bingo's game flow is mainly separated into 5 stages:

1. Connections, Authorizations and Authentications
2. Start Game
3. Card Generation and Validation
4. Deck Shuffling
5. Compute Winners

The next sections describes which messages a module can send, according to game stage. A message not attached to a game state can be sent anytime.

<br>

### **Playing Area**

Responsibilities:

- Forward messages between players and caller

<br>

1. Connections, Authorizations and Authentications
   - Authorization Response
   - Acknowledge Response
2. Start Game
   - Game Info
3. Card Generation and Validation
   - Game Info
   - Card Request
   - Card Share
   - Card Validation Error
4. Deck Shuffling
   - Deck Send
   - Deck Share
5. Compute Winners
   - Deck Validation Error
   - Winner Share

<br>

### **Caller**

 Responsibilities:

- End Current Stage & Start Next Stage

<br>

1. Connections, Authorizations and Authentications
   - Authorization Request
   - Acknowledge Request
2. Start Game
   - Start
3. Card Generation and Validation
   - Card Request
   - Card Validation Error
4. Deck Shuffling
   - Deck Send
   - Deck Share
   - Key Share
5. Compute Winners
   - Deck Validation Error
   - Winner Share

<br>

### **Player**

Responsibilities

- Respond to requests

<br>

1. Connections, Authorizations and Authentications
   - Authorization Request
   - Acknowledge Request
2. Start Game
3. Card Generation and Validation
   - Card Share
   - Card Validation Error
4. Deck Shuffling
   - Deck Send
   - Key Share
5. Compute Winners
   - Deck Validation Error
   - Winner Share
