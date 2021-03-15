#!/usr/bin/python3

import hashlib
import os.path

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

def menu():
    print("------- MENU --------")
    nome = input("Digite o nome de usuário: ")
    if usuarioExistente(nome):
        semente = carregarSenha("semente_" + nome + ".bin")
        senha_local = carregarSenha("senha_local_" + nome + ".bin")

    else:
        semente = input("Digite um número para ser a semente: ")
        senha_local = input("Digite uma senha local: ")

        semente = hashlib.md5(semente.encode()).digest()
        senha_local = hashlib.md5(senha_local.encode()).digest()

        salvarSenha("semente_" + nome + ".bin", semente)
        salvarSenha("senha_local_" + nome + ".bin", senha_local)

    print(nome)
    print(semente)
    print(senha_local)

    return nome, semente, senha_local

def main():
    nome, semente, senha_local = menu()

if __name__ == '__main__':
    main()