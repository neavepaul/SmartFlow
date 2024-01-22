from gpiozero import TrafficLights
from time import sleep

# every traffic signal will have this definition
lightsNS = TrafficLights(25, 8, 7) #RYG
lightsNSL = TrafficLights(25, 8, 7) #RYG
lightsSN = TrafficLights(25, 8, 7) #RYG
lightsSNL = TrafficLights(25, 8, 7) #RYG
lightsEW = TrafficLights(25, 8, 7) #RYG
lightsEWL = TrafficLights(25, 8, 7) #RYG
lightsWE = TrafficLights(25, 8, 7) #RYG
lightsWEL = TrafficLights(25, 8, 7) #RYG


PHASE_NS_GREEN = [lightsNS]
# PHASE_NS_GREEN = [lightsNS,lightSN]
PHASE_NS_YELLOW = [lightsNS]
# PHASE_NS_YELLOW = [lightsNS, lightsSN]
PHASE_NSL_GREEN = [lightsNSL, lightsSNL]
PHASE_NSL_YELLOW = [lightsNSL, lightsSNL]
PHASE_EW_GREEN = [lightsEW, lightsWE]
PHASE_EW_YELLOW = [lightsEW, lightsWE]
PHASE_EWL_GREEN = [lightsEWL, lightsWEL]
PHASE_EWL_YELLOW = [lightsEWL, lightsWEL]

old = [] #phase
# make a list to keep track of all the phases in order to set the green when all are red only

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

def green(phase):
    phase[0].red.off()
    phase[1].red.off()
    phase[0].red.off()
    phase[1].red.off()
    

set_y2r(old)
set_green(new)
