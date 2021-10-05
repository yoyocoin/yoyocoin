from sys import argv
from time import sleep
from random import randrange

from yoyocoin_node import YoyocoinNode
from blockchain import Actor, Config


def idle():
    try:
        while True:
            sleep(1)
    except KeyboardInterrupt:
        pass


def main():
    ip = argv[1]
    if len(argv) > 2:
        secret_key = argv[2]
    else:
        secret_key = "main_secret"
    actor = Actor(secret_key)
    actor2 = Actor("Recipient")
    Config.test_net = True

    n = YoyocoinNode(host=ip)
    n.start()
    sleep(5)
    n.sync()
    while True:
        sleep(randrange(30, 50))
        for _ in range(2):
            transaction = actor.transfer_coins(actor2.address, 0.1)
            n.broadcast_transaction(transaction.to_dict())
        n.broadcast_candidate_block(actor.forge_block().to_dict())
    idle()


if __name__ == "__main__":
    main()
