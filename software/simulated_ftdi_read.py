# server.py
import socket, threading, time

def main():

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    host = 'localhost'
    port = 5000

    # Bind to the port
    server_socket.bind((host, port))

    # Listen for incoming connections
    server_socket.listen(20)

    while True:
        data = input('Enter data to be received by host PC: ')

        # Establish a connection
        client_socket, addr = server_socket.accept()
        print('Got connection from', addr)

        # Send data to the client
        client_socket.send(data.encode('utf-8'))
        print('Sent:', data.encode('utf-8'))

        # Close the connection
        client_socket.close()

        time.sleep(0.1)

if __name__ == '__main__':
    main()