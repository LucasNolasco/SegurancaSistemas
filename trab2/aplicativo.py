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

def login():
    '''
    Nome: login
    Função responsável por obter o nome do usuário e a sua senha local
    e conferir se a senha local informada bate com a senha local real
    do usuário.

    Valor de retorno: hash da semente do usuário
    '''

    print("------- LOGIN --------")
    nome = input("Digite o nome de usuário: ")
    if usuarioExistente(nome): # Verifica se o usuário informado existe
        semente, _ = carregarSenhas(nome + ".bin") # Carrega a semente do usuário

    else:
        semente = None
        print("Usuário não registrado!")

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
    senha = semente + datetime.now().strftime("%d%m%Y%H%M").encode() # Adiciona o dia, mês, ano, hora e minuto atual ao hash da semente
    for _ in range(5):
        senha = hashlib.md5(senha).digest() # Gera o hash
        senhas.append(binascii.hexlify(senha)[:6].decode()) # Adiciona à lista de senhas os primeiros 6 caracteres do resultado do hash em hexa

    return senhas

def main():
    ultima_senha_usada = None
    opcao = 0 # IDLE

    while opcao != 2:
        print("-------- MENU -----------")
        print("Digite a operação desejada: ")
        print("1 - Autenticar")
        print("2 - Sair")

        try:
            opcao = int(input("Opção escolhida: "))
        except ValueError:
            opcao = 0
            print("Opcao inexistente")

        if opcao == 1:
            semente = login() # Efetua o login
            if semente is not None:
                senha_temporaria = input("Digite a senha temporária: ") # Solicita a senha temporária para o usuário
                senhas = gerar(semente)
                try: # Procura a última chave utilizada na lista de senhas para saber quais das senhas ainda podem ser utilizadas
                    index_inicial = senhas.index(ultima_senha_usada)
                except ValueError: # Caso nenhuma senha tenha sido utilizada ainda, permite que todas sejam utilizadas
                    index_inicial = len(senhas)
                if senha_temporaria in senhas[:index_inicial]: # Verifica se a senha digitada está dentro das senhas possíveis
                    ultima_senha_usada = senha_temporaria # Atualiza a última senha digitada
                    print("Chave validada!")
                else:
                    print("Chave incorreta!")

if __name__ == '__main__':
    main()