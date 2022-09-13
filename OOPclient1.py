"""
    yotam shavit
"""

# mouduls
import socket
import sys
from constants1 import *

# constatns
IP = "127.0.0.1"
RECEIVED_FILE_LOCATION = "c:\\test_folder\\client"


class Client(object):
    def __init__(self, ip, port):
        try:
            # client socket init
            self.c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            self.c.connect((ip, port))
        except socket.error as msg:
            print('Connection failure: ', msg, "\n terminating program")
            sys.exit(1)

    @staticmethod
    def vaild_request(request):
        """
         checks if the input is vaild
        """
        # split to request and parameters
        req_and_prms = request.split()
        if len(req_and_prms) > LEN_REQ_PARS:
            req = req_and_prms[FIRST_REQ_PARS]
            pars = req_and_prms[PARS:]
            if not DIC_LIST.get(req) is None:
                if DIC_LIST[req] == len(pars):
                    return True
                else:
                    return False
            else:
                return False
        else:
            req = req_and_prms[FIRST_REQ_PARS]
            pars = None  # no parameters
            if not DIC_LIST.get(req) is None:
                if DIC_LIST[req] == NO_PARS:
                    return True
                else:
                    return False
            else:
                return False

    def send_request_to_server(self, request):
        """
        Function that send the client request to the server,
        using protocol  "hello" -> "0005hello"
        5 shows the lengh of the data

        """
        # sending the input to the server
        req_enc = request.encode()
        raw_size = str(len(req_enc)).zfill(MSG_LEN).encode()
        answer = raw_size + req_enc
        self.c.send(answer)

    def handle_server_responde(self, request):
        """
        Function that receive the server responde and prints it.
        """
        # reciving message length
        if request.split()[FIRST_REQ_PARS] == 'SEND_FILE':
            self.receive_file(request)
        raw_size = self.c.recv(MSG_LEN)
        data_size = raw_size.decode()

        if data_size.isdigit():
            # reciving responde from server
            data = self.c.recv(int(data_size))

            # prints:
            print(data.decode())  # print string
            return data

    def receive_file(self, request):
        """
        Recving file from server.
        """
        received_base_name = (request.split()[1]).split("\\")[SOURCE_BASE_NAME]
        answer_file = \
            RECEIVED_FILE_LOCATION + "\\" + received_base_name.lower()
        done = False
        data = b''
        try:
            with open(answer_file, "wb") as f:
                while not done:
                    raw_size = self.c.recv(MSG_LEN)
                    size = raw_size.decode()
                    if size.isdigit():
                        data = self.c.recv(int(size))
                    if data == b'-1':
                        done = True
                    else:
                        f.write(data)
        except:
            pass

    def handle_user_input(self):
        '''
        handels user inputs to server
        '''
        request = ""
        while request.upper() != "QUIT" and request.upper() != "EXIT":
            try:
                # reading input
                request = input('please enter a request ')
                request = request.upper()

                if self.vaild_request(request):
                    # sending the input to the server
                    self.send_request_to_server(request)

                    # reciving responde from server and printing it
                    self.handle_server_responde(request)
                else:
                    print("illegal request")
            except socket.error as msg:
                print("socket error:", msg)
                request = "QUIT"
            except Exception as msg:
                print("general error:", msg)

    def send_command(self, request):
        rsp = ""
        if self.vaild_request(request):
            self.send_request_to_server(request)
            rsp = self.handle_server_responde(request)
        return rsp


def main():
    """
    main -
    building the client's object and calling the in class handle function
    """
    client = Client(IP, PORT)
    client.handle_user_input()


if __name__ == '__main__':
    main()
