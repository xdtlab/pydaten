<img src="pydaten/network/resources/static/logo.svg" alt="Daten Logo" width="96">

# Daten Project

[![Build Status](https://travis-ci.org/daten-project/pydaten.svg?branch=master)](https://travis-ci.org/daten-project/pydaten)

It has been years since the first version of Bitcoin came out. Although a massive amount of time has been spent on research and development of blockchains, they are still being used primarily for financial purposes.

I, as a Software Engineer, interested in Blockchain stuff, decided to design and implement a brand new P2P network from scratch, in which members are able to store structured data by spending some tokens.

## What is Daten?

Daten is a P2P decentralized database platform based on blockchain technology. It removes the need for remote servers and centralized databases. Applications just need to define some schema and rules for their database and use the Daten network for storing data. This way, the only thing application developers should implement is a client side program that just connects to the Daten network.

Through Daten, you can upload files, securely chat with your friends, participate in decentralized social networks, store webpages, transfer value and much more.

As an example, users can build a Twitter-like social network on top of Daten, without the need of a remote server, with everything, including the HTML pages, CSS styles, JS files and images uploaded on the blockchain itself.

Daten is a NoSQL data storage network, heavily inspired from the original Bitcoin. The Daten Network consists of miners who verify the transactions by doing PoW on blocks. Accounts are simply private-key and public-key pairs, which have some balance in themselves.

Unlike regular cryptocurrencies in which transactions are just means of transferring value, in Daten network, every transaction is also a record in a database with a unique identifier.

Users are able to attach different types of data to the transactions. The difference is, those data are **_indexed_** and **_queryable_**. Attachments are not free, just as regular transactions in other cryptocurrencies cost a fee.

The result is an universal database, which provide a platform for storing structured data for dApps, on top of the blockchain technology. Users can put their data on this database by spending some Daten tokens.

Nobody owns these data, and every byte on this blockchain, once uploaded, will remain till the end of the universe. Daten is trying to spread the word that **_“If You're Not Paying, You're The Product”_**.

## Data and Addresses, building blocks of the Daten Network

Unlike many popular cryptocurrencies like Bitcoin or Ethereum, where you can only transact your value to a cryptographic public-key, Daten network provides you two different ways to

1. Public-Keys: A public-key in Daten Network is same as a cryptographic public-key in Bitcoin, public-keys are the final destination of transmitted value. The value assigned to a public-key can be spent using its corresponding private-key.

2. Domains: Users are able to assign domain names to their public-keys and use that human-readable name instead of long, error prone hex strings as the destination of their transactions.

All of the transactions in the Daten blockchain have unique domain names associated with them. These identifiers are dot-separated names, representing a huge tree of data.

<p align="center">
  <img src="https://user-images.githubusercontent.com/42034037/46507248-73be9000-c844-11e8-8839-2b5be2178060.png" alt="Daten Tree"/>
</p>

Each transaction in the Daten blockchain has a property called **data** which is used to store up to 64KB of data with different types, including **Strings**, **Bytes**, **Booleans**,  **Decimals**, **Maps**, **Lists** (and **Functions** in the future) in itself.

Daten nodes are continuously indexing the incoming transactions in their database, which is used to store entire transaction history of the Daten blockchain. There are currently two ways for querying this database. You can either find a transaction by its full-name or find all transactions associated with children of a particular name. Both of these operations are fast and efficient.

Consider the blog example above, you can find contents of the second post of Alice by querying `post2.alice.blog`, or you can find all comments attached to the first post of Bob by querying `*.post1.bob`. If you want to see the main page of `blog` dApp, you can query `index.web.blog` which will return a HTML document, and the HTML document itself can include the jQuery library from `jquery.js.web.blog`.

One who has created and signed a transaction, owns the name of that transactions, and that means, if other users ever transfer money to this name (Instead of a public-key), the public-key will be the final owner of that money.

 - If you send a transaction to a public-key with name `alice`, you will own the domain `alice`.
 - If you send a transaction to `bob` with name `alice`, you will own the domain `alice.bob`.

This feature brings two important features:

1. Users can assign domains to their accounts by creating dummy transactions with the domain name they want.

2. This helps the dApps to organize their data in a tree-like structure.

## Byteprice
Daten is about data, the fee of a transaction is calculated by multiplying the number of bytes it consumes by a byte-price. There is also a minimum byte-price in order to prevent spamming.

## Block Targeting
A major issue with cryptocurrencies like Bitcoin is that when clients sign and send a transaction with a low fee, it propagates over the network and all nodes get aware of it, and even though the transaction doesn't get accepted by the network, it can show up any time. In a cryptocurrency like Daten which the order of stored data matters, this can be problematic. Daten solves this issue by adding a property called **target** to transactions which represents the block index this transaction wants to sit on. Blocks containing transactions with targets different with block index will be invalid.

## Supply Account
Calculating rewards in Daten follows a different strategy. Daten blockchain has a special account called **Supply Account** which stores all the spendable value. Miners get a share (Something like 0.01 percent) of this account every time they mine a new block. This brings a smooth and clear rewarding mechanism in the Daten network.

## Instant Data Propagation
Daten is about exchanging data, not value. So there isn't any need for a message receiver to be sure that the transaction has been verified by the miners. The only important thing is the signature of the sender. As long as the sender puts a regular fee on his transactions, his transactions will be propagated through the network, even if it doesn't get accepted by the miners. This allows **instant transaction of data**, not value. Being aware of this concept is important as it makes real-time messaging (E.g. chat applications) possible in the Daten network.

## Web friendliness
Protocol is implemented with HTTP and WebSockets, therefore you can easily communicate with the nodes directly on a web browser.

## dApps
Daten is a decentralized application platform.
### Encrypted Instant Messaging
Talk anonymously without a third-party, and you can access your conversations everywhere.
### File Storage Platform
You can upload your files on the Daten Network with anysize.
Load balancing as a feature!
### Decentralized Web
Uploading HTML content.
### Search Engines
A search-engine may be provided which is able to explore the entire Daten blockchain.
### General-purpose Database
Developers can develop dApps without maintaining a server and let the user choose where he wants to store his data. This can make private social-networks on the Daten platform possible.

## Implementation
Daten is currently implemented in Python.
Daten uses **Argon2i** as its PoW hash function.
Total supply is: 18,446,744,073 XDT

## Usage

### Running a Daten Node (Docker way)

#### Docker way

```bash
git clone https://github.com/xdtlab/pydaten.git
cd ./pydaten
docker build -t daten .
docker run -v /path/to/data:/data -p 32323:32323 daten
```

#### Normal way

You should have Python 3.5+ installed on your system in order to be able to run a Daten node.
```bash
git clone https://github.com/xdtlab/pydaten.git
cd ./pydaten
sudo pip3 install -r requirements.txt
sudo python3 setup.py install
```
Configurations are normally stored in `~/.daten/node.json`.

```json
{
  "host": "1.2.3.4:32323",
  "ip": "0.0.0.0",
  "port": 32323,
  "path": "~/.daten/data",
  "initialPeers": [
    "nd1.daten.cash:32323"
  ]
}
```
 - `host` is where the network nodes are able to find you in the internet.
 - `ip` and `port` is the listening socket.
 - `path` is where the blocks are going to be stored.
 - `initialPeers` is a list of

After setting up the configurations you can run your node:
```bash
daten
```
### Start developing Daten dApps using daten.js
A guide on how to develop Daten dApps using JavaScript is here:
[https://github.com/xdtlab/daten.js](https://github.com/xdtlab/daten.js)

### Mining
Start mining Daten tokens using arbeit!
[https://github.com/xdtlab/arbeit](https://github.com/xdtlab/arbeit)

## Illegal contents
A major problem in blockchains that store data.


## Bibliography
S. Nakamoto, Bitcoin: A peer-to-peer electronic cash system, 2008. Available: [http://bitcoin.org/bitcoin.pdf](http://bitcoin.org/bitcoin.pdf)

Cranklin, Let's Create Our Own Cryptocurrency, 2017. Available: [https://github.com/cranklin/crankycoin](https://github.com/cranklin/crankycoin)
