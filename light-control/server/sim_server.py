import socket
import pickle
from time import sleep
from gpiozero import TrafficLights
from gpiozero.pins.pigpio import PiGPIOFactory
import numpy as np
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # kill warning about tensorflow
import tensorflow as tf
from tensorflow.keras.models import load_model


factory_NS = PiGPIOFactory(host='192.168.29.56')
factory_SN = PiGPIOFactory(host='192.168.29.20')
factory_EW = PiGPIOFactory(host='192.168.29.109')
factory_WE = PiGPIOFactory(host='192.168.29.215')

# Every traffic signal will have this definition
lightsNS = TrafficLights(25, 8, 7, pin_factory=factory_NS)  # RYG
lightsNSL = TrafficLights(16, 20, 21, pin_factory=factory_NS)  # RYG
lightsSN = TrafficLights(25, 8, 7, pin_factory=factory_SN)  # RYG
lightsSNL = TrafficLights(16, 20, 21, pin_factory=factory_SN)  # RYG
lightsEW = TrafficLights(25, 8, 7, pin_factory=factory_EW)  # RYG
lightsEWL = TrafficLights(16, 20, 21, pin_factory=factory_EW)  # RYG
lightsWE = TrafficLights(25, 8, 7, pin_factory=factory_WE)  # RYG
lightsWEL = TrafficLights(16, 20, 21, pin_factory=factory_WE)  # RYG

lightsNS.red.on()
lightsNSL.red.on()
lightsSN.red.on()
lightsSNL.red.on()
lightsEW.red.on()
lightsEWL.red.on()
lightsWE.red.on()
lightsWEL.red.on()

NS_GREEN = [lightsNS, lightsSN]
NS_YELLOW = [lightsNS, lightsSN]
NSL_GREEN = [lightsNSL, lightsSNL]
NSL_YELLOW = [lightsNSL, lightsSNL]
EW_GREEN = [lightsEW, lightsWE]
EW_YELLOW = [lightsEW, lightsWE]
EWL_GREEN = [lightsEWL, lightsWEL]
EWL_YELLOW = [lightsEWL, lightsWEL]

# Raspberry Pi's IP address
PI_IP = '192.168.29.155'
PI_PORT = 12345

CLASS_TO_PHASE = {
    0: "NS_GREEN",
    1: "NSL_GREEN",
    2: "EW_GREEN",
    3: "EWL_GREEN"
}

loaded_model = load_model('traffic_model.h5')
old_action = 0  # Initialize with an invalid action

def choose_action(state):
    """
    Pick the best action known based on the current state of the env
    """
    state = np.reshape(state, [1, 8])
    return np.argmax(loaded_model.predict(state))


def set_y2r(curr_phase):
    curr_phase[0].green.off()
    curr_phase[1].green.off()
    curr_phase[0].yellow.on()
    curr_phase[1].yellow.on()
    sleep(4)
    curr_phase[0].yellow.off()
    curr_phase[1].yellow.off()
    curr_phase[0].red.on()
    curr_phase[1].red.on()


def set_green(phase):
    phase[0].red.off()
    phase[1].red.off()
    phase[0].green.on()
    phase[1].green.on()


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as pi_socket:
    pi_socket.bind((PI_IP, PI_PORT))
    pi_socket.listen(1)

    try:
        print("Waiting for connection from PC...")
        connection, address = pi_socket.accept()
        
        with connection:
            print(f"Connected to {address}")
            
            while True:
                # Receive state from PC [TEMPORARY... WILL HAVE TO COMPILE STATES LATER FROM DIFF CLIENTS]
                received_data = connection.recv(1024)
                if not received_data:
                    # Break the loop if no data is received (server closed the connection)
                    break

                state = pickle.loads(received_data)
                
                # Make predictions
                action = choose_action(state)
                

                # Update lights based on the predicted action
                if action != old_action:
                    # Turn off green lights from the previous phase
                    if old_action == 0:
                        # Turn off lights for NS_GREEN phase
                        phase = CLASS_TO_PHASE[old_action]
                        old_phase = globals()[phase]
                        set_y2r(old_phase)
                    elif old_action == 1:
                        # Turn off lights for NSL_GREEN phase
                        phase = CLASS_TO_PHASE[old_action]
                        old_phase = globals()[phase]
                        set_y2r(old_phase)
                    elif old_action == 2:
                        # Turn off lights for EW_GREEN phase
                        phase = CLASS_TO_PHASE[old_action]
                        old_phase = globals()[phase]
                        set_y2r(old_phase)
                    elif old_action == 3:
                        # Turn off lights for EWL_GREEN phase
                        phase = CLASS_TO_PHASE[old_action]
                        old_phase = globals()[phase]
                        set_y2r(old_phase)

                    # Set lights for the new predicted action
                    if action == 0:
                        # Set lights for NS_GREEN phase
                        phase = CLASS_TO_PHASE[action]
                        new_phase = globals()[phase]
                        set_green(new_phase)
                    elif action == 1:
                        # Set lights for NSL_GREEN phase
                        phase = CLASS_TO_PHASE[action]
                        new_phase = globals()[phase]
                        set_green(new_phase)
                    elif action == 2:
                        # Set lights for EW_GREEN phase
                        phase = CLASS_TO_PHASE[action]
                        new_phase = globals()[phase]
                        set_green(new_phase)
                    elif action == 3:
                        # Set lights for EWL_GREEN phase
                        phase = CLASS_TO_PHASE[action]
                        new_phase = globals()[phase]
                        set_green(new_phase)

                    # Update old action
                    old_action = action

                # Send response back to the server
                serialised_result=pickle.dumps(action)
                connection.sendall(serialised_result)

                print(f"Action {action} performed")

    except Exception as e:
        print(f"ERROR: {e}")
    except KeyboardInterrupt:
        print("Server interrupted.")
    finally:
        pi_socket.close()
