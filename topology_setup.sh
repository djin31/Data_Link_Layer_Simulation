#!/bin/bash
sudo mn --custom topology_setup.py --topo=mytopo --switch lxbr,stp=1 --link tc
