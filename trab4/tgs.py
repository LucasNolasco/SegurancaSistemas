#!/usr/bin/python3

import time
from Crypto.Cipher import DES
import json
import os
from flask import request, Flask
app = Flask(__name__)

# =======================================

senhas_servicos = {
    'porta1': 'porta1p1'
}

# =======================================

senha_tgs = 'tgstgstg'

# =======================================

def pad(text):
    while len(text) % 8 != 0:
        text += '\x00'

    return text

# =======================================

@app.route("/ticket_granting_service/get_ticket")
def get_ticket():
    m3 = request.get_json() # Obtém a m3

    cifra_des = DES.new(senha_tgs.encode(), DES.MODE_ECB)
    try: # Tenta descriptografar o ticket
        T_c_tgs = json.loads(cifra_des.decrypt(bytes.fromhex(m3["T_c_tgs"])).decode().replace("\x00", ""))
        ID_C = bytes.fromhex(T_c_tgs["ID_C"]).decode()
        T_R = bytes.fromhex(T_c_tgs["T_R"]).decode()
        K_c_tgs = bytes.fromhex(T_c_tgs["K_c_tgs"])
    except:
        return {"erro": "Ticket inválido (ticket não foi criptografado com chave a chave do TGS)"}

    cifra_sessao_tgs_cliente = DES.new(K_c_tgs, DES.MODE_ECB)
    try: # Tenta descriptografar o resto da mensagem usando a chave de sessão obtida no ticket
        ID_C_codificado = cifra_sessao_tgs_cliente.decrypt(bytes.fromhex(m3["ID_C"])).decode()
        ID_S = cifra_sessao_tgs_cliente.decrypt(bytes.fromhex(m3["ID_S"])).decode()
        T_R_codificado = cifra_sessao_tgs_cliente.decrypt(bytes.fromhex(m3["T_R"])).decode()
        N2 = cifra_sessao_tgs_cliente.decrypt(bytes.fromhex(m3["N2"])).decode()
    except:
        return {"erro": "Mensagem inválida (mensagem não foi criptografada com a chave de sessão)"}

    T_R = T_R.replace("\x00", "")
    T_R_codificado = T_R_codificado.replace("\x00", "")

    T_R = min(float(T_R), float(T_R_codificado)) # Utiliza o menor tempo entre o indicado no ticket e o solicitado na mensagem
    if T_R < time.time(): # Verifica se o tempo desejado para acessar o serviço é válido
        return {"erro": "Tempo solicitado para acesso ao serviço já está expirado"}

    T_R = str(T_R) # Converte o tempo para uma string novamente

    K_c_s = os.urandom(8) # Gera a chave de sessão para a comunicação do cliente com o serviço

    T_c_s = { # Cria o ticket para permitir que o cliente se comunique com o serviço
        "ID_C": ID_C.encode().hex(),
        "T_A": T_R.encode().hex(),
        "K_c_s": K_c_s.hex()
    }
    
    ID_S = ID_S.replace("\x00", "") # Remove o padding do ID
    if ID_S not in senhas_servicos: # Verifica se o serviço desejado existe
        return {"erro": "Serviço solicitado não existe"}

    senha_servico = senhas_servicos[ID_S] # Obtém a chave do serviço armazenada no TGS
    chave_servico = DES.new(senha_servico.encode(), DES.MODE_ECB) 
    T_c_s = chave_servico.encrypt(pad(json.dumps(T_c_s)).encode()) # Criptografa o ticket

    m4_K_c_s = cifra_sessao_tgs_cliente.encrypt(K_c_s) # Criptografa os demais itens da mensagem
    m4_T_A = cifra_sessao_tgs_cliente.encrypt(pad(T_R).encode())
    m4_N2 = cifra_sessao_tgs_cliente.encrypt(pad(N2).encode())

    m4 = { # Monta a mensagem para envio
        "K_c_s": m4_K_c_s.hex(),
        "T_A": m4_T_A.hex(),
        "N2": m4_N2.hex(),
        "T_c_s": T_c_s.hex()
    }

    return m4

if __name__ == "__main__":
    app.run(port=5001)