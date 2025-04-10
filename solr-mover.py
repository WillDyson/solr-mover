#!/usr/bin/env python3

import argparse
import sys
import json
from collections import defaultdict, Counter

# number of decomission iterations to allow
MAX_ITERS = 10

# need limit to stop us stacking all replicas on three nodes
MAX_REPLICAS_PER_NODE=5

# prefer nodes already decommissioned
NODE_PROCESSED_FACTOR=1.2


def build_demo_placement():
    ''' build demo init structure for solr (ignores shards as a concept wlog) '''

    nodes = [f'node_{i}' for i in range(6)]
    shards = [f'shard_{i}_1' for i in range(10)]
    placement = defaultdict(list)

    for shard in shards:
        for replica in [(shard, f'replica_{i}') for i in range(3)]:
            node_scores = [0 for _ in nodes]

            for i, node in enumerate(nodes):
                node_replicas = placement.get(node) or []

                score = len(node_replicas)

                for (node_shard, _) in node_replicas:
                    if node_shard == shard:
                        score += 999999

                node_scores[i] = score

            i = node_scores.index(min(node_scores))

            placement[nodes[i]].append(replica)

    return dict(placement)


def load_state(f):
    ''' creates a placement using Solr state '''

    state = json.load(f)

    placement = defaultdict(list)

    collections = state['cluster']['collections']

    for collection in collections:
        shards = collections[collection]['shards']

        for shard in shards:
            replicas = shards[shard]['replicas']

            for replica in replicas:
                node = replicas[replica]['node_name']

                placement[node].append((f'{collection}.{shard}', replica))

    return placement


def move_candidate(placement, replica, ignored, processed):
    ''' find the best move candidate for a given replica '''

    (shard, replica) = replica

    min_score = None
    min_node = None

    for node in placement:
        if node in ignored:
            continue

        if shard in set(shard for (shard, _) in placement[node]):
            continue

        score = len(placement[node])

        if node not in processed:
            score *= NODE_PROCESSED_FACTOR

        if not min_score or score < min_score:
            if score <= MAX_REPLICAS_PER_NODE:
                min_score = score
                min_node = node

    return min_node


def iter(placement, processed, ignored=set(), processing=set()):
    ''' find the next nodes to empty (and how) ignoring both processed nodes and ignored nodes '''

    candidate_nodes = set(placement) - processed - ignored - processing

    # return new placement if no candidates left (terminal case)
    if not candidate_nodes:
        return placement, processing

    next_node = candidate_nodes.pop()

    shard_counter = \
        Counter([shard for replicas in placement.values() for (shard, _) in replicas])

    updated_placement = {node: replicas.copy() for node, replicas in placement.items()}

    for (shard, replica) in placement[next_node]:
        if shard_counter[shard] == 3:
            updated_placement[next_node].remove((shard, replica))

        elif shard_counter[shard] == 2:
            candidate = move_candidate(updated_placement, (shard, replica), ignored=processing.union({next_node}), processed=processed)

            # if no candidates then rerun ignoring next_node
            if not candidate:
                return iter(placement, processed, ignored.union({next_node}), processing)

            updated_placement[next_node].remove((shard, replica))
            updated_placement[candidate].append((shard, replica))

        else:
            raise Exception('Replica constraint not met')

    if len(updated_placement[next_node]) == 0:
        return iter(updated_placement, processed, ignored, processing.union({next_node}))

    # if next_node failed to empty then rerun ignoring next_node
    return iter(placement, processed, ignored.union({next_node}), processing)


def describe_placement(placement):
    ''' pretty prints a placement '''

    for node in placement:
        shards = ' '.join(shard for (shard, _) in placement[node])

        print(f'{node}: {shards}')

    print()


def describe_placement_diff(old, new):
    ''' prints actions needed to get from old placement to new '''

    for node in old:
        for replica in new[node]:
            if replica not in old[node]:
                print('added', replica, 'to', node)

    for node in old:
        for replica in old[node]:
            if replica not in new[node]:
                print('removed', replica, 'from', node)

    print()


def load_state(f):
    ''' creates a placement using Solr state '''

    state = json.load(f)

    placement = defaultdict(list)

    collections = state['cluster']['collections']

    for collection in collections:
        shards = collections[collection]['shards']

        for shard in shards:
            replicas = shards[shard]['replicas']

            for replica in replicas:
                node = replicas[replica]['node_name']

                placement[node].append((f'{collection}.{shard}', replica))

    return placement


def main():
    ''' builds step-by-step decomission plan for a given Solr cluster '''

    parser = argparse.ArgumentParser(prog='solr-mover')
    parser.add_argument('--statepath')
    parser.add_argument('--use-demo-topology', action='store_true')
    parser.add_argument('--decom', help='list of previously decomissioned node')
    parser.add_argument('--target', help='list of target nodes to decomission')
    args = parser.parse_args()

    if args.statepath:
        with open(args.statepath, 'r') as f:
            placement = load_state(f)

    elif args.use_demo_topology:
        placement = build_demo_placement()

    else:
        print('You must provide a statepath or use the demo topology')
        parser.print_help()
        sys.exit(1)

    processed = set()
    if args.decom:
        processed = set(args.decom.split(','))

    ignored = set()
    if args.target:
        ignored = placement.keys() - set(args.target.split(','))

    print('\n#########    Initial State    #########\n')
    describe_placement(placement, processed, ignored)

    iters = 0

    while len(processed.union(ignored)) < len(placement):
        if iters > MAX_ITERS:
            raise Exception('Max iterations reached')

        updated_placement, new_processed = iter(placement, processed, ignored)

        describe_placement_diff(placement, updated_placement)
        describe_placement(placement)

        placement = updated_placement
        processed.update(new_processed)

        iters += 1


if __name__ == '__main__':
    main()
