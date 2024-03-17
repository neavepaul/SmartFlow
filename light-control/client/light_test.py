from gpiozero import TrafficLights
from time import sleep

light1 = TrafficLights(25, 8, 7)  # RYG
light2 = TrafficLights(16, 20, 21)  # RYG

light1.red.on()
light2.red.on()
sleep(5)
light1.red.off()
light1.yellow.on()
light2.red.off()
light2.yellow.on()
sleep(5)
light1.yellow.off()
light1.green.on()
light2.yellow.off()
light2.green.on()
sleep(5)
light1.green.off()
light2.green.off()
