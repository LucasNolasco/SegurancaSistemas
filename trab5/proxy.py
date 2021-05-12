import os
import threading
import socket
from signal import signal, SIGINT
import sys

SOCKET_TIMEOUT = 0.25

class WebServer:
    def main(self):
        port = 5001
        host = 'localhost'

        tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp.bind((host, port))
        tcp.listen(1)

        while True:
            (con, (ip, porta)) = tcp.accept()
                
            request_thread = HttpRequest(con, ip)
            request_thread.start()
                
class HttpRequest(threading.Thread):
    def __init__(self, request_socket, cliente):
        threading.Thread.__init__(self)
        self.request_socket = request_socket
        self.CRLF = "\r\n"
        self.cliente = cliente

    def recvall(self, recv_socket):
        buffer = b''
        while True:
            try:
                dados = recv_socket.recv(4096)
                buffer += dados
                if not dados: # Se não tem mais nada a receber
                    break
            except:
                break

        return buffer

    def run(self):
        self.request_socket.settimeout(SOCKET_TIMEOUT)
        request_original = self.recvall(self.request_socket)

        original_host = request_original.decode().split(self.CRLF)[1].replace("Host: ", "")
        objeto_requisitado = request_original.decode().split(self.CRLF)[0].split(" ")[1]

        if "monitorando" in objeto_requisitado.lower():
            status_line = b"HTTP/1.0 200 OK"
            content_type_line = b"Content-Type: text/html"
            entity_body = "<HTML>" + "<HEAD><TITLE>Monitoramento</TITLE></HEAD>" + "<BODY>Acesso nao autorizado</BODY></HTML>"

            self.request_socket.send(status_line)
            self.request_socket.send(self.CRLF.encode())
            self.request_socket.send(content_type_line)
            self.request_socket.send(self.CRLF.encode())
            self.request_socket.send(self.CRLF.encode())
            self.request_socket.send(entity_body.encode())

            codigo_resposta = 200

        else:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(SOCKET_TIMEOUT)
            s.connect((original_host, 80))
            s.sendall(request_original)

            resposta_servidor = self.recvall(s)

            s.shutdown(socket.SHUT_RDWR)
            s.close()

            self.request_socket.sendall(resposta_servidor)

            codigo_resposta = resposta_servidor.split(self.CRLF.encode())[0].decode().split(" ")[1]

        self.request_socket.shutdown(socket.SHUT_RDWR)        
        self.request_socket.close()

        print(f'-----------------------\n' \
              f'Cliente: {self.cliente},\n' \
              f'Servidor: {original_host},\n' \
              f'Objeto requisitado: {objeto_requisitado},\n'
              f'Código de resposta: {codigo_resposta}\n' 
        )

if __name__ == '__main__':
    server = WebServer()
    try:
        server.main()
    except KeyboardInterrupt:
        sys.exit(1)
