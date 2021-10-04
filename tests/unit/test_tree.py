# pylint: disable=missing-docstring

import collections
import spanning_tree.tree as spanning_tree_tree

def test_tree_shortest_path_least_bridges():
    Expectation = collections.namedtuple(
        'Expectation',
        [
            'expected_shortest_path',
            'root_bridge',
            'sending_bridge',
            'bridges',
        ])

    def first_case():
        # root <- a(1) <- c(1) <- d(1) <- f(1)
        #              <- b(1) <- e(1)
        #
        # Shortest path is:
        # root <- a <- b <- e
        root_bridge = spanning_tree_tree.Bridge('root')
        root_bridge.elect()

        bridge_a = spanning_tree_tree.Bridge(
            'a',
            spanning_tree_tree.Port(1024),
            spanning_tree_tree.Port(1025))
        bridge_b = spanning_tree_tree.Bridge('b')
        bridge_c = spanning_tree_tree.Bridge('c')
        bridge_d = spanning_tree_tree.Bridge('d')
        bridge_e = spanning_tree_tree.Bridge('e')
        bridge_f = spanning_tree_tree.Bridge('f')

        root_bridge.connect(bridge_a)
        bridge_a.connect(bridge_c)
        bridge_c.connect(bridge_d)
        bridge_d.connect(bridge_f)

        bridge_a.connect(bridge_b)
        bridge_b.connect(bridge_e)

        return Expectation(
            [bridge_e, bridge_b, bridge_a, root_bridge],
            root_bridge,
            bridge_e,
            [bridge_a, bridge_b, bridge_c, bridge_d, bridge_e, bridge_f])

    def second_case():
        # root <- a(1) <- c(1)
        #              <- b(1) <- d(1)
        #
        # Shortest path is:
        # root <- a <- c
        root_bridge = spanning_tree_tree.Bridge('root')
        root_bridge.elect()

        bridge_a = spanning_tree_tree.Bridge(
            'a',
            spanning_tree_tree.Port(1024),
            spanning_tree_tree.Port(1025))
        bridge_b = spanning_tree_tree.Bridge('b')
        bridge_c = spanning_tree_tree.Bridge('c')
        bridge_d = spanning_tree_tree.Bridge('d')

        root_bridge.connect(bridge_a)
        bridge_a.connect(bridge_c)

        bridge_a.connect(bridge_b)
        bridge_b.connect(bridge_d)

        return Expectation(
            [bridge_c, bridge_a, root_bridge],
            root_bridge,
            bridge_c,
            [bridge_a, bridge_b, bridge_c, bridge_d])

    expectations = [first_case(), second_case()]

    for expectation in expectations:
        assert expectation.expected_shortest_path \
            == spanning_tree_tree.shortest_path(
                    expectation.root_bridge,
                    expectation.sending_bridge,
                    *expectation.bridges)
