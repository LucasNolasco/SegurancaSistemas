import os
import threading
import socket
from signal import signal, SIGINT
import sys
import syslog
import hashlib

def main():
    port = 5001
    host = 'localhost'

    checarIntegridade()

    tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Configura o socket que o proxy irá ouvir
    tcp.bind((host, port))
    tcp.listen(1)

    print("Proxy iniciado...")
    syslog.syslog("Proxy iniciado...")

    while True:
        (con, (ip, porta)) = tcp.accept() # Espera novas conexões
            
        request_thread = HttpRequest(con, ip) # Cria uma thread para lidar com cada nova conexão
        request_thread.start()
                
def checarIntegridade():
    with open("proxy.py", "rb") as f:
        bytes = f.read() # read file as bytes
        current_hash = hashlib.md5(bytes).hexdigest()

    with open("MD5.txt", "r") as f:
        correct_hash = f.readline()

    if current_hash != correct_hash:
        syslog.syslog(f"Falha ao verificar a integridade do arquivo de proxy. Hash correto: {correct_hash}, Hash encontrado: {current_hash}")
        print(f"Falha ao verificar a integridade do arquivo de proxy. Hash correto: {correct_hash}, Hash encontrado: {current_hash}")
        exit(-1)

class HttpRequest(threading.Thread):
    '''
        Nome: HttpRequest
        Classe para tratar um http request recebido pelo proxy em uma thread
        separada. Nele, o objeto solicitado no request é analisado e, caso
        tenha o termo 'monitorando', o proxy retorna uma página indicando
        que o acesso não está autorizado. Caso não tenha o termo 'monitorando',
        é aberto um socket para encaminhar o request para o servidor desejado
        e após isso encaminha a resposta de volta para o cliente.
    '''
    def __init__(self, request_socket, cliente):
        '''
            Nome: __init__
            Construtor da classe HttpRequest. Método responsável por configurar
            alguns parâmetros da classe.

            Parâmetros:
                - request_socket: Socket com a requisição do cliente
                - cliente: Ip do cliente que fez a requisição inicial
        '''
        threading.Thread.__init__(self)
        self.request_socket = request_socket
        self.CRLF = "\r\n"
        self.cliente = cliente

        self.socket_timeout = 0.1
        self.buffer_size = 4096

    def recvall(self, recv_socket):
        '''
            Nome: recvall
            Método para receber todos os dados do buffer de um determinado
            socket.

            Parâmetros:
                - recv_socket: Socket do qual se deseja receber

            Valor de retorno:
                - buffer: Array de bytes contendo todos os dados recebidos
                            no socket informado.
        '''
        buffer = b''
        while True:
            try:
                dados = recv_socket.recv(self.buffer_size)
                buffer += dados
                if not dados: # Se não tem mais nada a receber
                    break
            except: # Caso ocorra algum erro (timeout, por exemplo)
                break

        return buffer

    def run(self):
        '''
            Nome: run
            Método a ser executado pela thread. Neste método, o request
            recebido do cliente é analisado. Caso seja um request válido
            (sem conter a palavra 'monitorando'), abre-se uma conexão com
            o host original e encaminha-se o request e a resposta desse
            request é encaminhada de volta para o cliente. Caso seja um
            request inválido, retorna para o cliente uma página com a
            mensagem 'Acesso não autorizado!'.
        '''
        self.request_socket.settimeout(self.socket_timeout) # Configura o timeout do socket
        request_original = self.recvall(self.request_socket) # Lê os dados recebidos nele

        original_host = request_original.decode().split(self.CRLF)[1].replace("Host: ", "") # Faz o parsing do host a partir do request
        objeto_requisitado = request_original.decode().split(self.CRLF)[0].split(" ")[1] # Faz o parsing do objeto requisitado

        rejeitado = False
        if "monitorando" in objeto_requisitado.lower(): # Verifica se o objeto requisitado contém a palavra 'monitorando'
            status_line = b"HTTP/1.0 200 OK"
            content_type_line = b"Content-Type: text/html"
            entity_body = "<HTML>" + "<HEAD><TITLE>Monitoramento</TITLE></HEAD>" + "<BODY>Acesso nao autorizado!</BODY></HTML>"

            self.request_socket.send(status_line) # Envia a página de acesso não autorizado
            self.request_socket.send(self.CRLF.encode())
            self.request_socket.send(content_type_line)
            self.request_socket.send(self.CRLF.encode())
            self.request_socket.send(self.CRLF.encode())
            self.request_socket.send(entity_body.encode())

            codigo_resposta = "200 OK"
            rejeitado = True

        else: # Caso seja um acesso válido
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Abre um novo socket
            s.settimeout(self.socket_timeout) # Configura o timeout
            s.connect((original_host, 80)) # Abre comunicação com o host
            s.sendall(request_original) # Encaminha o request

            resposta_servidor = self.recvall(s) # Recebe a resposta do host para o request feito

            s.shutdown(socket.SHUT_RDWR) # Fecha o socket
            s.close()

            self.request_socket.sendall(resposta_servidor) # Encaminha a resposta para o cliente

            codigo_resposta = resposta_servidor.split(self.CRLF.encode())[0].decode().replace("HTTP/1.1 ", "") # Faz o parsing do código da resposta recebida

        self.request_socket.shutdown(socket.SHUT_RDWR) # Fecha o socket do request do cliente
        self.request_socket.close()

        log_message = f'Cliente: {self.cliente}, Servidor: {original_host}, Código de resposta: {codigo_resposta}' # Constrói a mensagem de log

        if rejeitado: # Caso seja um acesso rejeitado, adiciona isso à mensagem que vai para o log
            log_message += ', Request rejeitado'

        print(log_message) # Exibe a mensagem de log no proxy
        syslog.syslog(log_message) # Salva a mensagem de log no syslog

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(1)
