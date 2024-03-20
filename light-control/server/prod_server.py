import socket
import pickle
from threading import Thread
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
from time import sleep
from gpiozero import TrafficLights
from gpiozero.pins.pigpio import PiGPIOFactory
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # kill warning about tensorflow


factory_WE = PiGPIOFactory(host='192.168.0.2')
factory_NS = PiGPIOFactory(host='192.168.0.3')
factory_EW = PiGPIOFactory(host='192.168.0.4')
factory_SN = PiGPIOFactory(host='192.168.0.5')

# Every traffic signal will have this definition
lightsNS = TrafficLights(25, 8, 7, pin_factory=factory_NS)  # RYG
lightsNSL = TrafficLights(16, 20, 21, pin_factory=factory_NS)  # RYG
lightsSN = TrafficLights(25, 8, 7, pin_factory=factory_SN)  # RYG
lightsSNL = TrafficLights(16, 20, 21, pin_factory=factory_SN)  # RYG
lightsEW = TrafficLights(25, 8, 7, pin_factory=factory_EW)  # RYG
lightsEWL = TrafficLights(16, 20, 21, pin_factory=factory_EW)  # RYG
lightsWE = TrafficLights(25, 8, 7, pin_factory=factory_WE)  # RYG
lightsWEL = TrafficLights(16, 20, 21, pin_factory=factory_WE)  # RYG

NS_GREEN = [lightsNS, lightsSN]
NS_YELLOW = [lightsNS, lightsSN]
NSL_GREEN = [lightsNSL, lightsSNL]
NSL_YELLOW = [lightsNSL, lightsSNL]
EW_GREEN = [lightsEW, lightsWE]
EW_YELLOW = [lightsEW, lightsWE]
EWL_GREEN = [lightsEWL, lightsWEL]
EWL_YELLOW = [lightsEWL, lightsWEL]


# Raspberry Pi's IP address
PI_IP = '192.168.0.69'
PI_PORT = 12345

CLASS_TO_PHASE = {
    0: "NS_GREEN",
    1: "NSL_GREEN",
    2: "EW_GREEN",
    3: "EWL_GREEN"
}

loaded_model = load_model('traffic_model.h5')


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


# Initialize the server socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((PI_IP, PI_PORT))
server_socket.listen(4)  # Allow up to 4 clients to connect

print("Server is running...")

# Initialize a dictionary to store received data
received_data_dict = {}

# Function to handle client connection
def handle_client(connection, address):
    try:
        while True:
            # Receive data from the client
            received_data = connection.recv(1024)
            if received_data:
                # (1, [3.4, 6.7]) == (index, times_list)
                client_index, data = pickle.loads(received_data)
                print(f"Received data from client {client_index}: {data}")
                # Store the received data in the dictionary
                received_data_dict[client_index] = data

                # 1 = w to e 
                # 2 = n to s
                # 3 = e to w
                # 4 = s to n

            else:
                print("No data received from client")
                break

    except Exception as e:
        print(f"ERROR: {e}")
    finally:
        connection.close()

# Function to handle action prediction
def action_thread():
    old_action = 0  # Initialize with an invalid action
    try:
        while True:
            # Wait until all clients have sent their data
            if len(received_data_dict) == 4:
                # Combine the received data in the correct order
                combined_data = [received_data_dict[i] for i in range(1, 5)]
                print("Combined data for action:", combined_data)
                # Predict action based on combined data
                action = choose_action(combined_data)
                # Reset the dictionary for the next iteration
                received_data_dict.clear()

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

                print(f"Action {action} performed")

    except KeyboardInterrupt:
        print("Action thread interrupted.")

# Start the action prediction thread
action_thread = Thread(target=action_thread)
action_thread.start()

try:
    while True:
        # Accept incoming connections
        connection, address = server_socket.accept()
        print(f"Connected to client at {address}")

        # Start a new thread to handle the client connection
        client_thread = Thread(target=handle_client, args=(connection, address))
        client_thread.start()

except KeyboardInterrupt:
    print("Server interrupted.")
finally:
    server_socket.close()
