from threading import Thread
import time

from loguru import logger


class HeartbeatService(Thread):
    def __init__(self, node_heartbeat_callback, interval):
        """ Create HeartbeatService object
        :param node_heartbeat_callback: callback to call on every beat
        :param interval: space between beats
        """
        super().__init__(daemon=True, name="Heartbeat service")
        self.node_heartbeat_callback = node_heartbeat_callback
        self.interval = interval
        self._run = True

    def run(self) -> None:
        logger.debug("Heartbeat service started")
        while self._run:
            self.node_heartbeat_callback()
            time.sleep(self.interval)

    def stop(self):
        self._run = False
