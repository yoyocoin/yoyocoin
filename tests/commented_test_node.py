from network.node import Node

MOCK_SERVER_VERSION = {"Version": "0.9.1", "Commit": "", "Repo": "11", "System": "amd64/windows", "Golang": "go1.16.6"}
PUT_BLOCK_RESPONSE = {'Key': 'QmX24kz2ykEuXHd3ojWFniok9peNyJDsAz4XCJfvurob8B', 'Size': 14}
GET_BLOCK_RESPONSE = {"test": True}


def test_load_version():
    node = Node()
    assert node.ipfs_version == MOCK_SERVER_VERSION


def test_create_cid():
    node = Node()
    assert node.create_cid({"test": True}) == PUT_BLOCK_RESPONSE


def test_load_cid():
    node = Node()
    assert node.load_cid("QmX24kz2ykEuXHd3ojWFniok9peNyJDsAz4XCJfvurob8B") == GET_BLOCK_RESPONSE


def test_publish_to_topic():
    node = Node()
    assert node.publish_to_topic("test", {"test": True}) == ''
