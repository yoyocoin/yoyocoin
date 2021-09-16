FROM python:3.9-slim-bullseye

# copy all src code and scripts
COPY . .

# install yoyocoin deps
RUN pip install -r requirements.txt

# install IPFS
RUN chmod -R +x /scripts
RUN /scripts/install-ipfs-private-network.sh

EXPOSE 4001 4001

# run ipfs node and yoyocoin node
CMD ["/scripts/run.sh"]