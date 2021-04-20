#!/usr/bin/python3

from Crypto.Cipher import DES
from flask import request, Flask
app = Flask(__name__)

senhas = {
    'lucas': 'chave123'
}

@app.route("/authentication_service/authenticate")
def client_authentication_request():
    pedido = request.get_json()
    usuario = pedido["ID_C"]
    if usuario in senhas:
        chave = senhas[usuario]
        cifra_des = DES.new(chave.encode(), DES.MODE_ECB)
        ID_S = cifra_des.decrypt(bytes.fromhex(pedido["ID_S"])).decode()
        T_R = cifra_des.decrypt(bytes.fromhex(pedido["T_R"])).decode()
        N1 = cifra_des.decrypt(bytes.fromhex(pedido["N1"])).decode()
        
        print(f"ID_S: {ID_S}, T_R: {T_R}, N1: {N1}")

    return "Ok"

if __name__ == "__main__":
    app.run(port=5000)