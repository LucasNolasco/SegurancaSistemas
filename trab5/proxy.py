import os
import threading
import socket
from signal import signal, SIGINT
import sys

class WebServer:
    def main(self):
        port = 5001
        host = 'localhost'

        tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp.bind((host, port))
        tcp.listen(1)

        while True:
            (con, (ip, porta)) = tcp.accept()
                
            request_thread = HttpRequest(con)
            request_thread.start()
                
class HttpRequest(threading.Thread):
    def __init__(self, request_socket):
        threading.Thread.__init__(self)
        self.request_socket = request_socket
        self.CRLF = "\r\n"

    def run(self):
        self.request_socket.settimeout(20)
        input_stream = b''
        while True:
            stream_slice = self.request_socket.recv(4096)
            input_stream += stream_slice
            if len(stream_slice) < 4096: # Se não tem mais nada a receber
                break

        input_stream = input_stream.decode()

        # input_stream = self.request_socket.recv(4096).decode()

        print(input_stream)
        original_host = input_stream.split(self.CRLF)[1].replace("Host: ", "")
        print(original_host)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(10)
        s.connect((original_host, 80))
        s.sendall(input_stream.encode())

        data = b''
        while True:
            stream_slice = s.recv(4096)
            if not stream_slice:
                break
            
            data += stream_slice                

        print(data)

        s.shutdown(socket.SHUT_RDWR)
        s.close()

        self.request_socket.sendall(data)

        self.request_socket.shutdown(socket.SHUT_RDWR)        
        self.request_socket.close()

    def processRequest(self):
        input_stream = self.request_socket.recv(1024)

        request_line = input_stream.split(self.CRLF)[0]

        print(request_line)

        if request_line.split(" ")[0] == "GET":
            file_name = request_line.split(" ")[1]
            file_name = os.getcwd() + file_name

            file_exists = True
            if(os.path.isfile(file_name)):
                fis = open(file_name, "rb")
            else:
                file_exists = False

            status_line = ""
            content_type_line = ""
            entity_body = ""
            
            if(file_exists):
                status_line = "HTTP/1.0 200 OK"
                content_type_line = "Content-Type: " + self.contentType(file_name)

            else:
                status_line = "HTTP/1.0 404 Not Found"
                content_type_line = "Content-Type: text/html"
                entity_body = "<HTML>" + "<HEAD><TITLE>Not Found</TITLE></HEAD>" + "<BODY>Not Found</BODY></HTML>"

            self.request_socket.send(status_line)
            self.request_socket.send(self.CRLF)
            self.request_socket.send(content_type_line)
            self.request_socket.send(self.CRLF)

            self.request_socket.send(self.CRLF)

            if(file_exists):
                file_piece = fis.read(1024)
                while(file_piece):
                    self.request_socket.send(file_piece)
                    file_piece = fis.read(1024)

                fis.close()

            else:
                self.request_socket.send(entity_body)

        else:
            print("Falha na execucao")

        self.request_socket.shutdown(socket.SHUT_RDWR)        
        self.request_socket.close()
    
    def contentType(self, file_name):
        file_end = file_name.split(".")[-1]
        if (file_end == "htm" or file_end == "html"):
            return "text/html"

        elif(file_end == "jpg"):            
            return "image/jpeg"

        elif(file_end == "png" or file_end == "gif"):
            return "image/" + file_end


        return "application/octet-stream"


if __name__ == '__main__':
    server = WebServer()
    try:
        server.main()
    except KeyboardInterrupt:
        sys.exit(1)
