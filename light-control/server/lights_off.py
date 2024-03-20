from gpiozero import TrafficLights
from gpiozero.pins.pigpio import PiGPIOFactory



factory_NS = PiGPIOFactory(host='192.168.0.2')
factory_SN = PiGPIOFactory(host='192.168.0.3')
factory_EW = PiGPIOFactory(host='192.168.0.4')
factory_WE = PiGPIOFactory(host='192.168.0.5')

# Every traffic signal will have this definition
lightsNS = TrafficLights(25, 8, 7, pin_factory=factory_NS)  # RYG
lightsNSL = TrafficLights(16, 20, 21, pin_factory=factory_NS)  # RYG
lightsSN = TrafficLights(25, 8, 7, pin_factory=factory_SN)  # RYG
lightsSNL = TrafficLights(16, 20, 21, pin_factory=factory_SN)  # RYG
lightsEW = TrafficLights(25, 8, 7, pin_factory=factory_EW)  # RYG
lightsEWL = TrafficLights(16, 20, 21, pin_factory=factory_EW)  # RYG
lightsWE = TrafficLights(25, 8, 7, pin_factory=factory_WE)  # RYG
lightsWEL = TrafficLights(16, 20, 21, pin_factory=factory_WE)  # RYG

lightsNS.red.off()
lightsNSL.red.off()
lightsSN.red.off()
lightsSNL.red.off()
lightsEW.red.off()
lightsEWL.red.off()
lightsWE.red.off()
lightsWEL.red.off()