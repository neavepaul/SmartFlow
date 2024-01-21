import socket
import pickle
import numpy as np
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # kill warning about tensorflow
import tensorflow as tf
from tensorflow.keras.models import load_model

# Raspberry Pi's IP address
PI_IP = '192.168.137.128' #hotspot
# PI_IP = '192.168.43.76' #phone
PI_PORT = 12345

loaded_model = load_model('traffic_model.h5')

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

                # Perform prediction (replace this with your model prediction logic)
                action = choose_action(state)

                # Serialize and send the result back to PC
                serialized_result = pickle.dumps(action)
                connection.sendall(serialized_result)

                print(f"Action {action} sent")

    except Exception as e:
        print(f"ERROR: {e}")
    except KeyboardInterrupt:
        print("Server interrupted.")
    finally:
        pi_socket.close()
