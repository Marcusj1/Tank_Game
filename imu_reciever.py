import socket
import time

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tank_ip = "192.168.1.2"
port = 5555
addr = (tank_ip, port)

try:
    client.connect(addr)
    print("connection successful")

except:
    print("connection failed")
    quit()

while True:
    time.sleep(0.001)
    print(client.recv(2048).decode())
