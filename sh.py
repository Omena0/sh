from sys import argv
import socket
from threading import Thread
import subprocess as sp
from getpass import getpass
import os
import random as r
from time import sleep

print(argv)

if len(argv) != 4:
    exit('Invalid number of arguments. Must be 3.\nSyntax: sh [connect|serve] <ip> <port>')

ip = argv[2]
port = int(argv[3])

username = os.getlogin()

name = f'{username}@{ip}:{port}'

# CONFIGURABLE: AMMOUNT OF CHALLENGES TO ISSUE
challenges = 5
s = socket.socket()

client_sockets = set()

startSeed = 57629

timer = 1

def shash(text,seed):
    if seed == None:
        seed = startSeed
    seed = str(seed)
    if len(seed) > 9:
        seed = round(int(seed) / 10 * len(seed)-9)
    cmd = ['python', '-c', f'print(hash("{text}"))']
    p = sp.Popen(cmd, env={'PYTHONHASHSEED': seed})
    return p.communicate()[0]

def clientHandler(cs,addr):
    global out, timer
    msg = cs.recv(2048).decode()
    if msg != 'SH HANDSHAKE':
        cs.send('Wrong protocol! Please use SH'.encode())
        cs.close()
        return

    seed = shash(password,startSeed)
    for i in range(challenges):
        print(f'Challenge #{i}')
        challenge = str(r.randrange(0,4294967296))
        print(f'PASSWORD CHALLENGE|{challenge}|{name}')
        cs.send(f'PASSWORD CHALLENGE|{challenge}|{name}'.encode())
        correct = str(shash(challenge,seed))
        attempt = cs.recv(2048).decode()
        if attempt == correct:
            print('Correct!')
            continue
        print(f'Incorrect! {attempt} != {correct}')
        cs.close()
        return
    cs.send('SH HANDSHAKE END'.encode())
    
    cmd = []
    p = sp.Popen(args=cmd,shell=True,stdin=sp.PIPE,stdout=sp.PIPE)
    clientId = len(client_sockets)
    client_sockets.add(cs)
    while True:
        msg = cs.recv(2048)
        print(f'{msg=}')
        p.wait()
        out = p.stdout.read(1)
        print(f'{out=}')
        cs.send(out)
        cs.send('fuk'.encode())
        

if argv[1] == 'connect':
    s.connect((ip,port))
    password = getpass(f'Password for {name}:')
    s.send('SH HANDSHAKE'.encode())
    seed = shash(password,startSeed)
    i = 0
    while True:
        print(f'Challenge #{i}')
        msg = s.recv(2048).decode()
        if msg == 'SH HANDSHAKE END' or msg == '': break
        msg = msg.split('|')
        name = msg[2]
        if msg[0] != 'PASSWORD CHALLENGE':
            s.send(f'PROTOCOL FAILIURE')
            exit(f'PROTOCOL ERROR: {"".join(msg)} DOES NOT MATCH EXPECTED FORMAT')
        challenge = str(r.randrange(0,4294967296))
        attempt = str(shash(challenge,seed))
        s.send(f'{attempt}'.encode())
        i += 1
    
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
        Thread(target=clientHandler, args=(cs,addr)).start()
        print(f'[+] {addr}')


else:
    exit('Invalid mode\nSyntax: sh [connect|serve] <ip> <port>')
    
