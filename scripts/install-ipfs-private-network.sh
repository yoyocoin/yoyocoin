#!/bin/sh

# install deps
apt update -y
apt install wget -y

# install ipfs
wget https://dist.ipfs.io/go-ipfs/v0.9.1/go-ipfs_v0.9.1_linux-amd64.tar.gz
tar xvfz go-ipfs_v0.9.1_linux-amd64.tar.gz
cd go-ipfs || exit
./install.sh
export IPFS_PATH=~/.ipfs
ipfs init

# setup private network
echo "/key/swarm/psk/1.0.0/\n/base16/\n94f45a5cafead4bad1a309d95db631d00ced30b8a4f4ad3186c4b914360fdf8b\n" > ~/.ipfs/swarm.key
#ipfs bootstrap rm --all
#ipfs bootstrap add /ip4/<ip address of bootnode>/tcp/4001/ipfs/<peer identity hash of bootnode>
#ipfs bootstrap add /ip4/<ip address of bootnode>/tcp/4001/ipfs/<peer identity hash of bootnode>
#ipfs bootstrap add /ip4/<ip address of bootnode>/tcp/4001/ipfs/<peer identity hash of bootnode>

export LIBP2P_FORCE_PNET=1

# cleanup image
cd /
rm go-ipfs_v0.9.1_linux-amd64.tar.gz
apt remove wget -y

# Run in docker file: ipfs daemon --enable-pubsub-experiment
