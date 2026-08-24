## Quelques astuces utiles sur Wireshark

## Filtres utiles :

| Message             | Type TLS        | Ce que tu cherches dans Wireshark |
|---------------------|-----------------|-----------------------------------|
| Client Hello        | Handshake (1)   | tls.handshake.type == 1           |
| Server Hello        | Handshake (2)   | tls.handshake.type == 2           |
| Certificate         | Handshake (11)  | tls.handshake.type == 11          |
| Server Hello Done   | Handshake (14)  | tls.handshake.type == 14          |
| Client Key Exchange | Handshake (16)  | tls.handshake.type == 16          |
| Change Cipher Spec  | Content type 20 | tls.record.content_type == 20     |
| Finished            | Handshake (20)  | tls.handshake.type == 20          |

## Obtenir la bonne session TLS parmis plusieurs :
Filtre sur le Client Hello uniquement pour voir toutes les sessions :
```
tls.handshake.type == 1
```

Repère le bon paquet (par IP, port, timestamp, SNI…), puis :
- Note le numéro de tcp.stream
- Applique : `tcp.stream eq <N>`Filtres utiles

Tu peux aussi voir le **SNI (le domaine ciblé)** directement dans le Client Hello :
````
tls.handshake.extensions_server_name == "example.com"
````