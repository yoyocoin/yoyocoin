from typing import List, Tuple, Callable

from socketserver import ThreadingTCPServer, BaseRequestHandler
from queue import Queue

from .config import SERVER_RECV_BATCH, MESSAGE_DELIMITER


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

        self.finished_queues: List[Queue] = []
        self.queues: List[Queue] = []

        super().__init__(
            server_address, RequestHandlerClass, bind_and_activate=bind_and_activate
        )

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
        self.server: Server = server

        self.q: Queue = Queue(maxsize=10000)
        self.server.queues.append(self.q)
        super().__init__(request, client_address, server)

    def handle(self) -> None:
        print("new connection from", self.c_addr)
        msg = self.sock.recv(SERVER_RECV_BATCH)
        reply = self.server.processor.process(msg)
        if reply is not None:
            self.sock.send(reply)
            return  # Stop communication after response

        while True:
            msg = self.q.get()
            try:
                self.sock.send(msg + MESSAGE_DELIMITER)
            except BrokenPipeError:
                break

    def finish(self) -> None:
        self.server.finished_queues.append(self.q)
