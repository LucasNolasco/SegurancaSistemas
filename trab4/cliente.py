#!/usr/bin/python3

import time
from Crypto.Cipher import DES
import random
import sys
import requests
import hashlib

# =======================================

# Url dos demais agentes

AUTENTICATION_SERVICE_URL = "http://localhost:5000/authentication_service/authenticate"
TICKET_GRANTING_SERVICE_URL = "http://localhost:5001/ticket_granting_service/get_ticket"
SERVICE_URL = "http://localhost:5002/service/"

# =======================================

def pad(text):
    while len(text) % 8 != 0:
        text += '\x00'

    return text

# =======================================

def menu():
    '''
        Nome: menu
        Método responsável por obter as informações básicas para a solicitação e
        acesso a um determinado serviço. Essas informações são:

            ID_C - Identificação do usuário
            ID_S - Identificação do serviço
            S_R - Operação que se deseja que o serviço execute
            T_R - Tempo requisitado para duração do direito de acesso em segundos
    '''
    ID_C = input("Insira o id do cliente: ")
    ID_S = input("Insira o id do serviço: ")
    S_R = input("Digite o serviço desejado: ")
    
    T_R = input("Insira o prazo de validade para acesso ao serviço em segundos: ")
    T_R = str(time.time() + int(T_R)) # Adiciona o intervalo de tempo desejado no timestamp atual

    
    key = input(f"Digite a chave para criptografar: ")
    key = hashlib.md5(key.encode()).digest() # Cria o hash da chave
    key = key[:8] # Corta o hash da chave no tamanho necessário para o DES

    return ID_C, ID_S, T_R, S_R, key

# =======================================

def main():
    ID_C, ID_S, T_R, S_R, key = menu() # Obtém as informações do usuário e o serviço que ele deseja acessar

    # ========================= Envia a M1 ====================================

    cifra_des = DES.new(key, DES.MODE_ECB) # Cria a instância de criptografia simétrica
    m1_ID_S = cifra_des.encrypt(pad(ID_S).encode()) # Criptografa o ID do usuário
    m1_T_R = cifra_des.encrypt(pad(T_R).encode()) # Criptografa o timeout solicitado
    N1 = random.randint(0, sys.maxsize) # Gera o número aleatório
    m1_N1 = cifra_des.encrypt(pad(str(N1)).encode())
    
    m1 = {
        "ID_C": ID_C,
        "ID_S": m1_ID_S.hex(),
        "T_R": m1_T_R.hex(),
        "N1": m1_N1.hex()
    }

    m2 = requests.get(AUTENTICATION_SERVICE_URL, json=m1) # Envia a mensagem M1 para o AS

    # ========================= Recebe a M2 ===================================
    
    m2 = m2.json() # Lê a resposta enviada pelo AS
    if "erro" in m2:
        print("Erro ao contactar o AS. Falha ocorrida: {0}".format(m2["erro"]))
        exit(-1)

    K_c_tgs = cifra_des.decrypt(bytes.fromhex(m2["K_c_tgs"])) # Descriptografa a chave de sessão para comunicação com o TGS
    N1_recebido = cifra_des.decrypt(bytes.fromhex(m2["N1"])).decode() # Descriptografa o número aleatório recebido
    
    if int(N1) != int(N1_recebido.replace("\x00", "")): # Verifica se a resposta do AS corresponde à solicitação feita
        print(f"Erro na requisição. Resposta enviada pelo AS não corresponde à solicitação feita. N1 enviado: {N1}, N1 recebido: {N1_recebido}")
        exit(-1)

    # ========================= Envia a M3 ====================================

    cifra_sessao_tgs = DES.new(K_c_tgs, DES.MODE_ECB) # Cria a cifra utilizando a chave de sessão para comunicação com o TGS
    m3_ID_C = cifra_sessao_tgs.encrypt(pad(ID_C).encode()) # Criptografa o id do usuário
    m3_ID_S = cifra_sessao_tgs.encrypt(pad(ID_S).encode()) # Criptografa o id do serviço
    m3_T_R = cifra_sessao_tgs.encrypt(pad(T_R).encode()) # Criptografa o tempo de acesso solicitado
    N2 = random.randint(0, sys.maxsize) # Gera um novo número aleatório
    m3_N2 = cifra_sessao_tgs.encrypt(pad(str(N2)).encode()) # Criptografa esse novo número aleatório

    m3 = {
        "ID_C": m3_ID_C.hex(),
        "ID_S": m3_ID_S.hex(),
        "T_R": m3_T_R.hex(),
        "N2": m3_N2.hex(),
        "T_c_tgs": m2["T_c_tgs"]
    }

    m4 = requests.get(TICKET_GRANTING_SERVICE_URL, json=m3) # Envia a M3 para o TGS

    # ======================= Recebe a M4 =====================================
    
    m4 = m4.json()
    if "erro" in m4:
        print("Erro ao contactar o TGS. Falha ocorrida: {0}".format(m4["erro"]))
        exit(-1)

    K_c_s = cifra_sessao_tgs.decrypt(bytes.fromhex(m4["K_c_s"])) # Decodifica a chave de sessão recebida para a comunicação com o serviço
    T_A = cifra_sessao_tgs.decrypt(bytes.fromhex(m4["T_A"])).decode() # Decodifica o tempo recebido
    N2_recebido = cifra_sessao_tgs.decrypt(bytes.fromhex(m4["N2"])).decode() # Decodifica o N2 recebido

    if int(N2) != int(N2_recebido.replace("\x00", "")): # Verifica se a resposta recebida corresponde à solicitação feita ao TGS
        print(f"Erro na requisição. Resposta enviada pelo TGS não corresponde à solicitação feita. N2 enviado: {N2}, N2 recebido: {N2_recebido}")
        exit(-1)

    # ======================= Envia a M5 ======================================

    cifra_sessao_servico = DES.new(K_c_s, DES.MODE_ECB) # Cria a cifra com a chave de sessão entre o cliente e o serviço
    m5_ID_C = cifra_sessao_servico.encrypt(pad(ID_C).encode()) # Criptografa o ID do cliente
    m5_T_A = cifra_sessao_servico.encrypt(pad(T_A).encode()) # Criptografa o tempo limite de acesso 
    m5_S_R = cifra_sessao_servico.encrypt(pad(S_R).encode()) # Criptografa a operação desejada do serviço
    N3 = random.randint(0, sys.maxsize) # Cria um novo número aleatório
    m5_N3 = cifra_sessao_servico.encrypt(pad(str(N3)).encode()) # Criptografa esse número aleatório

    m5 = {
        "ID_C": m5_ID_C.hex(),
        "T_A": m5_T_A.hex(),
        "S_R": m5_S_R.hex(),
        "N3": m5_N3.hex(),
        "T_c_s": m4["T_c_s"]
    }

    m6 = requests.get(SERVICE_URL + ID_S, json=m5) # Envia a M5 para o serviço
    
    # =============== Lê M6 =====================================
    m6 = m6.json()
    if "erro" in m6:
        print("Erro ao contactar o serviço. Falha ocorrida: {0}".format(m6["erro"]))
        exit(-1)

    resposta = cifra_sessao_servico.decrypt(bytes.fromhex(m6["Resposta"])).decode() # Descriptografa a resposta recebida
    N3_recebido = cifra_sessao_servico.decrypt(bytes.fromhex(m6["N3"])).decode() # Descriptografa o N3 recebido

    if int(N3) != int(N3_recebido.replace("\x00", "")): # Verifica se a resposta recebida corresponde à solicitação feita ao serviço
        print(f"Erro na requisição. Resposta enviada pelo serviço não corresponde à solicitação feita. N3 enviado: {N3}, N3 recebido: {N3_recebido}")
        exit(-1)

    print(f"Serviço acessado com sucesso!")
    print(f"Resposta recebida: {resposta}")

if __name__=='__main__':
    main()