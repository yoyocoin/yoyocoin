from threading import Thread
import time

from loguru import logger


class HeartbeatService(Thread):
    def __init__(self, node, interval=1):
        super().__init__(daemon=True, name="Heartbeat service")
        self.node = node
        self.interval = interval
        self._run = True

    def protocols_heartbeat(self):
        for protocol in self.node.protocols:
            if protocol.require_heartbeat and time.time() - protocol.last_heartbeat > protocol.heartbeat_interval:
                old_last_heartbeat = protocol.last_heartbeat
                logger.debug(f"Calling '{protocol.name}' protocol heartbeat")
                protocol.heartbeat()
                assert protocol.last_heartbeat != old_last_heartbeat,\
                    f'Protocol "{protocol.name}" must update last heartbeat every heartbeat'

    def run(self) -> None:
        logger.debug("Heartbeat service started")
        while self._run:
            self.protocols_heartbeat()
            time.sleep(self.interval)

    def stop(self):
        self._run = False
