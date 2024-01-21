import socket
import pickle
import numpy as np
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # kill warning about tensorflow
import tensorflow as tf
from tensorflow.keras.models import load_model
import json

# Raspberry Pi's IP address
PI_IP = '192.168.137.128' #hotspot
# PI_IP = '192.168.43.76' #phone
PI_PORT = 12345

loaded_model = load_model('traffic_model.h5')

stored_value = {'NS_GREEN': 0, 'NS_YELLOW': 0, 'NSL_GREEN': 0, 'NSL_YELLOW': 0,
                'EW_GREEN': 0, 'EW_YELLOW': 0, 'EWL_GREEN': 0, 'EWL_YELLOW': 0, 'KILL': 0}


CLASS_TO_PHASE = {
    0: "NS_GREEN",
    1: "NSL_GREEN",
    2: "EW_GREEN",
    3: "EWL_GREEN"
}

# Write to JSON file
STATE_FILE = 'state.json'
def write_state(state):
    with open(STATE_FILE, 'w') as file:
        json.dump(state, file)


def choose_action(state):
    """
    Pick the best action known based on the current state of the env
    """
    state = np.reshape(state, [1, 8])
    return np.argmax(loaded_model.predict(state))

# Create a socket on Raspberry Pi
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as pi_socket:
    pi_socket.bind((PI_IP, PI_PORT))
    pi_socket.listen(1)

    try:
        print("Waiting for connection from PC...")
        connection, address = pi_socket.accept()

        with connection:
            print(f"Connected to {address}")

            while True:
                # Receive array from PC
                received_data = connection.recv(1024)
                if not received_data:
                    break  # Break the loop if no data is received (client closed the connection)

                state = pickle.loads(received_data)

                # Turn off the current green phases and turn on the corresponding red phases
                for key in stored_value.keys():
                    if key.endswith('_GREEN'):
                        stored_value[key] = 0
                        corresponding_red_key = key.replace('_GREEN', '_RED')
                        stored_value[corresponding_red_key] = 1


                # Perform prediction (replace this with your model prediction logic)
                action = choose_action(state)


                # Update the corresponding phases based on the model's prediction
                phases_to_turn_green = CLASS_TO_PHASE.get(action)
                for phase in phases_to_turn_green:
                    stored_value[phase] = 1


                # serialized_result = pickle.dumps(action)
                            
                write_state(stored_value)
                response= "recvd array"
                connection.sendall(response)

                print(f"Action {action} sent")

    except Exception as e:
        print(f"ERROR: {e}")
    except KeyboardInterrupt:
        print("Server interrupted.")
    finally:
        pi_socket.close()
