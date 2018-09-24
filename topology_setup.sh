#!/bin/bash
sudo mn --custom <file> --topo=mytopo --switch lxbr,stp=1 --link tc
