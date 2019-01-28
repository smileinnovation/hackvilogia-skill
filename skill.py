# -*- coding: utf-8 -*-
import logging.handlers
import signal
import time
from hackVilogiaSkill import HackVilogiaSkill

formatter = logging.Formatter('%(asctime)s [%(threadName)s] - [%(levelname)s] - %(message)s')

_logger = logging.getLogger('HackVilogiaSkill')
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
    skill = None
    try:
        _logger.info('Starting HackVilogiaSkill')
        skill = HackVilogiaSkill('localhost', 1883)
        skill.start()
        while RUNNING:
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        _logger.info('Shutting down HackVilogiaSkill')
        if skill is not None:
            skill.stop()


if __name__ == "__main__":
    RUNNING = True
    main()