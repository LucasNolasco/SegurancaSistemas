#!/usr/bin/python3
from Crypto.Cipher import DES
import random
import sys
import requests

AUTENTICATION_SERVICE_URL = "http://localhost:5000/authentication_service/authenticate"

def pad(text):
    while len(text) % 8 != 0:
        text += '\x00'

    return text

def menu():
    ID_C = input("Insira o id do cliente: ")
    ID_S = input("Insira o id do serviço: ")
    T_R = input("Insira o prazo de validade para acesso ao serviço em segundos: ")

    tamanho_chave_correto = False
    while not tamanho_chave_correto:
        key = input(f"Digite a chave para criptografar (A chave deverá ter exatamente {DES.key_size} caracteres): ")
        tamanho_chave_correto = True
        if len(key) == DES.key_size:
            tamanho_chave_correto = True

    return ID_C, ID_S, T_R, key

def main():
    ID_C, ID_S, T_R, key = menu()

    cifra_des = DES.new(key.encode(), DES.MODE_ECB)

    ID_S = cifra_des.encrypt(pad(ID_S).encode())
    T_R = cifra_des.encrypt(pad(T_R).encode())
    N1 = random.randint(0, sys.maxsize)
    print(f"N1: {N1}")
    N1 = cifra_des.encrypt(pad(str(N1)).encode())

    request_data = {
        "ID_C": ID_C,
        "ID_S": ID_S.hex(),
        "T_R": T_R.hex(),
        "N1": N1.hex()
    }

    m2 = requests.get(AUTENTICATION_SERVICE_URL, json=request_data)
    m2 = m2.json()

    K_c_tgs = cifra_des.decrypt(bytes.fromhex(m2["K_c_tgs"]))
    N1_recebido = cifra_des.decrypt(bytes.fromhex(m2["N1"])).decode()
    print(f"K_c_tgs: {K_c_tgs}, N1: {N1_recebido}")

if __name__=='__main__':
    main()