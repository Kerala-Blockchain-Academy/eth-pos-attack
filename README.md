# eth-pos-attack

Created the blockchain network that can accept, validate and save the transaction. The network contains a master node that provides the online nodes and slot for the nodes that are initiating the connection.


### How to run?
- Start the master node. 
    - Edit the ip and port of the settings.yaml with the master node settings.( NB:- keep the port of the master node as port 5000)

- Run the master node <br>
    ```python node.py 5000```

The master node is responsible for providing the slot number to the newly joining peers. The newly joining peers which are unaware of the other peers, first connect with the master node by sending the **node_start** command to the master node. In response, the master sends back the connected peers and current slot number. The peer will now sync the slot number with its own internal thread and now has the whole list of connected peers available now. The same happen if a peer leave the network by **node_termination** command. The master node is also randomly select the attestor of the block in the current slot and broadcast among all other peers.

- Run the child node <br>
    ```python node.py <port number>```


### How to send a transaction?
Before sending a transaction make sure the sender has enough coin left. Sending a udp transaction message like the one given below to one of the online node 
```
from lib.p2p import Peer2Peer

tnx = {'from':'1','to':'A','nonce':0,'amount':10}
Peer2Peer.send(tnx,('192.168.1.7',6000))
```

To check the balance,  read the underlying database entry by,
```
python ./lib/state_trie.py
```

The database contain the key-value store with the key as the hash of the address and data, the value of address and balance. When the transaction occurs, the stateRoot entry of the block is updated which is calculated by finding the merkleRoot with the leaves as key-value pair.


### PoS Attack

The validator peers are assumed to be elected as the validator after they successfully send a specific amount of transaction into the network. Any misbehavior will cause the permanent loss of staked coins. The proposed attack is possible without going to a slashed condition.

The attacker used a modified version of script other than the normal one. The attacker node is hosted on the **attacker** branch. The attacker node can be run after moving to the attacker branch.

```
git checkout attacker & python node.py 7000
```

In the start of the communication, the attacker node act like a normal one. After an n chance, when the attacker is elected as the next proposer the real hacking starts which result in accepting the attacker node as genuine on by the rest of the nodes. 

But I would like to develop this blockchain network into a production ready one with the help of public contributions. It named  as **Catalyst Chain** and have already maintaining a repository on my github. I had this in my mind from the start of the project and well aware to remove this attack from my project. So the network is in-build capable of identifying the attack and adjusting accordingly if attack happens. Anyway for the sake of this project, the demonstration of the attack and its effects along with its solution can be seen. 