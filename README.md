# Introduction to Daten

_Daten Team_

## What is Daten?
Daten is a universal database. It brings a platform for storing structured data for dApps, on top of the blockchain technology. Users can put their data on this database by spending some Daten tokens.
Daten can be used for uploading files, secure chatting, decentralized social networks, anonymous blogging, storing webpages, transferring value and etc.
Nobody owns these data, and every byte on this blockchain, once uploaded, will remain till the end of the universe. Daten is trying to spread the word that **_If You're Not Paying, You're The Product_**.

## Introduction
Daten is a P2P NoSQL data storage network, heavily inspired from the original Bitcoin design with some simplifications and features. Like Bitcoin, The Daten Network consists of miners who verify transactions by doing PoW on blocks. Accounts are simply private-key and public-key pairs, which have some balance in themselves.

Beside the balance property of an account, there can be other properties as well, known as
Attachments.

### Attachments
Storing data on Daten accounts is done through a concept called **Attachments**. Users are able to attach different types of data to a transaction. Attachments are not free, just as regular transactions in other cryptocurrencies cost a fee.

### Universal Database
Daten can be used as a database platform for different applications. Daten removes the need for remote servers and centeralized databases. Applications just need to define some schema and rules for the database of their application and use the Daten network for storing data. This way, the only
thing application developers should implement is a client side application which just connects to the Daten network. As an example, users can build a Twitter-like social network on top of Daten, without the need of a remote server.

## Data and Addresses, building blocks of the Daten Network
Each transaction in the Daten blockchain has a property called **data** which is used to store up to 64KB of data with different types (Strings, Bytes, Decimals, Booleans, Lists and Maps) in itself.
One unique feature of the Daten blockchain is that transactions can be referenced somehow as users are able to assign a name for their transactions.
One who has created and signed a transaction, owns the name of that transactions, and that means, if other users ever transfer money to this name (Instead of a public-key), the public-key will be the final owner of that money.

This feature brings two important features:

1. Users can assign names to their account by creating a dummy transaction with the name they want.

2. This helps the apps to organize their data in a tree-like structure.

### What is an address?
An address is where you can transact data or value in the Daten network. Unlike many popular cryptocurrencies like Bitcoin or Ethereum, where you can only transact your value to a cryptographic public-key, Daten network provides you two different kinds of addresses that you can use as the source and target of your transactions.

#### Raw addresses
A raw-address is same as a cryptographic public-key in Bitcoin, raw-addresses are the final destination of transmitted value. The value stored in a raw-address can be spended using its corresponding private-key.

#### String addresses
Users are able to assign string addresses to their raw addresses and use that human-readable name instead of long, error prone hex strings.

## Byteprice
Daten is about data, the fee of a transaction is calculated by multiplying the number of bytes it consumes by a byte-price. There is also a minimum byte-price in order to prevent spamming.

## Block Targeting
A major issue with cryptocurrencies like Bitcoin is that when clients sign and send a transaction with a low fee, it propagates over the network and all nodes get aware of it, and even though the transaction doesn't get accepted by the network, it can show up any time. In a cryptocurrency like Daten which the order of stored data matters, this can be problematic. Daten solves this issue by adding a property called **target** to transactions which represents the block index this transaction wants to sit on. Blocks containing transactions with targets different with block index will be invalid.

## Supply Account
Calculating rewards in Daten follows a different strategy. Daten blockchain has a special account called **Supply Account** which stores all the spendable value. Miners get a share (Something like 0.01 percent) of this account every time they mine a new block. This brings a smooth and clear rewarding mechanism in the Daten network.

## Instant Data Propagation
Daten is about exchanging data, not value. So there isn't any need for a message receiver to be sure
that the transaction has been verified by the miners. The only important thing is the signature of
the sender. As long as the sender puts a regular fee on his transactions, his transactions will be
propagated through the network, even if it doesn't get accepted by the miners. This allows **instant
transaction of data**, not value. Being aware of this concept is important as it makes real-time
messaging (E.g. chat applications) possible in the Daten network.

## Web friendliness
Protocol is implemented with HTTP and WebSockets, therefore you can easily communicate with the nodes
directly on a web browser.

## dApps
Daten is a decentralized application platform.
### Encrypted Instant Messaging
Talk anonymously without a third-party, and you can access your conversations everywhere.
### File Storage Platform
Load balancing as a feature!
### Decentralized Web
Uploading HTML content.
### Search Engines
A search-engine may be provided which is able to explore the entire Daten blockchain.
### General-purpose Database
Developers can develop apps without maintaining a server and let the user choose where he wants to store
his data. This can allow private social-networks on the Daten platform.

## Implementation
Daten is currently implemented in Python.
Daten uses **Argon2i** as its PoW hash function.

## Usage

### Running a Daten Node
Follow the instructions below to setup a Daten node on your server:

#### Install Python and PyDaten
You should have Python 3.5+ installed on your system in order to be able to run a
Daten node on your server.


#### Configure and run
Start with running `daten` command.

#### Running a Daten Mining Pool
Start your mining pool by running `daten-pool`.

### Start developing Daten dApps
Guide on how to develop Daten dApps using JavaScript.

#### Connecting to a Daten node
First you should connect to a Daten node like this:
```js
var wallet = new Wallet("http://nd1.daten.cash");
```

#### Get node status
State of a node includes the current epoch of that node and length of its
blockchain.
You can get the state of a node like this:
```js
wallet.getStatus(function() {
});
```

#### Listen to transactions
Listen to incoming transactions to a specific address:
```js
wallet.listen(address, function(tx) {
});
```

#### Send transactions
Send transactions:
```js
wallet.sendTransaction();
```

#### Query data
Find data:
```js
wallet.query(params, function(txs) {
});
```

#### Confirming transactions
Confirm transactions:
```js
wallet.confirm(tx, maxConfirmations, function(confirmations, hashTries) {
});
```

### Mining
Start earning Datens!
Connect to a mining Daten node or Mining pool!

## Illegal contents
A major problem in blockchains that store data.


## Bibliography
S. Nakamoto, Bitcoin: A peer-to-peer electronic cash system, 2008. Available: [http://bitcoin.org/bitcoin.pdf](http://bitcoin.org/bitcoin.pdf)

Cranklin, Let's Create Our Own Cryptocurrency, 2017. Available: [https://github.com/cranklin/crankycoin](https://github.com/cranklin/crankycoin)
