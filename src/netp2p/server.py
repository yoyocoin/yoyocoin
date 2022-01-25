from typing import Tuple, Callable

from socketserver import ThreadingTCPServer, BaseRequestHandler
from queue import Queue


RECV_BATCH = 2048
MESSAGE_DELIMITER = b"%99"  # TODO: move to p2p network config


class Server(ThreadingTCPServer):
    def __init__(
        self,
        server_address: Tuple[str, int],
        RequestHandlerClass: Callable[..., BaseRequestHandler],
        bind_and_activate: bool,
        processor,
    ) -> None:
        self.s_addr = server_address
        self.processor = processor

        self.finished_queues = []
        self.queues = []

        super().__init__(server_address, RequestHandlerClass, bind_and_activate=bind_and_activate)
    
    def send(self, msgs: list):
        for q in self.queues:
            for msg in msgs:
                q.put(msg)
        fqs = self.finished_queues.copy()
        self.finished_queues.clear()
        for fq in fqs:
            self.queues.remove(fq)
        


class RequestHandler(BaseRequestHandler):
    def __init__(self, request, client_address: Tuple[str, int], server) -> None:
        self.sock = request
        self.c_addr = client_address
        self.server = server

        self.q = Queue(maxsize=10000)
        self.server.queues.append(self.q)
        super().__init__(request, client_address, server)
    
    def handle(self) -> None:
        print("new connection from", self.c_addr)
        msg = self.sock.recv(RECV_BATCH)
        self.server.processor.process(msg)

        while True:
            msg = self.q.get()
            try:
                self.sock.send(msg + MESSAGE_DELIMITER)
            except BrokenPipeError:
                break

    def finish(self) -> None:
        self.server.finished_queues.append(self.q)