#!/usr/bin/python3

from Crypto.Cipher import DES
import json
import os
from flask import request, Flask
app = Flask(__name__)

senhas_clientes = {
    'lucas': 'chave123'
}

senha_tgs = 'tgstgstg'

def pad(text):
    while len(text) % 8 != 0:
        text += '\x00'

    return text

@app.route("/authentication_service/authenticate")
def client_authentication_request():
    pedido = request.get_json()
    ID_C = pedido["ID_C"]
    if ID_C in senhas_clientes:
        chave = senhas_clientes[ID_C]
        cifra_des = DES.new(chave.encode(), DES.MODE_ECB)
        ID_S = cifra_des.decrypt(bytes.fromhex(pedido["ID_S"])).decode()
        T_R = cifra_des.decrypt(bytes.fromhex(pedido["T_R"])).decode()
        N1 = cifra_des.decrypt(bytes.fromhex(pedido["N1"])).decode()
        
        print(f"ID_S: {ID_S}, T_R: {T_R}, N1: {N1}")

        K_c_tgs = os.urandom(8)

        print(f"K_c_tgs: {K_c_tgs}")

        T_c_tgs = {
            "ID_C": ID_C.encode().hex(),
            "T_R": T_R.encode().hex(),
            "K_c_tgs": K_c_tgs.hex()
        }

        cifra_tgs_des = DES.new(senha_tgs.encode(), DES.MODE_ECB)
        T_c_tgs = cifra_tgs_des.encrypt(pad(json.dumps(T_c_tgs)).encode())

        encrypted_K_c_tgs = cifra_des.encrypt(K_c_tgs)

        m2 = {
            "K_c_tgs": encrypted_K_c_tgs.hex(),
            "N1": pedido["N1"],
            "T_c_tgs": T_c_tgs.hex()
        }

        return m2

    else:
        return "Error"

if __name__ == "__main__":
    app.run(port=5000)