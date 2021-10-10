"""
Spanning Tree module.
"""

import logging
import copy
import random

# traditional ephemeral port range
# see: https://datatracker.ietf.org/doc/html/rfc6056#section-2.1
_EPHEMERAL_PORT_MAX = 65535
_EPHEMERAL_PORT_MIN = 1024

_LOGGER = logging.getLogger(__name__)

def _ephemeral_port():
    """
    Generate an `ephemeral port <https://en.wikipedia.org/wiki/Ephemeral_port>`.

    returns: a generated ephemeral port
    """
    return random.randrange(_EPHEMERAL_PORT_MIN, _EPHEMERAL_PORT_MAX)

def shortest_path(root_bridge: 'Bridge', sending_bridge: 'Bridge'):
    """
    Compute the shortest path to the root bridge from the sending bridge.

    returns: the shortest path to the root bridge.
    """
    sending_bridge.send_bdpu(
        BridgeProtocolDataUnit(
            sending_bridge.name,
            root_bridge.name))

    received_bdpus = root_bridge.received_bdpus

    if _LOGGER.isEnabledFor(logging.DEBUG):
        _LOGGER.debug("received_bdpus: %s", received_bdpus)

    received_bdpus.sort(key=lambda bdpu: bdpu.total_cost)

    return received_bdpus[0].path

class BridgeProtocolDataUnit:
    """
    A BDPU containing info necessary for Spanning Tree Protocol (STP) to work.
    """

    def __init__(self, bridge_id, root_id):
        self._bridge_id = bridge_id
        self._root_id = root_id
        self._total_cost = 0
        self._path = []

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return (
            f"[BridgeProtocolDataUnit] {self.bridge_id}: "
            f"root_id={self._root_id}, "
            f"total_cost={self.total_cost}, "
            f"path={self.path}"
        )

    def add_bridge(self, bridge):
        """
        Add a bridge to the path tracked by the BDPU.
        """
        self._path.append(bridge)

    def add_cost(self, cost: int):
        """
        Add the cost of a bridge to the total cost of the path.
        """
        self._total_cost += cost

    @property
    def bridge_id(self):
        """
        The ID of the bridge sending the BDPU.

        returns: the ID of the bridge sending the BDPU.
        """
        return self._bridge_id

    def copy(self):
        """
        Create a copy of this BDPU.

        returns: a copy of this BDPU.
        """
        return copy.copy(self)

    @property
    def path(self):
        """
        The path taken by the BDPU.

        returns: the path taken by the BDPU.
        """
        return self._path

    @property
    def root_id(self):
        """
        The ID of the bridge that ought to receive packets.

        returns: the ID of the bridge that ought to receive packets.
        """
        return self._root_id

    @property
    def total_cost(self):
        """
        The total cost of the path taken by the BDPU.

        returns: the total cost of the path taken by the BDPU.
        """
        return self._total_cost

class Port:
    """
    A port.
    """

    def __init__(self, number: int = None, priority: int = 1):
        if number and (number < _EPHEMERAL_PORT_MIN or number > _EPHEMERAL_PORT_MAX):
            raise ValueError("Outside port range.")

        self._number = number if number else _ephemeral_port()
        self._priority = priority
        self._listener = None
        self._listened = None
        self._is_root = False

    def __eq__(self, other: 'Port'):
        return self.number == other.number

    def connect(self, other: 'Port'):
        """
        Connect this port to another one.
        """
        other.listener = self
        self.listened = other

    @property
    def connected(self):
        """
        Whether this port is connected to another port.
        """
        return self.listener is not None and self.listened is not None

    @property
    def listener(self):
        """
        Get the Port listening on this port.

        returns: the Port listening on this port.
        """
        return self._listener

    @listener.setter
    def listener(self, listener: 'Port'):
        """
        Set the Port to listen on this port.
        """
        self._listener = listener

    @property
    def listened(self):
        """
        Get the Port that this port is listening to.

        returns: the Port listened to by this port.
        """
        return self._listened

    @listened.setter
    def listened(self, listened: 'Port'):
        """
        Set the Port that this port is listening to.
        """
        self._listened = listened

    @property
    def number(self):
        """
        The port number.

        returns: the port number.
        """
        return self._number

class Bridge:
    """
    A bridge.
    """

    def __init__(self, name: str, *ports: Port, cost: int = 1):
        self._name = name
        self._ports = ports if ports else [Port()]
        self._is_root = False
        self._listened = {}
        self._listeners = {}
        self._cost = cost
        self._received_bdpus = []

    def __eq__(self, other: object):
        return isinstance(other, Bridge) and self.name == other.name

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"[Bridge] {self.name}"

    def connect(self, other: 'Bridge'):
        """
        Connect to another bridge.
        """
        unallocated_port = self.unallocated_port
        if not unallocated_port:
            raise ValueError("No free ports.")

        self._listened[unallocated_port.number] = other
        other.set_listener(self)

    def elect(self):
        """
        Elect a bridge to a root bridge.
        """
        self._is_root = True

    @property
    def is_root(self):
        """
        Whether the bridge is the root bridge.

        returns: whether the bridge is the root bridge.
        """
        return self._is_root

    @property
    def received_bdpus(self):
        """
        The received BDPUs.

        returns: the received BDPUs.
        """
        return self._received_bdpus.copy()

    @property
    def listened(self):
        """
        Get all the bridges that this bridge is listening to.

        returns: all the bridges that this bridge is listening tos.
        """
        return self._listened.values()

    @property
    def listeners(self):
        """
        Get all the bridges that are listening to this bridge.

        returns: all the bridges that are listening to this bridge.
        """
        return self._listeners.values()

    @property
    def name(self):
        """
        The name of the bridge.

        returns: the name of the bridge.
        """
        return self._name

    def send_bdpu(self, bdpu):
        """
        Send a BDPU to all of its listeners.
        """
        copied_bdpu = bdpu.copy()
        copied_bdpu.add_bridge(self)
        copied_bdpu.add_cost(self._cost)
        self._received_bdpus.append(copied_bdpu)
        for listener in self.listeners:
            listener.send_bdpu(bdpu)

    def set_listener(self, other: 'Bridge'):
        """
        Set another bridge as a listener of this bridge.
        """
        unallocated_port = self.unallocated_port
        if not unallocated_port:
            raise ValueError("No free ports.")

        self._listeners[unallocated_port.number] = other

    @property
    def unallocated_port(self):
        """
        An unallocated port.

        returns: an unallocated port
        """
        for port in self._ports:
            if not port.connected:
                return port

        return None
