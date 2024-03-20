from gpiozero import TrafficLights
from gpiozero.pins.pigpio import PiGPIOFactory
from time import sleep

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

lights = [lightsNS, lightsNSL, lightsSN, lightsSNL, lightsEW, lightsEWL, lightsWE, lightsWEL]
phases = [[lightsNS, lightsSN], [lightsNSL, lightsSNL], [lightsEW, lightsWE], [lightsEWL, lightsWEL]]

try:
    while True:
        for phase in phases:
            set_green(phase)
            sleep(5)  # Green phase duration
            set_y2r(phase)
            sleep(4)  # Yellow phase duration
except KeyboardInterrupt:
    print("Testing stopped by the user.")
