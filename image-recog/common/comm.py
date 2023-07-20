#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec  8 19:54:45 2016

@author: markov

Provides two classes Client and Server for communication
with text, audio and image data.

Communication Protocol
"""

import socket
import struct

# Message header length
# 1.command (int) - 4 bytes
# 2.message number (int, int) - 8 bytes
# 3.data type (int) - 4 bytes
# 4.data size (int) - 4 bytes

MESS_HEAD_LEN = 20

# Commands
CMDS_DEC = {0: 'init', 1: 'request', 2: 'result',
            3: 'confirm', 4: 'end', 5: 'error'}
CMDS_ENC = {v: k for k, v in CMDS_DEC.items()}

# Data types
DT_DEC = {0: None, 1: 'text', 2: 'image', 3: 'audio', 4: 'binary'}
DT_ENC = {v: k for k, v in DT_DEC.items()}


# Helper function
def get_bytes(sock, data_size):

    if data_size == 0:
        return None

    r_bytes = 0
    chunks = []
    while r_bytes < data_size:
        chunk = sock.recv(min(data_size - r_bytes, 2048))
        if chunk == b'':
            raise RuntimeError('socket connection broken')
        r_bytes += len(chunk)
        chunks.append(chunk)

    return b''.join(chunks)


# Message receive function
def receive(sock):

    while 1:
        # Get message header
        command, mess_num, from_num, data_type, data_size = \
            struct.unpack('5i', sock.recv(MESS_HEAD_LEN))

#        print(command, mess_num, from_num, data_type, data_size)

        # Checks
        if command not in CMDS_DEC:
            raise ValueError('Unknown command received - %i!' % command)
        if data_type not in DT_DEC:
            raise ValueError('Unknown data type received - %i!' % data_type)

        data = None

        if data_size > 0:
            # Get data
            data = get_bytes(sock, data_size)

            # Convert if necessary
            if DT_DEC[data_type] == 'text':
                data = data.decode('utf-8')

            if DT_DEC[data_type] == 'image':
                pass

            if DT_DEC[data_type] == 'audio':
                raise ValueError('Audio data handling NOT implemented yet!')

        yield CMDS_DEC[command], DT_DEC[data_type], data

        # Finish if last message received
        if mess_num == from_num:
            break


# Send message function
def send(sock, command, data, data_type, mess_num, from_num):

    # Checks
    if command not in CMDS_ENC:
        raise ValueError('Unknown command to send - %s!' % command)
    if data_type not in DT_ENC:
        raise ValueError('Unknown data type to send - %s!' % data_type)

    if not data:
        sock.sendall(struct.pack('5i', CMDS_ENC[
                     command], mess_num, from_num, 0, 0))
    else:
        if data_type == 'text':
            msg = data.encode('utf-8')
        elif data_type == 'image':
            msg = data
        elif data_type == 'audio':
            raise ValueError('Audio data handling NOT implemented yet!')
        elif data_type == 'binary':
            msg = data
        else:
            raise ValueError('Unknown data type: %s' % data_type)

        # Send header
        sock.sendall(struct.pack('5i', CMDS_ENC[command], mess_num,
                                 from_num, DT_ENC[data_type], len(msg)))
        # Send message
        sock.sendall(msg)


class Server:

    def __init__(self, port=10000):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host = socket.gethostbyname(socket.gethostname())
        server_address = (host, port)
        print('Starting up on %s port %s' % server_address)
        self.sock.bind(server_address)
        # Listen for incoming connections
        self.sock.listen(5)

    def waitConnection(self):
        # Wait for a connection
        print('Waiting for a connection')
        self.connection, client_address = self.sock.accept()
        print('Connection from', client_address)

    def receiveData(self):
        return receive(self.connection)

    def sendConfirm(self, mess_num=1, from_num=1, data_type=None, data=None):
        # Sends confirmation that the service is initialized
        send(self.connection, 'confirm', data, data_type, mess_num, from_num)

    def sendTextResult(self, text, mess_num=1, from_num=1):
        # Sends text result
        send(self.connection, 'result', text, 'text', mess_num, from_num)

    def sendImageResult(self, image, mess_num=1, from_num=1):
        # Sends image result
        send(self.connection, 'result', image, 'image', mess_num, from_num)

    def sendAudioResult(self, data, mess_num=1, from_num=1):
        # Sends audio result
        raise ValueError('Audio data sending NOT implemented yet!')

    def sendError(self, msg):
        # Sends error command with error message in 'msg'
        send(self.connection, 'error', msg, 'text', 1, 1)

    def closeConnection(self):
        self.connection.close()
        print('Closed last connection')


class Client:

    def __init__(self):
        pass

    def connectService(self, server, port=10000):
        # Connects to server:port
        self.sock = socket.create_connection((server, port))

    def initService(self, data=None, data_type=None, mess_num=1, from_num=1):
        # Initializes the service
        send(self.sock, 'init', data, data_type, mess_num, from_num)

    def stopService(self):
        # Sends "end" command for the service to close
        send(self.sock, 'end', None, None, 1, 1)

    def sendTextRequest(self, text, mess_num=1, from_num=1):
        # Sends text request
        send(self.sock, 'request', text, 'text', mess_num, from_num)

    def sendImageRequest(self, image, mess_num=1, from_num=1):
        # Sends image request
        send(self.sock, 'request', image, 'image', mess_num, from_num)

    def sendAudioRequest(self, data, mess_num=1, from_num=1):
        # Sends audio request
        raise ValueError('Audio data sending NOT implemented yet!')

    def receiveData(self):
        return receive(self.sock)

    def disconnectService(self):
        print('closing socket')
        self.sock.close()

