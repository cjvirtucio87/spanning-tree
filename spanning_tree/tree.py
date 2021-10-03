"""
Spanning Tree module.
"""

import random
from typing import List

def _ephemeral_port():
    """
    Generate an `ephemeral port <https://en.wikipedia.org/wiki/Ephemeral_port>`.

    returns: a generated ephemeral port
    """
    return random.randrange(1024, 65535)

class Port:
    """
    A port.
    """

    def __init__(self, number: int = None, priority: int = 1):
        self._number = number if number else _ephemeral_port()
        self._priority = priority

    @property
    def is_root(self):
        """
        Whether the port is the root port.

        returns: whether the port is the root port.
        """
        return False

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

    def __init__(self, name: str, ports: List[Port] = None):
        self._name = name
        self._ports = ports if ports else [Port()]
        self._is_root = False

    def __eq__(self, other: object):
        return isinstance(other, Bridge) and self.name == other.name

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"Bridge: {self.name}"

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

    @property
    def is_root(self):
        """
        Whether the bridge is the root bridge.

        returns: whether the bridge is the root bridge.
        """
        return self._is_root

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

        self._shortest_path = self._bridges
        return self._shortest_path
