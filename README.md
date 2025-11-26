# Scenari di attacco Real Time
Il progetto propone la realizzazione di diversi scenari di attacco real time.
## Descrizione degli scenari
### Scenario 1 e 2: Attacco SIP Spoofing e DoS
In questo scenario, sono descritti gli attacchi di SIP Spoofing e DoS (attraverso SIP Flooding). Sono stati utilizzati i seguenti componenti:
- <b>FreeSWITCH</b>: container che svolge il ruolo di SIP Server, vulnerabile a SIP Spoofing e DoS;
- <b>attacker</b>: container alpine su cui è stato installato python;
- <b>linphone</p>: speciale softphone che simula un client SIP.
In questo scenario, inizialmente si invia un SIP Message da un utente non registrato impersonando un altro utente (spoofing). Il secondo attacco sarà possibile in quanto si invieranno richieste di registrazione continue al server FreeSWITCH (DoS via SIP Flooding).
### Scenario 3: Attacco RTP Injection
In questo scenario si descrive un attacco di RTP Injection, a causa di una vulnerabilità RTP Bleed. Si utilizzano i seguenti componenti:
- <b>Asterisk</b>: container che svolge il ruolo di SIP Server, vulnerabile a RTP Injection;
- <b>sippts</b>: container kali rolling su cui è stato installato sippts (tool per compiere attacchi SIP/RTP);
- <b>linphone</b>: speciale softphone che simula un client SIP.
In questo scenario, dopo che due client hanno stabilito una comunicazione, un attaccante può intercettare il traffico RTP (a causa della vulnerabilità RTP Bleed) e iniettare audio nocivo nella conversazione.
### Scenario 4: Memory Corruption
In questo scenario si descrive un attacco di memory corruption, a causa di una vulnerabilità di heap overflow. Di seguito si riportano i componenti utilizzati:
- <b>Kamailio</b>: container che svolge il ruolo di SIP Server, vulnerabile a heap overflow;
- <b>SIPp</b>: container che svolge il ruolo di SIP Client;
- <b>linphone</b>: speciale softphone che simula un client SIP.
Nello scenario, a causa dell'invio di una richiesta mal formata al server, si ha la terminazione del container.
### Scenario 5: Access Bypass
### Scenario 6: Ransomware
### Scenario 7 e 8: NoSQLi e XSS
