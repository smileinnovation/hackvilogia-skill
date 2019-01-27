import math
import time
import zmq
import sys
import threading
from matrix_io.proto.malos.v1 import driver_pb2
from matrix_io.proto.malos.v1 import io_pb2

# MATRIX Everloop LED array port
PORT = 20021
LED_COUNT = 18
current_led_index = 0


def get_led(**args):
    ledValue = io_pb2.LedValue()
    ledValue.red = args.get('red', 0)
    ledValue.green = args.get('green', 0)
    ledValue.blue = args.get('blue', 0)
    ledValue.white = args.get('white', 0)
    return ledValue


colors = {
    'blank' 	: get_led(red=0, green=0, blue=0, white=0),
    'blue'		: get_led(red=0, green=0, blue=64, white=0),
    'red'		: get_led(red=64, green=0, blue=0, white=0),
    'green'		: get_led(red=0, green=64, blue=0, white=0),
    'yellow'	: get_led(red=64, green=64, blue=0, white=0),
    'white'		: get_led(red=0, green=0, blue=0, white=0),
}


class MatrixLed:
    _dark = get_led()

    def __init__(self, matrix_ip='127.0.0.1'):
        context = zmq.Context()
        self.address = 'tcp://{0}:{1}'.format(matrix_ip, PORT)
        self.socket = context.socket(zmq.PUSH)

    def __show(self, leds):
        config = driver_pb2.DriverConfig()
        config.image.led.extend(leds)
        self.socket.send(config.SerializeToString())

    def connect(self):
        self.socket.connect(self.address)

    def disconnect(self):
        self.socket.disconnect(self.address)

    def solid(self, color=_dark):
        """ Light all leds in single colour """
        leds = []
        for led in range(LED_COUNT):
            leds.append(color)
        self.__show(leds)

    def loading_bar(self, color, base=_dark, delay=0.01):
        """ Light one led at a time until all leds are lit """
        if color == base:
            self.disconnect()
            sys.exit('Color and base cannot be identical')
        count = 0
        while count < LED_COUNT:
            count += 1
            lit_leds = [color for led in range(count)]
            base_leds = [base for led in range(LED_COUNT - count)]
            leds = lit_leds + base_leds
            self.__show(leds)
            time.sleep(delay)

    def wave(self, color, delay=0.01):
        leds = [None] * 18
        count = 0
        while count < LED_COUNT:
            for i in range(LED_COUNT):
                led = (count + i) % LED_COUNT
                coef = (1+math.cos(math.pi*(led/9)))/2
                leds[i] = get_led(red=int(color.red*coef), green=int(color.green*coef), blue=int(color.blue*coef), white=int(color.white*coef))
            self.__show(leds)
            count += 1
            time.sleep(delay)

    def fadeIn(self, color, delay=0.01, steps=100):
        red_incr = color.red / steps
        green_incr = color.green / steps
        blue_incr = color.blue / steps
        white_incr = color.white / steps
        red = blue = green = white = 0
        for i in range(steps):
            current_color = get_led(red=int(red), green=int(green), blue=int(blue), white=int(white))
            leds = [current_color for led in range(LED_COUNT)]
            self.__show(leds)
            red += red_incr
            green += green_incr
            blue += blue_incr
            white += white_incr
            time.sleep(delay)

    def standby(self, color, delay=0.5):
        global current_led_index
        self.single(color, current_led_index)
        current_led_index = (current_led_index + 1) % LED_COUNT
        time.sleep(delay)

    def single(self, color, position=0):
        """ Light a single led """
        if position < 0 or position >= LED_COUNT:
            self.disconnect()
            sys.exit('Position must be a number between 0 and {}'.format(LED_COUNT-1))
        leds = [self._dark for led in range(LED_COUNT)]
        leds[position] = color
        self.__show(leds)


class LedRunner:
    def __init__(self):
        self.thread = None
        self.running = False

    def __repeat(self, func, args):
        while self.running:
            func(*args)

    def start(self, func, *args):
        self.stop()
        self.running = True
        self.thread = threading.Thread(target=self.__repeat, args=(func, args))
        self.thread.start()

    def stop(self):
        if self.thread is not None and self.thread.isAlive():
            self.running = False
            self.thread.join()
            global current_led_index
            current_led_index = 0

    def once(self, func, *args):
        self.stop()
        func(*args)

























