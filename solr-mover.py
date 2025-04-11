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

    nodes = [f'node_{i}.example.com:8995_solr' for i in range(6)]
    shards = [f'vertex_index.shard{i}' for i in range(10)]
    placement = defaultdict(list)

    for shard in shards:
        for replica in [(shard, f'core_node{i}') for i in range(3)]:
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
            if score < MAX_REPLICAS_PER_NODE:
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

    updated_placement = {node: replicas.copy() for node, replicas in placement.items()}

    for (shard, replica) in placement[next_node]:
        shard_counter = \
            Counter([shard for replicas in updated_placement.values() for (shard, _) in replicas])

        if shard_counter[shard] >= 3:
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


def describe_placement(placement, previously_processed, new_processed=set()):
    ''' pretty prints a placement '''

    for node in placement:
        c = ' '

        if node in previously_processed:
            c = '.'

        if node in new_processed:
            c = '*'

        shard_count = len(placement[node])
        shards = ' '.join(shard for (shard, _) in placement[node])

        print(f'{node} [{c}] ({shard_count}): {shards}')

    print()


def summarise_placement_diff(old, new):
    ''' returns counts for placement diff changes '''

    old_shards = defaultdict(set)

    for node in old:
        for (shard, _) in old[node]:
            old_shards[shard].add(node)

    new_shards = defaultdict(set)

    for node in new:
        for (shard, _) in new[node]:
            new_shards[shard].add(node)

    if old_shards.keys() - new_shards.keys():
        raise Exception('Shards missing in new placement')

    tot_moved = 0
    tot_added = 0
    tot_removed = 0

    for shard in new_shards:
        nodes_added = new_shards[shard] - old_shards[shard]
        nodes_removed = old_shards[shard] - new_shards[shard]

        no_moved = min(len(nodes_added), len(nodes_removed))
        no_added = len(nodes_added) - no_moved
        no_removed = len(nodes_removed) - no_moved

        tot_moved += no_moved
        tot_added += no_added
        tot_removed += no_removed

    return tot_moved, tot_added, tot_removed


def ensure_sufficient_replicas(new):
    ''' asserts at least two replicas per shard '''

    new_shards = defaultdict(set)

    for node in new:
        for (shard, _) in new[node]:
            new_shards[shard].add(node)

    for shard in new_shards:
        if len(new_shards[shard]) < 2:
            raise Exception(f'Shard {shard} less than two replicas')


def describe_placement_diff(old, new):
    ''' prints actions needed to get from old placement to new '''

    old_shards = defaultdict(set)

    for node in old:
        for (shard, _) in old[node]:
            old_shards[shard].add(node)

    new_shards = defaultdict(set)

    for node in new:
        for (shard, _) in new[node]:
            new_shards[shard].add(node)

    if old_shards.keys() - new_shards.keys():
        raise Exception('Shards missing in new placement')

    for shard in new_shards:
        collection, shard_id = shard.split('.')

        nodes_added = new_shards[shard] - old_shards[shard]
        nodes_removed = old_shards[shard] - new_shards[shard]

        no_moved = min(len(nodes_added), len(nodes_removed))

        for _ in range(no_moved):
            target = nodes_added.pop()
            source = nodes_removed.pop()
            replica = next(replica_ for (shard_, replica_) in new[target] if shard_ == shard)

            print(f'# moving {shard} from {source} -> {target}')
            print(f'# delete and add is better than move but it is not possible to pre-generate that')
            print(f'./move_replica.sh {collection} {replica} {target}\n')

        for node in nodes_added:
            print(f'# adding {shard} to {node}')
            print(f'./add_replica.sh {collecion} {shard_id} {node}\n')

        for node in nodes_removed:
            replica = next(replica_ for (shard_, replica_) in old[node] if shard_ == shard)

            print(f'# removing {shard} from {node}')
            print(f'./delete_replica.sh {collection} {shard_id} {replica}\n')


def main():
    ''' builds step-by-step decomission plan for a given Solr cluster '''

    parser = argparse.ArgumentParser(prog='solr-mover')
    parser.add_argument('--state-path')
    parser.add_argument('--use-demo-placement', action='store_true')
    parser.add_argument('--decom', help='list of previously decomissioned node')
    parser.add_argument('--target', help='list of target nodes to decomission')
    args = parser.parse_args()

    if args.state_path:
        with open(args.state_path, 'r') as f:
            placement = load_state(f)

    elif args.use_demo_placement:
        placement = build_demo_placement()

    else:
        print('You must provide a --state-path or --use-demo-placement')
        parser.print_help()
        sys.exit(1)

    processed = set()
    if args.decom:
        processed = set(args.decom.split(','))

    ignored = set()
    if args.target:
        ignored = placement.keys() - set(args.target.split(','))

    tot_moved = 0
    tot_added = 0
    tot_removed = 0
    tot_decom = 0

    print('\n#########    Initial State    #########\n')
    describe_placement(placement, processed, ignored)

    iters = 0

    while len(processed.union(ignored)) < len(placement):
        if iters > MAX_ITERS:
            raise Exception('Max iterations reached')

        updated_placement, new_processed = iter(placement, processed, ignored)

        print(f'\n######### Iteration {iters+1} #########\n')
        ensure_sufficient_replicas(updated_placement)
        describe_placement_diff(placement, updated_placement)
        describe_placement(updated_placement, processed, new_processed)
        print('Decommissioned node(s):', ', '.join(new_processed))

        no_moved, no_added, no_removed = summarise_placement_diff(placement, updated_placement)
        tot_moved += no_moved
        tot_added += no_added
        tot_removed += no_removed
        tot_decom += len(new_processed)
        print(f'iter_moved={no_moved} iter_added={no_added} iter_removed={no_removed}')

        placement = updated_placement
        processed.update(new_processed)

        iters += 1

    print('\n#########       Summary       #########\n')
    print(f'total_moved={tot_moved}')
    print(f'total_added={tot_added}')
    print(f'total_removed={tot_removed}')
    print(f'total_decommissioned={tot_decom}')


if __name__ == '__main__':
    main()
