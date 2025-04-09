# Solr Mover

This script can be used to create a decommissioning plan for Solr.

It accepts a Solr state JSON file path as an argument.

## Modifiable Constants

- _MAX_ITERS_ (default 10): Number of decomission iterations to allow
- _MAX_REPLICAS_PER_NODE_ (default 5): Limit to stop us stacking all replicas on three nodes
- _NODE_PROCESSED_FACTOR_ (default 1.2): Factor to prefer nodes already decommissioned

## Example output

```
$ python3 solr-mover.py solr-state.json
node_0: shard_0_1 shard_2_1 shard_4_1 shard_6_1 shard_8_1
node_1: shard_0_1 shard_2_1 shard_4_1 shard_6_1 shard_8_1
node_2: shard_0_1 shard_2_1 shard_4_1 shard_6_1 shard_8_1
node_3: shard_1_1 shard_3_1 shard_5_1 shard_7_1 shard_9_1
node_4: shard_1_1 shard_3_1 shard_5_1 shard_7_1 shard_9_1
node_5: shard_1_1 shard_3_1 shard_5_1 shard_7_1 shard_9_1

removed ('shard_0_1', 'replica_1') from node_1
removed ('shard_2_1', 'replica_1') from node_1
removed ('shard_4_1', 'replica_1') from node_1
removed ('shard_6_1', 'replica_1') from node_1
removed ('shard_8_1', 'replica_1') from node_1
removed ('shard_1_1', 'replica_1') from node_4
removed ('shard_3_1', 'replica_1') from node_4
removed ('shard_5_1', 'replica_1') from node_4
removed ('shard_7_1', 'replica_1') from node_4
removed ('shard_9_1', 'replica_1') from node_4

node_0: shard_0_1 shard_2_1 shard_4_1 shard_6_1 shard_8_1
node_1:
node_2: shard_0_1 shard_2_1 shard_4_1 shard_6_1 shard_8_1
node_3: shard_1_1 shard_3_1 shard_5_1 shard_7_1 shard_9_1
node_4:
node_5: shard_1_1 shard_3_1 shard_5_1 shard_7_1 shard_9_1

added ('shard_3_1', 'replica_0') to node_1
added ('shard_5_1', 'replica_0') to node_1
added ('shard_7_1', 'replica_0') to node_1
added ('shard_9_1', 'replica_0') to node_1
added ('shard_0_1', 'replica_0') to node_4
added ('shard_2_1', 'replica_0') to node_4
added ('shard_4_1', 'replica_0') to node_4
added ('shard_6_1', 'replica_0') to node_4
added ('shard_8_1', 'replica_0') to node_4
added ('shard_1_1', 'replica_0') to node_4
removed ('shard_0_1', 'replica_0') from node_0
removed ('shard_2_1', 'replica_0') from node_0
removed ('shard_4_1', 'replica_0') from node_0
removed ('shard_6_1', 'replica_0') from node_0
removed ('shard_8_1', 'replica_0') from node_0
removed ('shard_1_1', 'replica_0') from node_3
removed ('shard_3_1', 'replica_0') from node_3
removed ('shard_5_1', 'replica_0') from node_3
removed ('shard_7_1', 'replica_0') from node_3
removed ('shard_9_1', 'replica_0') from node_3

node_0:
node_1: shard_3_1 shard_5_1 shard_7_1 shard_9_1
node_2: shard_0_1 shard_2_1 shard_4_1 shard_6_1 shard_8_1
node_3:
node_4: shard_0_1 shard_2_1 shard_4_1 shard_6_1 shard_8_1 shard_1_1
node_5: shard_1_1 shard_3_1 shard_5_1 shard_7_1 shard_9_1

added ('shard_5_1', 'replica_2') to node_0
added ('shard_7_1', 'replica_2') to node_0
added ('shard_9_1', 'replica_2') to node_0
added ('shard_8_1', 'replica_2') to node_1
added ('shard_0_1', 'replica_2') to node_3
added ('shard_2_1', 'replica_2') to node_3
added ('shard_4_1', 'replica_2') to node_3
added ('shard_6_1', 'replica_2') to node_3
added ('shard_1_1', 'replica_2') to node_3
added ('shard_3_1', 'replica_2') to node_3
removed ('shard_0_1', 'replica_2') from node_2
removed ('shard_2_1', 'replica_2') from node_2
removed ('shard_4_1', 'replica_2') from node_2
removed ('shard_6_1', 'replica_2') from node_2
removed ('shard_8_1', 'replica_2') from node_2
removed ('shard_1_1', 'replica_2') from node_5
removed ('shard_3_1', 'replica_2') from node_5
removed ('shard_5_1', 'replica_2') from node_5
removed ('shard_7_1', 'replica_2') from node_5
removed ('shard_9_1', 'replica_2') from node_5

node_0: shard_5_1 shard_7_1 shard_9_1
node_1: shard_3_1 shard_5_1 shard_7_1 shard_9_1 shard_8_1
node_2:
node_3: shard_0_1 shard_2_1 shard_4_1 shard_6_1 shard_1_1 shard_3_1
node_4: shard_0_1 shard_2_1 shard_4_1 shard_6_1 shard_8_1 shard_1_1
node_5:
```

