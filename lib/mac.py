from .phy import airtime, MIN_TX_WAIT_MSEC
from . import config as conf
import random

VERBOSE = False


def setTransmitDelay(node, packet):  # from RadioLibInterface::setTransmitDelay
    for p in reversed(node.packetsAtN[node.nodeid]):
        if p.seq == packet.seq and p.rssiAtN[node.nodeid] != 0 and p.receivedAtN[node.nodeid] == True: 
            # verboseprint('At time', round(self.env.now, 3), 'pick delay with RSSI of node', self.nodeid, 'is', p.rssiAtN[self.nodeid])
            return getTxDelayMsecWeighted(node, p.rssiAtN[node.nodeid])  # weigthed waiting based on RSSI
    return getTxDelayMsec()


def getTxDelayMsecWeighted(node, rssi):  # from RadioInterface::getTxDelayMsecWeighted
    snr = rssi-conf.NOISE_LEVEL
    SNR_MIN = -20
    SNR_MAX = 15
    if snr < SNR_MIN:
        verboseprint('Minimum SNR at RSSI of', rssi, 'dBm')  
        snr = SNR_MIN
    if snr > SNR_MAX:
        verboseprint('Maximum SNR at RSSI of', rssi, 'dBm')  
        snr = SNR_MAX

    if node.isRouter == True:
        CWmin = 1
        CWmax = 7
    else:
        CWmin = 2
        CWmax = 8

    CWsize = int((snr - SNR_MIN) * (CWmax - CWmin) / (SNR_MAX - SNR_MIN) + CWmin)
    CW = random.randint(0, 2**CWsize-1)
    verboseprint('Node', node.nodeid, 'has CW size', CWsize, 'and picked CW', CW)
    return CW * MIN_TX_WAIT_MSEC


def getTxDelayMsec():  # from RadioInterface::getTxDelayMsec
    CWsize = 2
    CW = random.randint(0, 2**CWsize-1)
    verboseprint('Picked CW', CW)
    return CW * MIN_TX_WAIT_MSEC


def getRetransmissionMsec(packet):  # from RadioInterface::getRetransmissionMsec
    packetAirtime = int(airtime(conf.SFMODEM[conf.MODEM], conf.CRMODEM[conf.MODEM], packet.packetlen, conf.BWMODEM[conf.MODEM]))
    return 2*packetAirtime + (2**2-1) * MIN_TX_WAIT_MSEC + (2**8-1) * MIN_TX_WAIT_MSEC 


if VERBOSE:
	def verboseprint(*args, **kwargs): 
		print(*args, **kwargs)
else:   
	def verboseprint(*args, **kwargs): 
		pass