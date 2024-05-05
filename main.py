import networkx as nx
import random
import multiprocessing
import argparse
import math
import time
import matplotlib.pyplot as plt
import numpy as np
from Resource import *

def spatial_hash(node_position, grid_size, lattice_size, num_partitions):
    x, y = node_position
    grid_x = int(x // grid_size)
    grid_y = int(y // grid_size)
    partition_index = (grid_x + grid_y * (lattice_size // grid_size)) % num_partitions
    return int(partition_index)

def partition_lattice(lattice, num_partitions):
    num_nodes = len(lattice.nodes)
    lattice_size = int(math.sqrt(num_nodes))

    partitions = [set() for _ in range(num_partitions)]

    # Start with an initial grid size
    grid_size = lattice_size / math.sqrt(num_partitions)

    # Iterate until all partitions are non-empty
    while any(len(partition) == 0 for partition in partitions):
        partitions = [set() for _ in range(num_partitions)]
        for node in lattice.nodes:
            row, col = node
            node_position = (row, col)
            partition_index = spatial_hash(node_position, grid_size, lattice_size, num_partitions)
            partitions[partition_index].add(node)

        # If there are empty partitions, reduce the grid size and try again
        if any(len(partition) == 0 for partition in partitions):
            grid_size /= 2

    subgraphs = []
    partition_index = 0
    for nodes in partitions:
        subgraph = lattice.subgraph(nodes)
        n = len(nodes)

        # Calculate the number of activated nodes based on the physical error rate
        num_error_nodes = sum(random.random() < 0.001 for _ in range(n))

        # Set the complexity equal to the number of activated nodes
        complexity = num_error_nodes + 1

        subgraphs.append((subgraph, complexity, partition_index))
        partition_index += 1

    # Check for shared nodes between partitions
    for i in range(len(partitions)):
        for j in range(i + 1, len(partitions)):
            shared_nodes = partitions[i] & partitions[j]
            if shared_nodes:
                subgraph1, complexity1, _ = subgraphs[i]
                subgraph2, complexity2, _ = subgraphs[j]

                subgraph1.add_nodes_from(shared_nodes)
                subgraph2.add_nodes_from(shared_nodes)
                subgraphs[i] = (subgraph1, complexity1, i)
                subgraphs[j] = (subgraph2, complexity2, j)

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
    parser.add_argument("--thresh_compl", type=int, default=2, help="Number of low-complexity resources")
    args = parser.parse_args()

    # Create a sample lattice
    lattice = nx.grid_2d_graph(args.size[0], args.size[1])

    # Partition the lattice into subgraphs with random complexity
    partitions = partition_lattice(lattice, args.partitions)

    # Add partition index to each partition
    for i, (subgraph, complexity, partition_index) in enumerate(partitions):
        partitions[i] = (subgraph, complexity, partition_index)

    # Print all partitions and their associated complexities
    print("\nAll Partitions:")
    for subgraph, complexity, partition_index in partitions:
        print(f"Partition {partition_index}: Complexity = {complexity}")

    # Create high-complexity resources
    high_complexity_resources = [Resource(i, max_complexity=float('inf'), type='high') for i in range(args.num_hr)]

    # Create low-complexity resources
    low_complexity_resources = [Resource(i + args.num_hr, max_complexity=args.thresh_compl, type='low') for i in range(args.num_lr)]

    start_time = time.time()
    # Perform dynamic load balancing and schedule partitions (SEQUENTIAL)
    combined_resources = dynamic_load_balancing(partitions, high_complexity_resources, low_complexity_resources)
    end_time = time.time()  # Record the end time
    total_time = end_time - start_time
    print(f"\nScheduling overhead: {total_time:.9f} seconds.")

    # Print all partitions and their associated complexities
    print("\nAll Partitions:")
    for subgraph, complexity, partition_index in partitions:
        print(f"Partition {partition_index}: Complexity = {complexity}")

    # Estimate processing times for each resource (PARALLEL)
    max_time_taken = 0

    print("\nPartition Processing:")
    for resource in combined_resources:
        processed_tasks = resource.process_queue()
        total_processing_time = sum(processing_time for _, processing_time in processed_tasks)
        print(f"Resource {resource.id} ({resource.type}) estimated processing time: {total_processing_time:.9f}")
        print(f"Resource {resource.id} ({resource.type}) utilization time: {resource.utilization_time:.9f}")
        max_time_taken = max(max_time_taken, resource.utilization_time)
        for task, processing_time in processed_tasks:
            print(f"Resource {resource.id} ({resource.type}) processing Partition {task.partition_index}")
            print(f"  Partition {task.partition_index} with {len(task.nodes)} nodes (syndrome graph size {task.complexity})")
        print("\n")

    # Generate Gantt chart
    fig, ax = plt.subplots(figsize=(12, 8))
    unique_resources = list(set(combined_resources))
    num_colors = len(partitions)
    colors = plt.colormaps['rainbow'](np.linspace(0, 1, num_colors))
    y_ticks = []
    y_labels = []

    for i, resource in enumerate(unique_resources):
        for task_start, task_end, task in resource.tasks:
            partition_index = task.partition_index
            ax.broken_barh([(task_start, task_end - task_start)], (i - 0.4, 0.8), color=colors[partition_index % num_colors])
            ax.text(task_start + (task_end - task_start) / 2, i, f"P{partition_index}", ha='center', va='center', color='black', fontsize=10)

        y_ticks.append(i)
        y_labels.append(f"Resource {resource.id} ({resource.type})")

    ax.set_ylim(-0.5, len(unique_resources) - 0.5)
    ax.set_yticks(y_ticks)
    ax.set_yticklabels(y_labels)
    ax.set_xlabel('Time')
    ax.set_title('Partition Execution Gantt Chart')
    ax.grid(True)

    # Add legend
    partition_indices = [partition_index for _, _, partition_index in partitions]
    legend_labels = [f"Partition {index}" for index in partition_indices]
    legend_handles = [plt.Rectangle((0, 0), 1, 1, color=colors[index % num_colors]) for index in partition_indices]
    ax.legend(legend_handles, legend_labels, loc='upper right', title='Partitions', ncol=2)

    plt.tight_layout()
    plt.show()

    start_time = time.time()
    # Combine all partitions in parallel
    all_partitions = [subgraph for subgraph, _, _ in partitions]  # Update the list comprehension
    combined_lattice = combine_partitions_parallel(all_partitions)
    end_time = time.time()  # Record the end time
    total_time = end_time - start_time
    print(f"Lattice formation time: {total_time:.9f} seconds.")
    print(f"Combined lattice has {len(combined_lattice.nodes)} nodes.")

    print(f"\nMaximum time taken by any resource: {max_time_taken:.9f}")