import networkx as nx
import random
import multiprocessing
import argparse
import math
import time
from Resource import *

def spatial_hash(node_position, grid_size, lattice_size):
    x, y = node_position
    grid_x = x // grid_size
    grid_y = y // grid_size
    # Combine grid_x and grid_y into a single index
    index = grid_x + grid_y * lattice_size
    return int(index)

def partition_lattice(lattice, num_partitions):
    num_nodes = len(lattice.nodes)
    lattice_size = int(math.sqrt(num_nodes))

    grid_size = lattice_size / math.sqrt(num_partitions)

    nodes_per_partition, remainder = divmod(num_nodes, num_partitions)
    partitions = [set() for _ in range(num_partitions)]

    for node in lattice.nodes:
        row, col = node
        node_position = (row, col)  # Assuming the node's position is represented by its row and column indices
        partition_index = spatial_hash(node_position, grid_size, lattice_size) % num_partitions
        partitions[partition_index].add(node)

    # Remove empty partitions
    partitions = [nodes for nodes in partitions if nodes]

    subgraphs = []
    for nodes in partitions:
        subgraph = lattice.subgraph(nodes)
        n = len(nodes)

        # Calculate the number of activated nodes based on the physical error rate
        num_error_nodes = sum(random.random() < 0.001 for _ in range(n))

        # Set the complexity equal to the number of activated nodes
        complexity = num_error_nodes

        subgraphs.append((subgraph, complexity))

    # Check for shared nodes between partitions
    for i in range(len(partitions)):
        for j in range(i + 1, len(partitions)):
            shared_nodes = partitions[i] & partitions[j]
            if shared_nodes:
                subgraph1, complexity1 = subgraphs[i]
                subgraph2, complexity2 = subgraphs[j]

                # Check if either subgraph is empty
                if not subgraph1.nodes:
                    subgraphs[i] = (subgraph2, complexity2)
                elif not subgraph2.nodes:
                    subgraphs[j] = (subgraph1, complexity1)
                else:
                    subgraph1.add_nodes_from(shared_nodes)
                    subgraph2.add_nodes_from(shared_nodes)
                    subgraphs[i] = (subgraph1, complexity1)
                    subgraphs[j] = (subgraph2, complexity2)

    return subgraphs

def combine_partitions(subgraph1, subgraph2):
    combined_graph = nx.Graph()
    combined_graph.add_nodes_from(subgraph1.nodes, bipartite=subgraph1.nodes)
    combined_graph.add_nodes_from(subgraph2.nodes, bipartite=subgraph2.nodes)
    combined_graph.add_edges_from(subgraph1.edges)
    combined_graph.add_edges_from(subgraph2.edges)

    return combined_graph

def combine_partitions_parallel(subgraphs):
    """
    Combine all subgraphs in parallel by combining pairs of subgraphs using a pool of workers.

    Args:
        subgraphs (list): A list of subgraphs to be combined.

    Returns:
        nx.Graph: The combined subgraph.
    """
    with multiprocessing.Pool() as pool:
        while len(subgraphs) > 1:
            if len(subgraphs) % 2 != 0:
                # If there is an odd number of subgraphs, combine the last subgraph with the second-to-last subgraph
                subgraphs[-2] = combine_partitions(subgraphs[-2], subgraphs[-1])
                subgraphs.pop()

            pairs = [(subgraphs[i], subgraphs[i + 1]) for i in range(0, len(subgraphs), 2)]
            subgraphs = pool.starmap(combine_partitions, pairs)

    return subgraphs[0] if subgraphs else None

if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Surface code lattice partitioning and processing.")
    parser.add_argument("--size", type=int, nargs=2, default=[5, 5], help="Size of the lattice grid (rows, cols)")
    parser.add_argument("--partitions", type=int, default=8, help="Number of partitions to create")
    parser.add_argument("--num_hr", type=int, default=2, help="Number of high-complexity resources")
    parser.add_argument("--num_lr", type=int, default=3, help="Number of low-complexity resources")
    parser.add_argument("--thresh_compl", type=int, default=6, help="Number of low-complexity resources")
    args = parser.parse_args()

    # Create a sample lattice
    lattice = nx.grid_2d_graph(args.size[0], args.size[1])

    # Partition the lattice into subgraphs with random complexity
    partitions = partition_lattice(lattice, args.partitions)

    # Create high-complexity resources
    high_complexity_resources = [Resource(i, max_complexity=float('inf'), type='high') for i in range(args.num_hr)]

    # Create low-complexity resources
    low_complexity_resources = [Resource(i + args.num_hr, max_complexity=args.thresh_compl, type='low') for i in range(args.num_lr)]

    start_time = time.time()
    # Perform dynamic load balancing and schedule partitions
    combined_resources = dynamic_load_balancing(partitions, high_complexity_resources, low_complexity_resources)
    end_time = time.time()  # Record the end time
    total_time = end_time - start_time
    print(f"\nScheduling overhead: {total_time:.9f} seconds.")

    # Estimate processing times for each resource
    max_time_taken = 0

    print("\nPartition Processing:")
    for resource in combined_resources:
        #print(f"Resource {resource.id} ({resource.type}):")
        resource.process_queue()
        print(f"Resource {resource.id} ({resource.type}) utilization time: {resource.utilization_time:.9f}")
        max_time_taken = max(max_time_taken, resource.max_time_taken)
        for task in resource.queue:
            print(f"  Partition with {len(task.nodes)} nodes (syndrome graph size {task.complexity})")
        print("\n")

    start_time = time.time()
    # Combine all partitions in parallel
    all_partitions = [subgraph for subgraph, _ in partitions]
    combined_lattice = combine_partitions_parallel(all_partitions)
    end_time = time.time()  # Record the end time
    total_time = end_time - start_time
    print(f"Lattice formation time: {total_time:.9f} seconds.")
    print(f"Combined lattice has {len(combined_lattice.nodes)} nodes.")

    print(f"\nMaximum time taken by any resource: {max_time_taken:.9f}")