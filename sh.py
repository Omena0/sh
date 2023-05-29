from sys import argv
import socket
from threading import Thread
import subprocess
from getpass import getpass
import os
import random as r

if len(argv) != 3:
    exit('Invalid number of arguments. Must be 3.\nSyntax: sh [connect|serve] <ip> <port>')

ip = argv[2]
port = int(argv[3])

username = os.getlogin()

name = f'{username}@{ip}:{port}'

# CONFIGURABLE: AMMOUNT OF CHALLENGES TO ISSUE
challenges = 5

s = socket.socket()

client_sockets = set()

def clientHandler(cs,addr):
    msg = cs.recv(2048).decode()
    if msg != 'SH HANDSHAKE':
        cs.send('Wrong protocol! Please use SH'.encode())
        client_sockets.remove(cs)
        cs.close()
        return

    seed = hash(password)
    os.environ['PYTHONHASHSEED'] = f'{seed}'
    for i in range(challenges):
        challenge = str(r.randrange(0,4294967296))
        cs.send(f'PASSWORD CHALLENGE|{challenge}|{name}')
        correct = str(hash(challenge))
        attempt = cs.recv(2048).decode()
        if attempt != correct:
            client_sockets.remove(cs)
            cs.close()
            return
    
    p = subprocess.Popen()
    clientId = len(client_sockets)
    client_sockets.add(cs)
    while True:
        msg = cs.recv(2048)
        stdout, stderr = p.communicate(msg)
        print(stderr)
        cs.send(f'{stdout}'.encode())
        

if argv[1] == 'connect':
    s.connect((ip,port))
    s.send('SH HANDSHAKE'.encode())
    while True:
        msg = s.recv(2048).decode()
        if msg == 'SH HANDSHAKE END': break
        msg = msg.split('|')
        name = msg[2]
        if msg[0] != 'PASSWORD CHALLENGE':
            s.send(f'PROTOCOL FAILIURE')
            exit(f'PROTOCOL ERROR: {"".join(msg)} DOES NOT MATCH EXPECTED FORMAT')
        password = getpass(f'Password for {name}:')
        seed = hash(password)
        os.environ['PYTHONHASHSEED'] = f'{seed}'
        challenge = str(r.randrange(0,4294967296))
        attempt = str(hash(challenge))
        s.send(f'{attempt}'.encode())
    
    while True:
        cmd = input(f'$ {name} > ')
        s.send(cmd.encode())
        msg = s.recv(2048).decode()
        print(msg)
    
    
    
    

elif argv[1] == 'serve':
    password = getpass(f'Create password for {name}: ')
    if password != getpass(f'Confirm password for {name}: '):
        exit('Passwords do not match.')
    s.bind((ip,port))
    s.listen(5)
    
    while True:
        cs, addr = s.accept()
        Thread
        print(f'[+] {addr}')


else:
    exit('Invalid mode\nSyntax: sh [connect|serve] <ip> <port>')
    
