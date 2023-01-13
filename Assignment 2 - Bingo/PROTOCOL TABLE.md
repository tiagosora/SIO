# **Message Protocol**

<br>

This document synthesizes the way messages work, using a table containing.

<br>

| **MESSAGE**                  | **SENDER**         | **RECEIVER**       | **COMMAND**           | **ARGS**                                        |
| ---------------------------- | ------------------ | ------------------ | --------------------- | ----------------------------------------------- |
| AuthorizationRequestMessage  | Player<br />Caller | PA                 | authorizationRequest  | user_type, nickname, public key, cc certificate |
| ValidAuthorizationMessage    | PA                 | Player<br />Caller | validAuthorization    | public key                                      |
| InvalidAuthorizationMessage  | PA                 | Player<br />Caller | invalidAuthorization  |                                                 |
| InvalidAuthenticationMessage | PA                 | Player<br />Caller | invalidAuthentication | error                                           |
| StartMessage                 | Caller             | PA                 | start                 | deck_size                                       |
| CardResquestMessage          | Caller             | PA                 | cardRequest           |                                                 |
|                              | PA                 | Player             |                       |                                                 |
| CardShareMessage             | Caller             | PA                 | cardShare             | card                                            |
|                              | PA                 | Player             |                       |                                                 |
| DeckSendMessage              | Caller             | PA                 | deckSend              | deck                                            |
|                              | PA                 | Player             |                       |                                                 |
| DeckShareMessage             | Caller             | PA                 | deckShare             | deck, signature, symmetric key                  |
|                              | PA                 | Player             |                       |                                                 |
| KeyShareMessage              | Player             | PA                 | keyShare              | symmetric key                                   |
|                              | PA                 | Player<br />Caller |                       |                                                 |
| KickMessage                  | Caller             | PA                 | kick                  | nickname                                        |
|                              | PA                 | Caller             |                       |                                                 |
| UserListSigningMessage       | PA                 | Player<br />Caller | userListSigning       | users' list, list's signature                   |
| ResultsSendMessage           | Player             | PA                 | resultsSend           | deck, winners' list                             |
|                              | PA                 | Caller             |                       |                                                 |
| AuditLogRequestMessage       | Player<br />Caller | PA                 | auditLogRequest       |                                                 |
| AuditLogResponseMessage      | PA                 | Player<br />Caller | auditLogResponse      | audit logs                                      |
| UserListRequestMessage       | Player<br />Caller | PA                 | userListRequest       |                                                 |
| UserListResponseMessage      | PA                 | Player<br />Caller | userListResponse      | users' list, list's signature                   |

