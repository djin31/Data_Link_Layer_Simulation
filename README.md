# Data_Link_Layer_Simulation
Go-Back-N Data Link simulation for COL334 Assignment 2

# Running the code
```
$ ./topology_setup.sh #sets up the topology on mininet
```
On mininet
```
$ xterm h1 h2
```
On host1 run 
```
python GBN.py 1 <host1 ip> <host2 ip>
```
On host2 run 
```
python GBN.py 2 <host2 ip> <host1 ip>”
```
-v [verbose flag] can be given to python scripts to print out the packets sent and received by network layer in a file
