#!/usr/bin/python3

import time
from Crypto.Cipher import DES
import json
import os
from flask import request, Flask
app = Flask(__name__)

# ====================================

senhas_servicos = {
    'porta1': 'porta1p1'
}

# ====================================

def pad(text):
    while len(text) % 8 != 0:
        text += '\x00'
    return text

# ====================================

@app.route("/service/porta1")
def service_porta1():
    m5 = request.get_json()

    cifra_des = DES.new(senhas_servicos["porta1"].encode(), DES.MODE_ECB) # Carrega a chave do serviço
    try: # Tenta descriptografar o ticket para verificar se ele é válido
        T_c_s = json.loads(cifra_des.decrypt(bytes.fromhex(m5["T_c_s"])).decode().replace("\x00", ""))
        ID_C = bytes.fromhex(T_c_s["ID_C"]).decode()
        T_A = bytes.fromhex(T_c_s["T_A"]).decode()
        K_c_s = bytes.fromhex(T_c_s["K_c_s"])
    except:
        return {"erro": "Ticket informado é inválido (Tcs)"}

    cifra_sessao_servico_cliente = DES.new(K_c_s, DES.MODE_ECB)
    try: # Tenta descriptografar o restante da mensagem utilizando a chave de sessão obtida no ticket
        ID_C_codificado = cifra_sessao_servico_cliente.decrypt(bytes.fromhex(m5["ID_C"])).decode()
        S_R = cifra_sessao_servico_cliente.decrypt(bytes.fromhex(m5["S_R"])).decode()
        T_A_codificado = cifra_sessao_servico_cliente.decrypt(bytes.fromhex(m5["T_A"])).decode()
        N3 = cifra_sessao_servico_cliente.decrypt(bytes.fromhex(m5["N3"])).decode()
    except:
        return {"erro": "Mensagem inválida (não foi criptografada utilizando a chave de sessão entre cliente e serviço)"}

    T_A = T_A.replace("\x00", "") # Faz o unpadding
    T_A_codificado = T_A_codificado.replace("\x00", "")

    T_A = min(float(T_A), float(T_A_codificado)) # Utiliza o menor tempo entre o existente no ticket e o informado pelo cliente
    if T_A < time.time():
        return {"erro": "Tempo expirado (serviço)"}

    S_R = S_R.replace("\x00", "") # Remove o padding do nome da operação a ser realizada pelo serviço
    if S_R.lower() == "abrir": # Verifica a ação e 'realiza' ela
        resposta = "Porta aberta"
    elif S_R.lower() == "fechar":
        resposta = "Porta fechada"
    else:
        resposta = "Operacao desconhecida"

    m6_resposta = cifra_sessao_servico_cliente.encrypt(pad(resposta).encode()) # Criptografa a resposta
    m6_N3 = cifra_sessao_servico_cliente.encrypt(pad(N3).encode())

    m6 = { # Monta a mensagem de resposta
        "Resposta": m6_resposta.hex(),
        "N3": m6_N3.hex()
    }

    return m6

if __name__ == "__main__":
    app.run(port=5002)