from sys import argv, exit as sys_exit
import socket
from threading import Thread
import subprocess as sp
from getpass import getpass
import os
import random as r
from time import sleep

def exit(msg):
    print(msg)
    sys_exit()

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
    try:
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

        clientId = len(client_sockets)
        client_sockets.add(cs)
        while True:
            try:
                msg = cs.recv(2048).decode()
                print(f'{msg=}')
                out = sp.check_output(msg,shell=True,text=True)
                if out == '': a = 'None'
                if out == 'None': out = '\\None'
                if out == '\n': out = 'None'
                print(f'{out=}')
                cs.send(out.encode())
            except Exception as e:
                cs.send(f'{e}\n'.encode())
    except:
        client_sockets.remove(cs)
        cs.close()
        sys_exit()
        

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
        if cmd == '': continue
        s.send(cmd.encode())
        msg = s.recv(2048).decode()
        if msg == 'None': msg = ''
        if msg == '\\None': msg = 'None'
        msg = msg.replace('Ä','─').replace('Ã','├').replace('³','│').replace('À','└').replace('À','└')\
            .replace('Ž','Ä').replace('„','ä').replace('™','Ö').replace('”','ö')
        print(msg,end='')
    
    
    
    

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
    
