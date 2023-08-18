import socket
import time

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tank_ip = "192.168.1.2"
port = 5555
addr = (tank_ip, port)


def data_unwrapper(received_string):
    print("Received: ", received_string)
    processed_string = received_string
    while len(processed_string) > 1:
        name_length = processed_string.find(":")
        name = processed_string[1:name_length]
        processed_string = processed_string[name_length:]
        value_length = processed_string.find("]")-1
        value = processed_string[:value_length]
        processed_string = processed_string[processed_string]

        print(name, value)


try:
    client.connect(addr)
    print("connection successful")

except:
    print("connection failed")
    quit()

while True:
    time.sleep(0.001)
    data = (client.recv(2048).decode())
    data_unwrapper(data)
