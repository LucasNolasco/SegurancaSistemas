#!/usr/bin/python3

from Crypto.Cipher import DES
import json
import os
from flask import request, Flask
app = Flask(__name__)

senhas_servicos = {
    'porta1': 'porta1p1'
}

senha_tgs = 'tgstgstg'

def pad(text):
    while len(text) % 8 != 0:
        text += '\x00'

    return text

@app.route("/ticket_granting_service/get_ticket")
def get_ticket():
    m3 = request.get_json()

    cifra_des = DES.new(senha_tgs.encode(), DES.MODE_ECB)
    T_c_tgs = json.loads(cifra_des.decrypt(bytes.fromhex(m3["T_c_tgs"])))
    ID_C = bytes.fromhex(T_c_tgs["ID_C"]).decode()
    T_R = bytes.fromhex(T_c_tgs["T_R"]).decode()
    K_c_tgs = bytes.fromhex(T_c_tgs["K_c_tgs"])

    cifra_sessao_tgs_cliente = DES.new(K_c_tgs, DES.MODE_ECB)
    ID_C_codificado = cifra_sessao_tgs_cliente.decrypt(bytes.fromhex(m3["ID_C"])).decode()
    ID_S = cifra_sessao_tgs_cliente.decrypt(bytes.fromhex(m3["ID_S"])).decode()
    T_R_codificado = cifra_sessao_tgs_cliente.decrypt(bytes.fromhex(m3["T_R"])).decode()
    N2 = cifra_sessao_tgs_cliente.decrypt(bytes.fromhex(m3["N2"])).decode()

    print(f"ID_C: {ID_C}, T_R: {T_R}, K_c_tgs: {K_c_tgs}")
    print(f"ID_C: {ID_C_codificado}, ID_S: {ID_S}, T_R: {T_R_codificado}, N2: {N2}")

    K_c_s = os.urandom(8)

    T_c_s = {
        "ID_C": ID_C.encode().hex(),
        "T_A": T_R_codificado.encode().hex(),
        "K_c_s": K_c_s.hex()
    }

    chave_servico = DES.new(senhas_servicos[ID_S.replace("\x00", "")].encode(), DES.MODE_ECB)
    T_c_s = chave_servico.encrypt(pad(json.dumps(T_c_s)).encode())

    m4_K_c_s = cifra_sessao_tgs_cliente.encrypt(K_c_s)
    m4_T_A = cifra_sessao_tgs_cliente.encrypt(pad(T_R_codificado).encode())
    m4_N2 = cifra_sessao_tgs_cliente.encrypt(pad(N2).encode())

    print(f"K_c_s: {K_c_s}, T_A: {T_R_codificado}, N2: {N2}")

    m4 = {
        "K_c_s": m4_K_c_s.hex(),
        "T_A": m4_T_A.hex(),
        "N2": m4_N2.hex(),
        "T_c_s": T_c_s.hex()
    }

    return m4

if __name__ == "__main__":
    app.run(port=5001)