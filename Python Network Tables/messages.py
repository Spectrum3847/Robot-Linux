#!/usr/bin/env python

from constants import *
from utils import SequenceNumber

def get_type(value):
    "Get the type of a value."
    if isinstance(value, int):
        return TYPE_INTEGER
    if isinstance(value, str):
        return TYPE_STRING

def encode_int(value, size):
    "Encodes an int in the big endian format."
    return bytearray((value >> (8*(size-i-1))) & 0xff
                     for i in range(size))

def decode_int(value):
    "Defcodes an int in the big endian format."
    return sum((value[i] << (8*(len(value)-i-1)))
             for i in range(len(value)))

def encode_string(value):
    "Encodes a string. This cheats and uses straight utf-8."
    string = bytearray(value.encode())
    return encode_int(len(string), 2) + string

def decode_string(sock):
    "Decodes a string. This cheats and uses straight utf-8."
    length = decode_int(sock.recv(2))
    return str(sock.recv(length), "utf-8")

def encode(value):
    "Encode a value of any type."
    if get_type(value) == TYPE_INTEGER:
        return encode_int(value, 4)
    elif get_type(value) == TYPE_STRING:
        return encode_string(value)

def decode(typeof, sock):
    "Decode a value of the given type."
    if typeof == TYPE_INTEGER:
        return decode_int(sock.recv(4))
    elif typeof == TYPE_STRING:
        return decode_string(sock)


def create_messages(table, manager):
    "Create a lookep table of messages to handle."
    global MESSAGES
    MESSAGES = {
        # NOTE: No keep-alive message since the implementation is trivial.
        CLIENT_HELLO: ClientHelloMessage(table, manager),
        PROTOCOL_UNSUPPORTED: ProtocolUnsupportedMessage(table, manager),
        ENTRY_ASSIGNMENT: EntryAssignmentMessage(table, manager),
        ENTRY_UPDATE: EntryUpdateMessage(table, manager),
        BEGIN_TRANSACTION: BeginTransaction(table, manager),
        END_TRANSACTION: EndTransaction(table, manager)
        }

class Message:
    "The super class of all messages"

    def __init__(self, table, manager):
        self.table = table
        self.manager = manager

class ClientHelloMessage(Message):
    "A message for handling client joins"

    def encode(self):
        return bytearray((CLIENT_HELLO,)) +\
            encode_int(PROTOCOL_VERSION, 2)

    def decode(self, sock):
        version = decode_int(sock.recv(2))
        print("Client connected with version: {}.".format(version))
        if version != PROTOCOL_VERSION:
            print("Disconnecting from client.")
            sock.sendall(MESSAGES[PROTOCOL_UNSUPPORTED].encode())
            self.manager.disconnect(sock)
        else:
            print("Sending all table values.")
            sock.sendall(MESSAGES[BEGIN_TRANSACTION].encode())
            self.table.lock()
            for entry in self.table.entries.values():
                print("\t{}: {}".format(entry.name, entry.value))
                sock.sendall(MESSAGES[ENTRY_ASSIGNMENT].encode(entry))
            self.table.release()
            sock.sendall(MESSAGES[END_TRANSACTION].encode())

class ProtocolUnsupportedMessage(Message):
    "A message for alerting clients you don't support their revision."

    def encode(self):
        return bytearray((PROTOCOL_UNSUPPORTED,)) +\
            encode_int(PROTOCOL_VERSION, 2)

    def decode(self, sock):
        version = decode_int(sock.recv(2))
        print("Server is version {} and does not support our protocol revision: {}.".format(
                version, PROTOCOL_VERSION))
        self.manager.disconnect(sock)

class EntryAssignmentMessage(Message):
    "A message for assigning entries."

    def encode(self, entry):
        print("Assigning entry: {}={}".format(entry.name, entry.value))
        return bytearray((ENTRY_ASSIGNMENT,)) +\
            encode_string(entry.name) +\
            encode_int(entry.type, 1) +\
            encode_int(entry.id, 2) +\
            encode_int(entry.sequence_number.val, 2) +\
            encode(entry.value)

    def decode(self, sock):
        name = decode_string(sock)
        typeof = decode_int(sock.recv(1))
        idVal = decode_int(sock.recv(2))
        sequence_number = decode_int(sock.recv(2))
        value = decode(typeof, sock)
        
        return (name, typeof, idVal, sequence_number, value)

class EntryUpdateMessage(Message):
    "A message for updating the value of entries."

    def encode(self, entry):
        return bytearray((ENTRY_UPDATE,)) +\
            encode_int(entry.id, 2) +\
            encode_int(entry.sequence_number.val, 2) +\
            encode(entry.value)

    def decode(self, sock):
        idVal = decode_int(sock.recv(2))
        sequence_number = SequenceNumber(decode_int(sock.recv(2)))
        value = decode(self.table.ids[idVal].type, sock)
        
        return (idVal, sequence_number, value)


class BeginTransaction(Message):
    "A message for beginning a transaction."

    def encode(self):
        return bytearray((BEGIN_TRANSACTION,))

    def decode(self, sock):
        self.table.lock()
        thread = self.manager.get_read_thread(sock)
        thread.begin_transaction()
        self.table.release()

class EndTransaction(Message):
    "A message for ending a transaction."

    def encode(self):
        return bytearray((END_TRANSACTION,))

    def decode(self, sock):
        self.table.lock()
        thread = self.manager.get_read_thread(sock)
        thread.end_transaction()
        self.table.release()
