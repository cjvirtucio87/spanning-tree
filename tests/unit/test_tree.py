# pylint: disable=missing-docstring

import spanning_tree.tree as spanning_tree_tree

# root <- a(1) <- c(1) <- d(1)
#      <- b(1) <- e(1)
#
# Shortest path is:
# root <- b <- e
def test_tree_shortest_path_least_bridges():
    root_bridge = spanning_tree_tree.Bridge('root')
    bridge_a = spanning_tree_tree.Bridge('a')
    bridge_b = spanning_tree_tree.Bridge('b')
    bridge_c = spanning_tree_tree.Bridge('c')
    bridge_d = spanning_tree_tree.Bridge('d')
    bridge_e = spanning_tree_tree.Bridge('e')
    tree = spanning_tree_tree.Tree(
        root_bridge,
        bridge_a,
        bridge_b,
        bridge_c,
        bridge_d,
        bridge_e)

    assert [root_bridge, bridge_b, bridge_e] == tree.shortest_path()
