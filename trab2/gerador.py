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

def salvarSenha(caminho_arquivo, senha):
    with open(caminho_arquivo, "wb") as arquivo:
        arquivo.write(senha)

def login():
    print("------- LOGIN --------")
    nome = input("Digite o nome de usuário: ")
    if usuarioExistente(nome):
        senha_informada = input("Digite uma senha local: ") # Senha informada pelo usuário no momento de login
        senha_local = carregarSenha("senha_local_" + nome + ".bin") # Carrega a senha local
        if senha_local == hashlib.md5(senha_informada.encode()).digest(): # Verifica se a senha informada está correta
            semente = carregarSenha("semente_" + nome + ".bin")
        else:
            print("Senha incorreta!") # Caso seja incorreta, informa o usuário e finaliza o programa
            exit(-1)

        # Exemplo de como converter de volta de bytes para hexa, caso necessário
        # print(binascii.hexlify(semente))
        # print(binascii.hexlify(senha_local))

    else:
        semente = input("Digite um número para ser a semente: ")
        senha_local = input("Digite uma senha local: ")

        semente = hashlib.md5(semente.encode()).digest()
        senha_local = hashlib.md5(senha_local.encode()).digest()

        salvarSenha("semente_" + nome + ".bin", semente)
        salvarSenha("senha_local_" + nome + ".bin", senha_local)

    return semente

def gerar(semente):
    senhas = []
    senha = semente + datetime.now().strftime("%d%m%Y%H%M").encode()
    for _ in range(5):
        senha = hashlib.md5(senha).digest()
        senhas.append(binascii.hexlify(senha)[:6])

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