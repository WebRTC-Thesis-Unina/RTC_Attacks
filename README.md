# Scenari di attacco Real Time
Il progetto propone la realizzazione di diversi scenari di attacco ad infrastrutture per la comunicazione real time.
## Descrizione degli scenari
### Scenario 1 e 2: Attacco SIP Spoofing e DoS
In questo scenario, sono descritti gli attacchi di SIP Spoofing e DoS (attraverso SIP Flooding). Sono stati utilizzati i seguenti componenti:
- <b>FreeSWITCH</b>: container che svolge il ruolo di SIP Server, vulnerabile a SIP Spoofing e DoS;
- <b>attacker</b>: container alpine su cui è stato installato python;
- <b>linphone</b>: speciale softphone che simula un client SIP.<br>
In questo scenario, inizialmente si invia un SIP Message da un utente non registrato impersonando un altro utente (spoofing). Il secondo attacco sarà possibile in quanto si invieranno richieste di registrazione continue al server FreeSWITCH (DoS via SIP Flooding).
### Scenario 3: Attacco RTP Injection
In questo scenario si descrive un attacco di RTP Injection, a causa di una vulnerabilità RTP Bleed. Si utilizzano i seguenti componenti:
- <b>Asterisk</b>: container che svolge il ruolo di SIP Server, vulnerabile a RTP Injection;
- <b>sippts</b>: container kali rolling su cui è stato installato sippts (tool per compiere attacchi SIP/RTP);
- <b>linphone</b>: speciale softphone che simula un client SIP.<br>
In questo scenario, dopo che due client hanno stabilito una comunicazione, un attaccante può intercettare il traffico RTP (a causa della vulnerabilità RTP Bleed) e iniettare audio nocivo nella conversazione.
### Scenario 4: Memory Corruption
In questo scenario si descrive un attacco di Memory Corruption, a causa di una vulnerabilità di heap overflow. Di seguito si riportano i componenti utilizzati:
- <b>Kamailio</b>: container che svolge il ruolo di SIP Server, vulnerabile a heap overflow;
- <b>SIPp</b>: container che svolge il ruolo di SIP Client;
- <b>linphone</b>: speciale softphone che simula un client SIP.<br>
Nello scenario, a causa dell'invio di una richiesta mal formata al server, si ha la terminazione del container.
### Scenario 5: Access Bypass
In questo scenario si descrive un attacco di Access Bypass. I componenti utilizzati sono i seguenti:
- <b>coTURN</b>: container che emula il comportamento di un server TURN vulnerabile ad access bypass;
- <b>STUNner</b>: container che funge da proxy socks5 verso il server TURN;
- <b>node</b>: container che emula signal server WebRTC.<br>
Nello scenario, dopo aver creato un proxy socks5 verso il server TURN, si può osservare che utilizzando particolari GET HTTP, è possibile accedere a servizi interni del server.
### Scenario 6: Ransomware
In questo scenario si descrive un attacco di Ransomware a causa di una vulnerabilità del server che permette l'upload di file malevoli. Il componente utilizzati è il seguente:
- <b>node</b>: container che gestisce il backend della web application, vulnerabile all'attacco.<br>
Nello scenario, è possibile caricare un file javascript nocivo, per eseguire una webshell sulla macchina vittima. Una volta fatto ciò si carica dal server HTTP dell'attaccante il file python contente il ransomware e lo si esegue attraverso webshell. L'effetto sarà la crittografia dei file presenti sulla macchina vittima.
### Scenario 7 e 8: Access Bypass e Information Disclosure
Nello scenario si descrivono due scenari d'attacco: Access Bypass e Information Disclosure, a causa rispettivamente di vulnerabilità di NoSQLi e XSS. Si utilizzano i componenti:
- <b>node</b>: container che gestisce il backend della web application, vulnerabile a NoSQli.
- <b>VDO.Ninja</b>: container che simula la piattaforma VDO.Ninja, per gestire comunicazioni audio video. E' vulnerabile a XSS.<br>
In questo scenario, è possibile inserendo particolari input "superare" i controlli e accedere alla piattaforma VDO.Ninja. Utilizzando poi una particolare query string, si possono ottenere informazioni sensibili (es. cookie).
