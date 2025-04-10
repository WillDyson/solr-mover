# Solr Mover

This script can be used to create a decommissioning plan for Solr.

It accepts a Solr state JSON file path as an argument.

## Modifiable Constants

- _MAX_ITERS_ (default 10): Number of decomission iterations to allow
- _MAX_REPLICAS_PER_NODE_ (default 5): Limit to stop us stacking all replicas on three nodes
- _NODE_PROCESSED_FACTOR_ (default 1.2): Factor to prefer nodes already decommissioned

## Example output

```
$ python3 solr-mover.py --state-path solr-state.json
#########    Initial State    #########

node_0.example.com:8995_solr [ ] (5): vertex_index.shard0 vertex_index.shard2 vertex_index.shard4 vertex_index.shard6 vertex_index.shard8
node_1.example.com:8995_solr [ ] (5): vertex_index.shard0 vertex_index.shard2 vertex_index.shard4 vertex_index.shard6 vertex_index.shard8
node_2.example.com:8995_solr [ ] (5): vertex_index.shard0 vertex_index.shard2 vertex_index.shard4 vertex_index.shard6 vertex_index.shard8
node_3.example.com:8995_solr [ ] (5): vertex_index.shard1 vertex_index.shard3 vertex_index.shard5 vertex_index.shard7 vertex_index.shard9
node_4.example.com:8995_solr [ ] (5): vertex_index.shard1 vertex_index.shard3 vertex_index.shard5 vertex_index.shard7 vertex_index.shard9
node_5.example.com:8995_solr [ ] (5): vertex_index.shard1 vertex_index.shard3 vertex_index.shard5 vertex_index.shard7 vertex_index.shard9


######### Iteration 1 #########

# removing vertex_index.shard0 from node_2.example.com:8995_solr
./delete_replica.sh vertex_index shard0 core_node2

# removing vertex_index.shard2 from node_2.example.com:8995_solr
./delete_replica.sh vertex_index shard2 core_node2

# removing vertex_index.shard4 from node_2.example.com:8995_solr
./delete_replica.sh vertex_index shard4 core_node2

# removing vertex_index.shard6 from node_2.example.com:8995_solr
./delete_replica.sh vertex_index shard6 core_node2

# removing vertex_index.shard8 from node_2.example.com:8995_solr
./delete_replica.sh vertex_index shard8 core_node2

# removing vertex_index.shard1 from node_3.example.com:8995_solr
./delete_replica.sh vertex_index shard1 core_node0

# removing vertex_index.shard3 from node_3.example.com:8995_solr
./delete_replica.sh vertex_index shard3 core_node0

# removing vertex_index.shard5 from node_3.example.com:8995_solr
./delete_replica.sh vertex_index shard5 core_node0

# removing vertex_index.shard7 from node_3.example.com:8995_solr
./delete_replica.sh vertex_index shard7 core_node0

# removing vertex_index.shard9 from node_3.example.com:8995_solr
./delete_replica.sh vertex_index shard9 core_node0

node_0.example.com:8995_solr [ ] (5): vertex_index.shard0 vertex_index.shard2 vertex_index.shard4 vertex_index.shard6 vertex_index.shard8
node_1.example.com:8995_solr [ ] (5): vertex_index.shard0 vertex_index.shard2 vertex_index.shard4 vertex_index.shard6 vertex_index.shard8
node_2.example.com:8995_solr [*] (0):
node_3.example.com:8995_solr [*] (0):
node_4.example.com:8995_solr [ ] (5): vertex_index.shard1 vertex_index.shard3 vertex_index.shard5 vertex_index.shard7 vertex_index.shard9
node_5.example.com:8995_solr [ ] (5): vertex_index.shard1 vertex_index.shard3 vertex_index.shard5 vertex_index.shard7 vertex_index.shard9

Decommissioned node(s): node_2.example.com:8995_solr, node_3.example.com:8995_solr
iter_moved=0 iter_added=0 iter_removed=10

######### Iteration 2 #########

# moving vertex_index.shard0 from node_1.example.com:8995_solr -> node_2.example.com:8995_solr
./move_replica.sh vertex_index core_node1 node_2.example.com:8995_solr

# moving vertex_index.shard2 from node_1.example.com:8995_solr -> node_2.example.com:8995_solr
./move_replica.sh vertex_index core_node1 node_2.example.com:8995_solr

# moving vertex_index.shard4 from node_1.example.com:8995_solr -> node_2.example.com:8995_solr
./move_replica.sh vertex_index core_node1 node_2.example.com:8995_solr

# moving vertex_index.shard6 from node_1.example.com:8995_solr -> node_2.example.com:8995_solr
./move_replica.sh vertex_index core_node1 node_2.example.com:8995_solr

# moving vertex_index.shard8 from node_1.example.com:8995_solr -> node_2.example.com:8995_solr
./move_replica.sh vertex_index core_node1 node_2.example.com:8995_solr

# moving vertex_index.shard1 from node_4.example.com:8995_solr -> node_3.example.com:8995_solr
./move_replica.sh vertex_index core_node1 node_3.example.com:8995_solr

# moving vertex_index.shard3 from node_4.example.com:8995_solr -> node_3.example.com:8995_solr
./move_replica.sh vertex_index core_node1 node_3.example.com:8995_solr

# moving vertex_index.shard5 from node_4.example.com:8995_solr -> node_3.example.com:8995_solr
./move_replica.sh vertex_index core_node1 node_3.example.com:8995_solr

# moving vertex_index.shard7 from node_4.example.com:8995_solr -> node_3.example.com:8995_solr
./move_replica.sh vertex_index core_node1 node_3.example.com:8995_solr

# moving vertex_index.shard9 from node_4.example.com:8995_solr -> node_3.example.com:8995_solr
./move_replica.sh vertex_index core_node1 node_3.example.com:8995_solr

node_0.example.com:8995_solr [ ] (5): vertex_index.shard0 vertex_index.shard2 vertex_index.shard4 vertex_index.shard6 vertex_index.shard8
node_1.example.com:8995_solr [*] (0):
node_2.example.com:8995_solr [.] (5): vertex_index.shard0 vertex_index.shard2 vertex_index.shard4 vertex_index.shard6 vertex_index.shard8
node_3.example.com:8995_solr [.] (5): vertex_index.shard1 vertex_index.shard3 vertex_index.shard5 vertex_index.shard7 vertex_index.shard9
node_4.example.com:8995_solr [*] (0):
node_5.example.com:8995_solr [ ] (5): vertex_index.shard1 vertex_index.shard3 vertex_index.shard5 vertex_index.shard7 vertex_index.shard9

Decommissioned node(s): node_4.example.com:8995_solr, node_1.example.com:8995_solr
iter_moved=10 iter_added=0 iter_removed=0

######### Iteration 3 #########

# moving vertex_index.shard0 from node_0.example.com:8995_solr -> node_1.example.com:8995_solr
./move_replica.sh vertex_index core_node0 node_1.example.com:8995_solr

# moving vertex_index.shard2 from node_0.example.com:8995_solr -> node_1.example.com:8995_solr
./move_replica.sh vertex_index core_node0 node_1.example.com:8995_solr

# moving vertex_index.shard4 from node_0.example.com:8995_solr -> node_1.example.com:8995_solr
./move_replica.sh vertex_index core_node0 node_1.example.com:8995_solr

# moving vertex_index.shard6 from node_0.example.com:8995_solr -> node_1.example.com:8995_solr
./move_replica.sh vertex_index core_node0 node_1.example.com:8995_solr

# moving vertex_index.shard8 from node_0.example.com:8995_solr -> node_1.example.com:8995_solr
./move_replica.sh vertex_index core_node0 node_1.example.com:8995_solr

# moving vertex_index.shard1 from node_5.example.com:8995_solr -> node_4.example.com:8995_solr
./move_replica.sh vertex_index core_node2 node_4.example.com:8995_solr

# moving vertex_index.shard3 from node_5.example.com:8995_solr -> node_4.example.com:8995_solr
./move_replica.sh vertex_index core_node2 node_4.example.com:8995_solr

# moving vertex_index.shard5 from node_5.example.com:8995_solr -> node_4.example.com:8995_solr
./move_replica.sh vertex_index core_node2 node_4.example.com:8995_solr

# moving vertex_index.shard7 from node_5.example.com:8995_solr -> node_4.example.com:8995_solr
./move_replica.sh vertex_index core_node2 node_4.example.com:8995_solr

# moving vertex_index.shard9 from node_5.example.com:8995_solr -> node_4.example.com:8995_solr
./move_replica.sh vertex_index core_node2 node_4.example.com:8995_solr

node_0.example.com:8995_solr [*] (0):
node_1.example.com:8995_solr [.] (5): vertex_index.shard0 vertex_index.shard2 vertex_index.shard4 vertex_index.shard6 vertex_index.shard8
node_2.example.com:8995_solr [.] (5): vertex_index.shard0 vertex_index.shard2 vertex_index.shard4 vertex_index.shard6 vertex_index.shard8
node_3.example.com:8995_solr [.] (5): vertex_index.shard1 vertex_index.shard3 vertex_index.shard5 vertex_index.shard7 vertex_index.shard9
node_4.example.com:8995_solr [.] (5): vertex_index.shard1 vertex_index.shard3 vertex_index.shard5 vertex_index.shard7 vertex_index.shard9
node_5.example.com:8995_solr [*] (0):

Decommissioned node(s): node_5.example.com:8995_solr, node_0.example.com:8995_solr
iter_moved=10 iter_added=0 iter_removed=0

#########       Summary       #########

total_moved=20
total_added=0
total_removed=10
total_decommissioned=6
```

