"""yotamm shavit server"""

import glob
import os
import shutil
# mouduls
import socket
import subprocess
import sys
import threading

from PIL import ImageGrab

# constants
from constants1 import *

IP = '0.0.0.0'
SAVE_LOC = 'c:\\test_folder\\server\\screen.jpg'


class Server(object):
    def __init__(self, ip, port):
        try:
            # server socket init
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket = server_socket
            self.thread_counter = 0
            self.hist = {}

            # connecting to the IP
            self.server_socket.bind((ip, port))
            # attempt to connect
            self.server_socket.listen(1)
        except socket.error as m:
            print("Connection failure:", m, "\n terminating program")
            sys.exit(1)

    def receive_client_request(self, client_socket, address):
        """
        Function that recives the client request and returns
        it as a string
        """
        # read from socket
        raw_size = client_socket.recv(MSG_LEN)
        data_size = raw_size.decode()

        if data_size.isdigit():
            # recive the client message
            raw_request = client_socket.recv(int(data_size))
            # returns the client message
            request = raw_request.decode()

            # split to request and parameters
            req_and_prms = request.split()
            #add to history
            self.hist[address] = req_and_prms[FIRST_REQ_PARS]
            if len(req_and_prms) > LEN_REQ_PARS:
                return req_and_prms[FIRST_REQ_PARS], req_and_prms[PARS:]
            else:
                return req_and_prms[FIRST_REQ_PARS], None  # no parameters
        else:
            return None, None  # illegal size parameter

    def handle_clients(self):
        """handle requests until ser asks to exit"""
        done = False
        while not done:
            try:
                client_socket, address = self.server_socket.accept()
                clnt_thread = threading.Thread(target=self.handle_single_client, args=(client_socket, address))
                clnt_thread.start()
            except socket.error as msg:
                print("socket error handle clients", msg)

    def handle_single_client(self, client_socket, address):
        num = self.thread_counter
        self.thread_counter += 1
        print("starting thread ", num)
        done = False
        while not done:
            try:
                command, params = self.receive_client_request(client_socket, address)
                valid = self.check_client_request(command, params, client_socket)
                if valid:
                    response = self.handle_client_request(command, params, client_socket, address)
                    self.send_response_to_client(response, client_socket)
                else:
                    self.send_response_to_client("illegal command", client_socket)
                if command == 'EXIT ':
                    done = True
            except socket.error as msg:
                client_socket.close()
                print('Connection failure: %s\n ' % msg)
                done = True
                print("exiting thread", num)

    def check_client_request(self, request, params, sock):
        """
        Function that checks if the client request is vaild
        """
        if params is None:
            parcheck = NO_PARS
            params = ""
        else:
            parcheck = len(params)
        count = COUNT_START
        request = request.upper()
        if not DIC_LIST.get(request) is None:
            if DIC_LIST[request] == parcheck:
                for par in params:
                    if chr(BACK_SPLASH_ID) in par:
                        if os.path.isdir(par) or os.path.isfile(par):
                            count += COUNT_ADDER
                        else:
                            if request == "SEND_FILE":
                                sock.send(b'0002-1')
                    else:
                        count += COUNT_ADDER
            else:
                return False
        else:
            return False
        if count == parcheck:
            return True
        else:
            return False

    def handle_client_request(self, request, parmas, sock, address):
        """
        Function that call the function by the request
        the server recived from the client
        """
        if request == "TAKE_SCREENSHOT":
            return self.take_screenshot()
        elif request == "DIR":
            return self.list_folder(parmas[FIRST_PAR])
        elif request == "DELETE":
            return self.delete_file(parmas[FIRST_PAR])
        elif request == "COPY":
            return self.copy_file(parmas[FIRST_PAR], parmas[SECOND_PAR])
        elif request == "EXECUTE":
            return self.execute_program(parmas[FIRST_PAR])
        elif request == "HISTORY":
            return self.get_history(address)
        elif request == "SEND_FILE":
            return self.send_file(parmas[FIRST_PAR], sock)
        elif request == "QUIT":
            return "Quiting..."
        elif request == "EXIT":
            return "Exiting and shutting server down"

    def send_response_to_client(self, response, client_socket):
        """
        Function that send the client request to the server,
        using protocol  "hello" -> "0005hello"
        5 shows the lengh of the data
        """
        resp_enc = response.encode()
        raw_size = str(len(resp_enc)).zfill(MSG_LEN).encode()
        answer = raw_size + resp_enc
        # sending the encoded responde to the client
        client_socket.send(answer)

    def send_file(self, file_name, client_socket):
        """
         send file to client,using protocol
        """
        try:
            done = False
            with open(file_name, "rb") as f:
                while not done:
                    data = f.read(FILE_SEND_SIZE)
                    raw_size = (str(len(data)).zfill(4)).encode()
                    if not data:
                        done = True
                        answer = b'0002' + b'-1'
                        client_socket.send(answer)
                    else:
                        answer = raw_size + data
                        client_socket.send(answer)
            return "file sent"
        except:
            return "Error, coulden't send file"

    def take_screenshot(self):
        """
         take screen shot and save.
        """
        try:
            # take screen shot
            im = ImageGrab.grab()
            # # save it
            im.save(SAVE_LOC)
            return 'screenshot taken'
        except:
            return "Error, couldn't take screenshot"

    def get_history(self, address):
        try:
            result = self.hist.get(address)
            return result
        except Exception as m:
            print("get history error", m)

    def list_folder(self, folder):
        """
        Function that returns the files in the recived folder path.
        """
        folder += "\*.*"
        file_list = glob.glob(folder)
        return str(file_list)

    def delete_file(self, file):
        """
        Function that recive a file and deletes it.
        """
        try:
            os.remove(file)
            return "file deleted"
        except Exception as m:
            return m + "coulden't delete file"

    def copy_file(self, src, dst):
        """
        Function that recive source file path and distantion folder path
        and copy the file to the folder.
        """
        try:
            src = src.split("\\")
            file_basename = src[SOURCE_BASE_NAME].lower()
            src = "\\".join(src)
            dst += "\\" + file_basename
            shutil.copy(src, dst)
            return "file copied"
        except Exception as m:
            return m

    def execute_program(self, prog):
        """
        Function that execute a program
        """
        try:
            subprocess.call(prog)
            return "program executed"
        except Exception as m:
            return m


def main():
    """
    Main -
    Server main, creating server object and calling in class
     functions
    """
    # create server object and init a server socket
    server = Server(IP, PORT)
    # handle clients
    server.handle_clients()


if __name__ == '__main__':
    main()
