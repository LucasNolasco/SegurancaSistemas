#!/usr/bin/python3

import hashlib
import os.path
from datetime import datetime
import binascii

def usuarioExistente(nome):
    if os.path.isfile("semente_" + nome + ".bin") and os.path.isfile("senha_local_" + nome + ".bin"):
        return True
    else:
        return False

def carregarSenha(caminho_arquivo):
    with open(caminho_arquivo, "rb") as arquivo:
        senha = arquivo.read()

    return senha

def login():
    print("------- LOGIN --------")
    nome = input("Digite o nome de usuário: ")
    if usuarioExistente(nome):
        semente = carregarSenha("semente_" + nome + ".bin")
        senha_temporaria = input("Digite a senha temporária: ")
        senhas = gerar(semente)

        if senha_temporaria in senhas:
            print("Chave validada!")
        else:
            print("Chave incorreta!")

    else:
        print("Usuário não registrado!")
        exit(-1)

    return semente

def gerar(semente):
    senhas = []
    senha = semente + datetime.now().strftime("%d%m%Y%H%M").encode()
    for _ in range(5):
        senha = hashlib.md5(senha).digest()
        senhas.append(binascii.hexlify(senha)[:6].decode())

    return senhas

def main():
    semente = login()

    opcao = 0 # IDLE
    while opcao != 2:
        print("-------- MENU -----------")
        print("Digite a operação desejada: ")
        print("1 - Gerar senha")
        print("2 - Sair")
        opcao = int(input("Opção escolhida: "))

        if opcao == 1: # Gerar lista de senhas
            senhas = gerar(semente)
            print("-------- SENHAS -----------")
            print("Senhas válidas para {0}:".format(datetime.now().strftime("%Hh%M")))
            for senha in senhas:
                print("\t-> " + senha.decode())

if __name__ == '__main__':
    main()