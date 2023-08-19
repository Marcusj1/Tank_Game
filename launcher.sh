#!/bin/sh
# launcher.sh

cd /
cd /home/pi/Desktop/Tank_Game
sudo git reset --hard
sudo git pull
sudo python3 imu_stream.py
cd /

