#!/usr/bin/python3

from Crypto.Cipher import DES
import json
import os
from flask import request, Flask
app = Flask(__name__)

# =======================================

senhas_clientes = {
    'lucas': 'chave123'
}

# =======================================

senha_tgs = 'tgstgstg'

# =======================================

def pad(text):
    while len(text) % 8 != 0:
        text += '\x00'

    return text

# =======================================

@app.route("/authentication_service/authenticate")
def client_authentication_request():
    m1 = request.get_json()
    ID_C = m1["ID_C"] # Obtém o ID do cliente
    ID_C = ID_C.replace("\x00", "") # Remove o padding
    if ID_C in senhas_clientes: # Verifica se o cliente informado existe nos registros do AS
        chave = senhas_clientes[ID_C] # Carrega a chave armazenada para este cliente
        cifra_des = DES.new(chave.encode(), DES.MODE_ECB)
        
        try: # Tenta descriptografar a mensagem recebida para ver se a senha utilizada pelo usuário está correta
            ID_S = cifra_des.decrypt(bytes.fromhex(m1["ID_S"])).decode() # Descriptografa o id do serviço
            T_R = cifra_des.decrypt(bytes.fromhex(m1["T_R"])).decode() # Descriptografa o tempo requisitado pelo cliente
            N1 = cifra_des.decrypt(bytes.fromhex(m1["N1"])).decode() # Descriptografa o número recebido

        except:
            return {"erro": "Mensagem criptografada com a chave incorreta"}

        K_c_tgs = os.urandom(8) # Gera uma nova chave de sessão para a comunicação entre o cliente e o TGS
        
        T_c_tgs = { # Cria o ticket para que o cliente possa se comunicar com o TGS
            "ID_C": ID_C.encode().hex(),
            "T_R": T_R.encode().hex(),
            "K_c_tgs": K_c_tgs.hex()
        }

        cifra_tgs_des = DES.new(senha_tgs.encode(), DES.MODE_ECB) # Cria a cifra com a senha do TGS
        T_c_tgs = cifra_tgs_des.encrypt(pad(json.dumps(T_c_tgs)).encode()) # Criptografa o ticket utilizando a senha do TGS

        encrypted_K_c_tgs = cifra_des.encrypt(K_c_tgs) # Criptografa a chave de sessão utilizando a chave do cliente

        m2 = { # Monta a M2
            "K_c_tgs": encrypted_K_c_tgs.hex(),
            "N1": m1["N1"],
            "T_c_tgs": T_c_tgs.hex()
        }

        return m2


    else:
        return {"erro": "Usuário não registrado no AS"}

if __name__ == "__main__":
    app.run(port=5000)