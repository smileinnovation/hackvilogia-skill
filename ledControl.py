import logging.handlers
import signal
import time
from matrix import LedControl

_logger = logging.getLogger('LedControl')
_logger.setLevel(logging.DEBUG)
streamHandler = logging.StreamHandler()
_logger.addHandler(streamHandler)

def stopHandler(signum, frame):
    onStop()

def onStop():
    global RUNNING
    RUNNING = False

def main():
    signal.signal(signal.SIGINT, stopHandler)
    signal.signal(signal.SIGTERM, stopHandler)
    led_control = LedControl('localhost', 1883, _logger)

    try:
        _logger.info('Starting LedControl')
        led_control.start()
        while RUNNING:
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        _logger.info('Shutting down Snips Led Control')
        led_control.stop()


if __name__ == "__main__":
    RUNNING = True
    main()