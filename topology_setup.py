from mininet.topo import Topo
from mininet.link import TCLink
from mininet.node import OVSSwitch

LOSS = 1
DELAY = "3ms"
class testTopo(Topo):
    "Testbed topology"

    def __init__(self):
        Topo.__init__(self)

        # adding hosts and switches
        h1 = self.addHost('h1')
        h2 = self.addHost('h2')
        s0 = self.addSwitch('s0')

        # adding links
        self.addLink(h1, s0, bw=10, delay=DELAY, loss=LOSS, max_queue_size=500)
        self.addLink(h2, s0, bw=10, delay='0ms', loss=0, max_queue_size=500)


topos = {'mytopo': (lambda: testTopo())}
