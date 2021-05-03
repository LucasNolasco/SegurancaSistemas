#!/usr/bin/python3

from Crypto.Cipher import DES
import json
import os
import hashlib
from flask import request, Flask
app = Flask(__name__)

# =======================================

def pad(text):
    while len(text) % 8 != 0:
        text += '\x00'

    return text

# =======================================

def load_passwd(path):
    '''
        Função para carregar o hash da senha armazenado
        no arquivo txt
    '''
    with open(path, "r") as arq:
        senha = arq.readline()
        senha = bytes.fromhex(senha)
    
    senha = senha[:8] # Limita no tamanho necessário para o DES

    return senha

# =======================================

@app.route("/authentication_service/authenticate")
def client_authentication_request():
    m1 = request.get_json()
    ID_C = m1["ID_C"] # Obtém o ID do cliente
    ID_C = ID_C.replace("\x00", "") # Remove o padding
    if os.path.isfile("AS/usuarios/" + ID_C + ".txt"): # Verifica se o cliente informado existe nos registros do AS
        chave = load_passwd("AS/usuarios/" + ID_C + ".txt") # Carrega a chave armazenada para este cliente
        cifra_des = DES.new(chave, DES.MODE_ECB)
        
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

        senha_tgs = load_passwd("AS/TGS/tgs.txt")
        cifra_tgs_des = DES.new(senha_tgs, DES.MODE_ECB) # Cria a cifra com a senha do TGS
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