# Ping / Traceroute  

Válasszuk ki az első és utolsó 10 nevet a listából, írjunk egy python programot, ami végig megy a leszűkített 20 elemű listán és minden címre lefuttatja a traceroute és ping toolokat, majd az eredményeket rendezett formában két fájlba írja!

**Script paraméterezése:** python3 client.py hosts.csv (NEM MILLIÓ SOROS ÉS EGY HOST TÖBBSZÖR IS SZEREPELHET!!!)

**Traceroute paraméterek:** max. 30 hopot vizsgáljunk

**Ping paraméterek:** 10 próba legyen

**Kimeneti fájlok (ld. diák):**
*traceroute.json
*ping.json  

**A teszt 10 perc után lelövi a futást!!!**

A párhuzamos futtatás esetén vigyázzunk és limitáljuk a processek maximális számát!!!

**Leadás:** A program leadása a BE-AD rendszeren .zip formátumban, amiben egy client.py szerepeljen!
