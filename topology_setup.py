from mininet.topo import Topo
from mininet.link import TCLink
from mininet.node import OVSSwitch


class testTopo(Topo):
    "Testbed topology"

    def __init__(self):
        Topo.__init__(self)

        # adding hosts and switches
        h1 = self.addHost('h1')
        h2 = self.addHost('h2')
        s0 = self.addSwitch('s0')

        # adding links
        self.addLink(h1, s0, bw=1, delay='5ms', loss=1, max_queue_size=50)
        self.addLink(h2, s0, bw=1, delay='5ms', loss=1, max_queue_size=50)


topos = {'mytopo': (lambda: testTopo())}
