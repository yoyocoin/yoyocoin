FROM python:3.9-slim-bullseye

# copy all src code and scripts
ADD src /
ADD scripts /

# install IPFS
RUN chmod +x /scripts/install-ipfs-private-network.sh
RUN /scripts/install-ipfs-private-network.sh

# run ipfs node and yoyocoin node
ENTRYPOINT ["ipfs", "daemon", "--enable-pubsub-experiment"]
CMD ["python3.9 src/run.py"]