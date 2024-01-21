from gpiozero import TrafficLights
from time import sleep

lights_NS = TrafficLights(25, 8, 7)
lights_NSL = TrafficLights(14, 15, 18)

lights_EW = TrafficLights(25, 8, 7)
lights_EWL = TrafficLights(14, 15, 18)


############ NS ROADS ##############

def ns_green_on():
    sleep(4)
    lights_NS.red.off()
    lights_NS.green.on()

def ns_red_on():
    lights_NS.green.off()
    lights_NS.yellow.on()
    sleep(4)
    lights_NS.yellow.off()
    lights_NS.red.on()

def nsl_green_on():
    sleep(4)
    lights_NSL.red.off()
    lights_NSL.green.on()

def nsl_red_on():
    lights_NSL.green.off()
    lights_NSL.yellow.on()
    sleep(4)
    lights_NSL.yellow.off()
    lights_NSL.red.on()

####################################
    
############ EW ROADS ##############

def ew_green_on():
    sleep(4)
    lights_EW.red.off()
    lights_EW.green.on()

def ew_red_on():
    lights_EW.green.off()
    lights_EW.yellow.on()
    sleep(4)
    lights_EW.yellow.off()
    lights_EW.red.on()

def ewl_green_on():
    sleep(4)
    lights_EWL.red.off()
    lights_EWL.green.on()

def ewl_red_on():
    lights_EWL.green.off()
    lights_EWL.yellow.on()
    sleep(4)
    lights_EWL.yellow.off()
    lights_EWL.red.on()

####################################