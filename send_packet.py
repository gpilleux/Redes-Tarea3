import socket

'''
 sirve para enviar
un paquete a un cierto puerto. Se les deja para poder realizar pruebas más fácilmente.
Es importante notar que send_packet no realiza ningún formateo de los paquetes (eso
queda a responsabilidad suya).
'''

def send_packet(port, message):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = ('localhost', port)

    try:
        sock.sendto(message.encode(), server_address)
    finally:
        sock.close()
