import hashlib

def main():
    '''
        Script para gerar o hash de uma senha e armazenar em um arquivo txt
    '''
    usuario = input("Digite o nome de usuário: ")
    senha = input("Digite a senha: ")

    senha = hashlib.md5(senha.encode())
    
    with open(usuario + ".txt", "w") as arq:
        arq.write(senha.digest().hex())

if __name__ == '__main__':
    main()