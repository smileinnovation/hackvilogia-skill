# -*- coding: utf-8 -*-
import logging.handlers
import signal
import time
from matrix import LedControl

formatter = logging.Formatter('%(asctime)s [%(threadName)s] - [%(levelname)s] - %(message)s')

_logger = logging.getLogger('LedControl')
_logger.setLevel(logging.DEBUG)
streamHandler = logging.StreamHandler()
streamHandler.setFormatter(formatter)
_logger.addHandler(streamHandler)


def stopHandler(signum, frame):
    onStop()


def onStop():
    global RUNNING
    RUNNING = False


def main():
    signal.signal(signal.SIGINT, stopHandler)
    signal.signal(signal.SIGTERM, stopHandler)
    led_control = None
    try:
        _logger.info('Starting LedControl')
        led_control = LedControl('localhost', 1883)
        led_control.start()
        while RUNNING:
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        _logger.info('Shutting down LedControl')
        if led_control is not None:
            led_control.stop()


if __name__ == "__main__":
    RUNNING = True
    main()