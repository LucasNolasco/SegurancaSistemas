#!/usr/bin/python3

from Crypto.Cipher import DES
import json
import os
from flask import request, Flask
app = Flask(__name__)

senhas_servicos = {
    'porta1': 'porta1p1'
}

def pad(text):
    print(text)
    while len(text) % 8 != 0:
        print(len(text))
        text += '\x00'
    return text

@app.route("/service/porta1")
def service_porta1():
    m5 = request.get_json()

    cifra_des = DES.new(senhas_servicos["porta1"].encode(), DES.MODE_ECB)
    T_c_s = json.loads(cifra_des.decrypt(bytes.fromhex(m5["T_c_s"])).decode().replace("\x00", ""))
    ID_C = bytes.fromhex(T_c_s["ID_C"]).decode()
    T_A = bytes.fromhex(T_c_s["T_A"]).decode()
    K_c_s = bytes.fromhex(T_c_s["K_c_s"])

    cifra_sessao_servico_cliente = DES.new(K_c_s, DES.MODE_ECB)
    ID_C_codificado = cifra_sessao_servico_cliente.decrypt(bytes.fromhex(m5["ID_C"])).decode()
    S_R = cifra_sessao_servico_cliente.decrypt(bytes.fromhex(m5["S_R"])).decode()
    T_A_codificado = cifra_sessao_servico_cliente.decrypt(bytes.fromhex(m5["T_A"])).decode()
    N3 = cifra_sessao_servico_cliente.decrypt(bytes.fromhex(m5["N3"])).decode()

    print(f"ID_C: {ID_C}, T_A: {T_A}, K_c_s: {K_c_s}")
    print(f"ID_C: {ID_C_codificado}, S_R: {S_R}, T_A: {T_A_codificado}, N3: {N3}")

    S_R = S_R.replace("\x00", "")
    if S_R.lower() == "abrir":
        resposta = "Porta aberta"
    elif S_R.lower() == "fechar":
        resposta = "Porta fechada"
    else:
        resposta = "Operacao desconhecida"

    m6_resposta = cifra_sessao_servico_cliente.encrypt(pad(resposta).encode())
    m6_N3 = cifra_sessao_servico_cliente.encrypt(pad(N3).encode())

    print(f"Resposta: {resposta}")

    m6 = {
        "Resposta": m6_resposta.hex(),
        "N3": m6_N3.hex()
    }

    return m6

if __name__ == "__main__":
    app.run(port=5002)