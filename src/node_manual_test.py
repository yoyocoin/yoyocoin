from sys import argv

from manager import Manager

def main():
    port = int(argv[1])
    m = Manager(port)
    m.run()


if __name__ == "__main__":
    main()
