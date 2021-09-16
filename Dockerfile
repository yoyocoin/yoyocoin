FROM python:3.9-slim-bullseye

# copy all src code and scripts
COPY . .

# install yoyocoin deps
RUN pip install -r requirements.txt

# install IPFS
RUN ls
RUN chmod -R +x /scripts
RUN /scripts/install-ipfs-private-network.sh


# run ipfs node and yoyocoin node
CMD ["/scripts/run.sh"]