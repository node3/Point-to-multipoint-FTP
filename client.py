import sys
import socket
from utils import *


def get_file_chunks(file_path, mss):
    f = open(file_path, 'rb')
    data = f.read()
    f.close()
    offset = 0
    while offset*mss < len(data):
        yield data[offset*mss:(offset+1)*mss]
        offset += 1


def p2mp_ftp_send(recipients, file_chunks):
    for file_chunk in file_chunks:
        pdu = SendPDU(file_chunk, 'data')
        for recipient in recipients:
            rdt_send(recipient[0], recipient[1], pdu)


def rdt_send(ip, port, pdu):
    data_sent = False
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.settimeout(5)
    while not data_sent:
        try:
            client_socket.sendto(pdu.encode(), (ip, port))
            data, server = client_socket.recvfrom(socket_buffer)
            ack = ReceivePDU(data)
            if ack.sequence_number == pdu.sequence_number:
                data_sent = True
                print "Got ack for %d" % ack.sequence_number
        except socket.timeout:
            print 'rdt_send timeout for %s,%s' % (ip, port)


script_name, file_path, mss = sys.argv
mss = int(mss)

timeout = 5
sequence_number = 0
socket_buffer = mss + 64

recipients = [["localhost", 7735]]

file_chunks = get_file_chunks(file_path, mss)
p2mp_ftp_send(recipients, file_chunks)