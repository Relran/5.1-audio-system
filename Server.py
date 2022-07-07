import select
import socket


class Server:
    def __init__(self):
        self.ip = "0.0.0.0"
        self.port = 5555
        self.speaker_dict = []
        self.just_connected = []
        self.speakers_list = ["center", "FL", "FR", "bass", "SL", "SR"]
        self.server_socket = None
        self.initialize_server()

    def connect_speakers(self):
        print("Scanning for a device")
        client_sockets = []
        while True:
            while self.speakers_list:
                r_list, w_list, x_list = select.select([self.server_socket] + client_sockets,
                                                       client_sockets, [])

                for current_socket in r_list:
                    if current_socket is self.server_socket:
                        print("A device has been found")
                        connection, client_address = current_socket.accept()
                        connection.send(self.speakers_list[0].encode())

                        print("New client joined! Client: " + self.speakers_list[0] + '\n')
                        self.just_connected.append((self.speakers_list[0], connection))
                        self.speakers_list.remove(self.speakers_list[0])

    def initialize_server(self):
        try:  # preventing multiple servers construction
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.bind((self.ip, self.port))
            self.server_socket.listen(True)
            print("Server has been set up")
        except Exception:
            return
