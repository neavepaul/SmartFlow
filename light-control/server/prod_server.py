import socket
import pickle
from threading import Thread
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model

# Raspberry Pi's IP address and port
PI_IP = '192.168.29.155'
PI_PORT = 12345

# Load the pre-trained model
loaded_model = load_model('traffic_model.h5')

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
                client_index, data = pickle.loads(received_data)
                print(f"Received data from client {client_index}: {data}")
                # Store the received data in the dictionary
                received_data_dict[client_index] = data
            else:
                print("No data received from client")
                break

    except Exception as e:
        print(f"ERROR: {e}")
    finally:
        connection.close()

# Function to predict action based on combined data
def choose_action(combined_data):
    # Reshape the combined data for model input
    state = np.reshape(combined_data, [1, 8])
    # Predict the action using the loaded model
    return np.argmax(loaded_model.predict(state))

# Function to handle action prediction
def action_thread():
    try:
        while True:
            # Wait until all clients have sent their data
            if len(received_data_dict) == 4:
                # Combine the received data in the correct order
                combined_data = [received_data_dict[i] for i in range(1, 5)]
                print("Combined data for action:", combined_data)
                # Predict action based on combined data
                action = choose_action(combined_data)
                print("Action predicted:", action)
                # Reset the dictionary for the next iteration
                received_data_dict.clear()
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
