# Quelques notes utiles sur comment utiliser mitmproxy

## Avant de lancer mitmproxy
Il est indispensable d'activer l'IP forwarding, sans lui, on fait un déni de service au lieu d'un MITM (le trafic arrive et meurt sur la kali).

```bash
sudo sysctl -w net?ipv4.ip_forward=1

#pour verifier
sudo /proc/sys/net/ipv4/ip_forward
```

## Lancer mitmproxy
Il faut lancer mitmproxy en mode transparent sinon, mitmproxy attend un proxy explicitement configuré côté client et ne verra rien du trafic redirigé.


```bash
mitmproxy --mode transparent --ssl-insecure
```


