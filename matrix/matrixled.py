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
        self.leds = [None] * 18

    def __show(self):
        config = driver_pb2.DriverConfig()
        config.image.led.extend(self.leds)
        self.socket.send(config.SerializeToString())

    def connect(self):
        self.socket.connect(self.address)

    def disconnect(self):
        self.socket.disconnect(self.address)

    def solid(self, color=_dark):
        """ Light all leds in single colour """
        for led in range(LED_COUNT):
            self.leds[led] = color
        self.__show()

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
            self.leds = lit_leds + base_leds
            self.__show()
            time.sleep(delay)

    def wave(self, color, delay=0.01):
        count = 0
        while count < LED_COUNT:
            for i in range(LED_COUNT):
                led = (count + i) % LED_COUNT
                coef = (1+math.cos(math.pi*(led/9)))/2
                self.leds[i] = get_led(red=int(color.red*coef), green=int(color.green*coef), blue=int(color.blue*coef), white=int(color.white*coef))
            self.__show()
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
            self.leds = [current_color for led in range(LED_COUNT)]
            self.__show()
            red += red_incr
            green += green_incr
            blue += blue_incr
            white += white_incr
            time.sleep(delay)

    def shutdown(self, delay=0.01, steps=100):
        max_color = 0
        for ledValue in self.leds:
            m = max(ledValue.red, ledValue.green, ledValue.blue, ledValue.white)
            max_color = max(max_color, m)
        incr = max_color / steps
        for i in range(steps):
            for index, ledValue in enumerate(self.leds):
                red = int(ledValue.red - incr)
                red = red if red > 0 else 0
                green = int(ledValue.green - incr)
                green = green if green > 0 else 0
                blue = int(ledValue.blue - incr)
                blue = blue if blue > 0 else 0
                white = int(ledValue.white - incr)
                white = white if white > 0 else 0
                new_color = get_led(red=red, green=green, blue=blue, white=white)
                self.leds[index] = new_color
            self.__show()
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
        self.leds = [self._dark for led in range(LED_COUNT)]
        self.leds[position] = color
        self.__show()


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

























