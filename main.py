import networkx as nx
import random
import time
import multiprocessing
import argparse
from Resource import Resource, hierarchical_schedule, dynamic_load_balancing, process_queue_wrapper
import math

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

    subgraphs = []
    for nodes in partitions:
        subgraph = lattice.subgraph(nodes)
        n = len(nodes)
        max_complexity = n * (n - 1) // 2

        complexity = random.randint(0, max_complexity)
        complexity = int(complexity ** 0.6)

        subgraphs.append((subgraph, complexity))

    for i in range(num_partitions):
        for j in range(i + 1, num_partitions):
            shared_nodes = partitions[i] & partitions[j]
            if shared_nodes:
                subgraph1, complexity1 = subgraphs[i]
                subgraph2, complexity2 = subgraphs[j]
                subgraph1.add_nodes_from(shared_nodes)
                subgraph2.add_nodes_from(shared_nodes)
                subgraphs[i] = (subgraph1, complexity1)
                subgraphs[j] = (subgraph2, complexity2)

    return subgraphs

def combine_partitions(subgraph1, subgraph2):
    """
    Combine two subgraphs by merging their nodes and edges.

    Args:
        subgraph1 (nx.Graph): The first subgraph.
        subgraph2 (nx.Graph): The second subgraph.

    Returns:
        nx.Graph: The combined subgraph.
    """
    combined_graph = nx.Graph()
    combined_graph.add_nodes_from(subgraph1.nodes, bipartite=subgraph1.nodes)
    combined_graph.add_nodes_from(subgraph2.nodes, bipartite=subgraph2.nodes)
    combined_graph.add_edges_from(subgraph1.edges)
    combined_graph.add_edges_from(subgraph2.edges)

    num_boundary_nodes = len(set(subgraph1.nodes) & set(subgraph2.nodes))
    processing_time = num_boundary_nodes  # Simulate time proportional to the number of boundary nodes

    # Simulate processing time
    time.sleep(processing_time / 1000000)  # Divide by 1000000 to reduce actual waiting time

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
            pairs = [(subgraphs[i], subgraphs[i + 1]) for i in range(0, len(subgraphs), 2)]
            subgraphs = pool.starmap(combine_partitions, pairs)

    return subgraphs[0]

if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Surface code lattice partitioning and processing.")
    parser.add_argument("--size", type=int, nargs=2, default=[5, 5], help="Size of the lattice grid (rows, cols)")
    parser.add_argument("--partitions", type=int, default=8, help="Number of partitions to create")
    parser.add_argument("--num_hr", type=int, default=2, help="Number of high-complexity resources")
    parser.add_argument("--num_lr", type=int, default=3, help="Number of low-complexity resources")
    args = parser.parse_args()

    start_time = time.time()  # Record the start time

    # Create a sample lattice
    lattice = nx.grid_2d_graph(args.size[0], args.size[1])

    # Partition the lattice into subgraphs with random complexity
    partitions = partition_lattice(lattice, args.partitions)

    # Create high-complexity resources
    high_complexity_resources = [Resource(i, max_complexity=float('inf'), type='high') for i in range(args.num_hr)]

    # Create low-complexity resources
    low_complexity_resources = [Resource(i + args.num_hr, max_complexity=6, type='low') for i in range(args.num_lr)]

    # Perform dynamic load balancing and schedule partitions
    combined_resources = dynamic_load_balancing(partitions, high_complexity_resources, low_complexity_resources)

    # Process queues in parallel using multiprocessing
    with multiprocessing.Pool(processes=len(combined_resources)) as pool:
        pool.map(process_queue_wrapper, combined_resources)

    # Print which partition was processed on which resource
    print("\nPartition Processing:")
    for resource in combined_resources:
        print(f"Resource {resource.id} ({resource.type}):")
        for task in resource.queue:
            print(f"  Partition with {len(task.nodes)} nodes (complexity {task.complexity})")

    # Combine all partitions in parallel
    all_partitions = [subgraph for subgraph, _ in partitions]
    combined_lattice = combine_partitions_parallel(all_partitions)
    print(f"\nCombined lattice has {len(combined_lattice.nodes)} nodes.")

    end_time = time.time()  # Record the end time
    total_time = end_time - start_time
    print(f"\nTotal time taken: {total_time:.6f} seconds.")