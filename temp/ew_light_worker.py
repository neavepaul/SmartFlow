import socket
import pickle
from time import sleep
from control import ew_green_on, ew_red_on, ewl_green_on, ewl_red_on

HEADERSIZE = 10
client = {'NS_GREEN': 0, 'NS_RED': 0, 'NSL_GREEN': 0, 'NSL_RED': 0,
          'EW_GREEN': 0, 'EW_RED': 0, 'EWL_GREEN': 0, 'EWL_RED': 0}

old_state = {'NS_GREEN': 0, 'NS_RED': 0, 'NSL_GREEN': 0, 'NSL_RED': 0,
          'EW_GREEN': 0, 'EW_RED': 0, 'EWL_GREEN': 0, 'EWL_RED': 0}

host = 'server_IP'
port = 0 #PORT

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, port))


def update_lights(client):
    """UPDATE THE PHYSICAL STATES OF TRAFFIC LIGHTS WITH CHANGES"""
    # Check for differences and update only the lights that changed
    if client.get('EW_GREEN') != old_state['EW_GREEN']:
        if client.get('EW_GREEN') == 1:
            ew_green_on() 
    
    if client.get('EW_RED') != old_state['EW_RED']:
        if client.get('EW_RED') == 1:
            ew_red_on() 
    
    if client.get('EWL_GREEN') != old_state['EWL_GREEN']:
        if client.get('EWL_GREEN') == 1:
            ewl_green_on() 
    
    if client.get('EWL_RED') != old_state['EWL_RED']:
        if client.get('EWL_RED') == 1:
            ewl_red_on() 
    else:
        pass

        
while True:
    command = "UPDATE"
    msg = pickle.dumps(command, -1)
    msg = bytes(f"{len(msg):<{HEADERSIZE}}", 'utf-8') + msg
    s.send(msg)

    full_msg = b''
    new_msg = True
    msg = s.recv(1024)

    if new_msg:
        msglen = int(msg[:HEADERSIZE])
        new_msg = False

    full_msg += msg

    if len(full_msg) - HEADERSIZE == msglen:
        incoming = pickle.loads(full_msg[HEADERSIZE:])
        if type(incoming) is dict:
            client.update(incoming)
            print("new client")
            print(client)
            update_lights(client)

        else:
            print("Data Format Unrecognised.")

        new_msg = True
        full_msg = b''
        sleep(1)

    if client.get('KILL') == 1:
        s.close()
        break
