"""
Spanning Tree module.
"""

import random

# traditional ephemeral port range
# see: https://datatracker.ietf.org/doc/html/rfc6056#section-2.1
_EPHEMERAL_PORT_MAX = 65535
_EPHEMERAL_PORT_MIN = 1024

def _ephemeral_port():
    """
    Generate an `ephemeral port <https://en.wikipedia.org/wiki/Ephemeral_port>`.

    returns: a generated ephemeral port
    """
    return random.randrange(_EPHEMERAL_PORT_MIN, _EPHEMERAL_PORT_MAX)

def _traverse(bridge: 'Bridge', path, paths):
    path.append(bridge)
    if not bridge.listened:
        paths.append(path.copy())
        return

    for listened in bridge.listened:
        _traverse(listened, path.copy(), paths)

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
    def is_root(self):
        """
        Whether the port is the root port.

        returns: whether the port is the root port.
        """
        return self._is_root

    @is_root.setter
    def is_root(self, is_root: bool):
        """
        Set the flag for whether the port is the root port.
        """
        self._is_root = is_root

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

    def __init__(self, name: str, *ports: Port):
        self._name = name
        self._ports = ports if ports else [Port()]
        self._is_root = False
        self._listened = {}

    def __eq__(self, other: object):
        return isinstance(other, Bridge) and self.name == other.name

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"Bridge: {self.name}"

    def connect(self, other: 'Bridge'):
        """
        Connect to another bridge.
        """
        unallocated_port = self._get_unallocated_port()
        if not unallocated_port:
            raise ValueError("No free ports.")

        other.connect_port(unallocated_port)
        self._listened[unallocated_port.number] = other

    def check_ports(self):
        """
        Check whether any of the ports is a root port,
        which determines whether the bridge is the root bridge.
        """
        for port in self._ports:
            if port.is_root:
                self._is_root = True
                return

        self._is_root = False

    def _get_unallocated_port(self):
        for port in self._ports:
            if not port.connected:
                return port

        return None

    @property
    def is_root(self):
        """
        Whether the bridge is the root bridge.

        returns: whether the bridge is the root bridge.
        """
        return self._is_root

    def connect_port(self, port: Port):
        """
        Connect port to the bridge's own unallocated port.
        """
        unallocated_port = self._get_unallocated_port()
        if unallocated_port is None:
            raise ValueError("No free ports.")

        port.connect(unallocated_port)

    @property
    def listened(self):
        """
        Get all the bridges that this bridge is listening to.

        returns: all the bridges that this bridge is listening tos.
        """
        return self._listened.values()

    @property
    def name(self):
        """
        The name of the bridge.

        returns: the name of the bridge.
        """
        return self._name

class Tree: # pylint: disable=too-few-public-methods
    """
    A tree of bridges.
    """

    def __init__(self, *bridges: Bridge):
        self._bridges = bridges
        self._shortest_path = None

    def shortest_path(self):
        """
        Get the shortest path to the root bridge.

        returns: the shortest path to the root bridge in the form
            of a list of bridges.
        """
        if self._shortest_path:
            return self._shortest_path

        root_bridge = None
        for bridge in self._bridges:
            bridge.check_ports()
            if bridge.is_root:
                root_bridge = bridge
                break

        if not root_bridge:
            raise ValueError("No root bridge in tree.")

        for listened in root_bridge.listened:
            paths = []
            _traverse(listened, [root_bridge], paths)
            paths.sort(key=len)

            if self._shortest_path is None or (len(paths[0]) < len(self._shortest_path)):
                self._shortest_path = paths[0]

        return self._shortest_path
