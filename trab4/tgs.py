#!/usr/bin/python3

#!/usr/bin/python3

from Crypto.Cipher import DES
import json
import os
from flask import request, Flask
app = Flask(__name__)

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

    return "OK"

if __name__ == "__main__":
    app.run(port=5001)