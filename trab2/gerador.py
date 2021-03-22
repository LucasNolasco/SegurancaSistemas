#!/usr/bin/python3

import hashlib
import os.path
from datetime import datetime
import binascii

def usuarioExistente(nome):
    '''
    Nome: usuarioExistente
    Método responsável por verificar se um determinado usuário
    tem as credenciais salvas no sistema.

        - nome: Nome do usuário que se deseja verificar

    Valor de retorno: True, se o usuário estiver registrado
                      False, se o usuário não estiver registrado
    '''
    if os.path.isfile(nome + ".bin"):
        return True
    else:
        return False

def carregarSenhas(caminho_arquivo):
    '''
    Nome: carregarSenhas.
    Método responsável por carregar o hash das senhas à partir
    do arquivo informado.

        - caminho_arquivo: String contendo o caminho onde o arquivo está armazenado

    Valor de retorno:
        - semente: Hash da semente do usuário
        - senha_local: Hash da senha local do usuário
    '''
    with open(caminho_arquivo, "rb") as arquivo:
        conteudo = arquivo.read()

        tamanho = int(len(conteudo)/2)
        semente = conteudo[:tamanho]
        senha_local = conteudo[tamanho:]

    return semente, senha_local

def salvarSenhas(caminho_arquivo, semente, senha_local):
    '''
    Nome: salvarSenhas.
    Método responsável por salvar o hash das senhas do usuário em um 
    arquivo binário.

        - caminho_arquivo: Caminho do arquivo onde as senhas serão armazenadas
        - semente: Hash da semente do usuário
        - senha_local: Hash da senha local do usuário
    '''
    with open(caminho_arquivo, "wb") as arquivo:
        arquivo.write(semente)
        arquivo.write(senha_local)

def login():
    '''
    Nome: login
    Função responsável por obter o nome do usuário e a sua senha local
    e conferir se a senha local informada bate com a senha local real
    do usuário. Caso o usuário não esteja cadastrado, solicita uma 
    semente e uma senha local para criar um novo registro.

    Valor de retorno: hash da semente do usuário
    '''

    print("------- LOGIN --------")
    nome = input("Digite o nome de usuário: ")
    if usuarioExistente(nome): # Verifica se o usuário existe
        senha_informada = input("Digite sua senha local: ") # Senha informada pelo usuário no momento de login
        semente, senha_local = carregarSenhas(nome + ".bin") # Carrega a senha local
        if senha_local != hashlib.md5(senha_informada.encode()).digest(): # Verifica se a senha informada está correta
            print("Senha incorreta!") # Caso seja incorreta, informa o usuário e finaliza o programa
            exit(-1)

    else: # Caso o usuário não exista, cria um novo registro
        semente = input("Digite um número para ser a semente: ")
        senha_local = input("Digite uma senha local: ")

        semente = hashlib.md5(semente.encode()).digest() # Cria o hash da semente
        senha_local = hashlib.md5(senha_local.encode()).digest() # Cria o hash da senha local

        salvarSenhas(nome + ".bin", semente, senha_local) # Salva em disco o hash da senha local e da semente

    return semente

def gerar(semente):
    '''
    Nome: gerar
    Método responsável por gerar as possíveis senhas temporárias para o
    usuário naquele minuto. Para isso, soma-se o hash da semente
    do usuário com o dia, mes, ano, hora e minuto atual e então gera-se
    o hash desse valor. A primeira senha será os primeiros 6 caracteres
    desse hash resultante em hexadecimal. A partir desse hash, aplica-se
    o hash mais 4 vezes e do resultado de cada uma dessas operações sai
    as 4 senhas restantes.

        - semente: Hash da semente do usuário

    Valor de retorno:
        - senhas: Lista com as senhas temporárias do usuário para o minuto atual
    '''
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