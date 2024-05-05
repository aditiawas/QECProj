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

    partitions = [[] for _ in range(num_partitions)]

    # Start with an initial grid size
    grid_size = lattice_size / math.sqrt(num_partitions)

    for node in lattice.nodes:
        row, col = node
        node_position = (row, col)
        partition_index = spatial_hash(node_position, grid_size, lattice_size, num_partitions)

        # Add the current node to the partition
        partitions[partition_index].append(node)

        # Add neighboring nodes to the same partition
        neighbors = [(row - 1, col), (row + 1, col), (row, col - 1), (row, col + 1)]
        for neighbor in neighbors:
            if neighbor in lattice.nodes:
                neighbor_partition_index = spatial_hash((neighbor[0], neighbor[1]), grid_size, lattice_size, num_partitions)
                if neighbor_partition_index != partition_index:
                    partitions[neighbor_partition_index].append(node)

    # Create subgraphs from the partitions
    subgraphs = []
    partition_index = 0
    for nodes in partitions:
        subgraph = lattice.subgraph(set(nodes))
        n = len(nodes)

        # Calculate the number of activated nodes based on the physical error rate
        num_error_nodes = sum(random.random() <= 0.001 for _ in range(n))

        # Set the complexity equal to the number of activated nodes
        complexity = num_error_nodes + 1

        subgraphs.append((subgraph, complexity, partition_index))
        partition_index += 1

    return subgraphs

def combine_partitions(subgraph1, subgraph2, original_lattice):
    combined_nodes = set(subgraph1.nodes) | set(subgraph2.nodes)
    combined_graph = original_lattice.subgraph(combined_nodes)

    # Remove duplicate nodes and count shared nodes
    node_positions = set()
    nodes_to_remove = set()
    for node in combined_graph.nodes():
        if node in node_positions:
            nodes_to_remove.add(node)
        else:
            node_positions.add(node)

    # Remove duplicate nodes from the combined graph
    for node in nodes_to_remove:
        combined_graph.remove_node(node)

    # Calculate the total number of boundary nodes in both subgraphs
    boundary_nodes_subgraph1 = set()
    boundary_nodes_subgraph2 = set()

    for node in subgraph1.nodes:
        row, col = node
        neighbors = [(row - 1, col), (row + 1, col), (row, col - 1), (row, col + 1)]
        for neighbor in neighbors:
            if neighbor not in subgraph1.nodes and neighbor in original_lattice.nodes:
                boundary_nodes_subgraph1.add(node)

    for node in subgraph2.nodes:
        row, col = node
        neighbors = [(row - 1, col), (row + 1, col), (row, col - 1), (row, col + 1)]
        for neighbor in neighbors:
            if neighbor not in subgraph2.nodes and neighbor in original_lattice.nodes:
                boundary_nodes_subgraph2.add(node)

    total_boundary_nodes = (len(boundary_nodes_subgraph1) + len(boundary_nodes_subgraph2))/10

    # Calculate latency based on the total number of boundary nodes
    latency = total_boundary_nodes * (10 ** -10)

    return combined_graph, latency

def combine_partitions_parallel(subgraphs, original_lattice):
    """
    Combine all subgraphs in parallel by combining pairs of subgraphs using a pool of workers.

    Args:
        subgraphs (list): A list of subgraphs to be combined.
        original_lattice (nx.Graph): The original lattice graph.

    Returns:
        tuple: A tuple containing the combined subgraph and the total latency.
    """
    total_latency = 0

    with multiprocessing.Pool() as pool:
        while len(subgraphs) > 1:
            if len(subgraphs) % 2 != 0:
                # If there is an odd number of subgraphs, combine the last subgraph with the second-to-last subgraph
                subgraph, latency = combine_partitions(subgraphs[-2], subgraphs[-1], original_lattice)
                subgraphs[-2] = subgraph
                total_latency += latency
                subgraphs.pop()

            pairs = [(subgraphs[i], subgraphs[i + 1], original_lattice) for i in range(0, len(subgraphs), 2)]
            results = pool.starmap(combine_partitions, pairs)

            subgraphs = [result[0] for result in results]
            total_latency += sum(result[1] for result in results)

    return subgraphs[0], total_latency

def parse_arguments(args_list=None):
    parser = argparse.ArgumentParser(description="Surface code lattice partitioning and processing.")
    parser.add_argument("--size", type=int, nargs=2, default=[5, 5], help="Size of the lattice grid (rows, cols)")
    parser.add_argument("--partitions", type=int, default=8, help="Number of partitions to create")
    parser.add_argument("--num_hr", type=int, default=2, help="Number of high-complexity resources")
    parser.add_argument("--num_lr", type=int, default=3, help="Number of low-complexity resources")
    parser.add_argument("--thresh_compl", type=int, default=2, help="Number of low-complexity resources")
    parser.add_argument("--time_limit", type=float, default=float('inf'), help="Time limit for running the partitions (in seconds)")

    if args_list:
        args = parser.parse_args(args_list)
    else:
        args = parser.parse_args()

    return args

def create_resources(args):
    high_complexity_resources = [Resource(i, max_complexity=float('inf'), type='high') for i in range(args.num_hr)]
    low_complexity_resources = [Resource(i + args.num_hr, max_complexity=args.thresh_compl, type='low') for i in range(args.num_lr)]
    return high_complexity_resources, low_complexity_resources

def print_partition_details(partitions):
    print("\nAll Partitions:")
    for subgraph, complexity, partition_index in partitions:
        print(f"Partition {partition_index}: Complexity = {complexity}")

def schedule_partitions(partitions, high_complexity_resources, low_complexity_resources):
    start_time = time.time()
    combined_resources = dynamic_load_balancing(partitions, high_complexity_resources, low_complexity_resources)
    end_time = time.time()
    scheduling_overhead = end_time - start_time
    return combined_resources, scheduling_overhead

def process_partitions(combined_resources):
    max_time_taken = 0
    total_accuracy = 0

    print("\nPartition Processing:")
    for resource in combined_resources:
        processed_tasks = resource.process_queue()
        resource_processing_time = resource.utilization_time
        print(f"Resource {resource.id} ({resource.type}) estimated processing time: {resource_processing_time:.10f}")
        max_time_taken = max(max_time_taken, resource_processing_time)
        for task, processing_time, accuracy in processed_tasks:
            print(f"Resource {resource.id} ({resource.type}) processing Partition {task.partition_index}")
            print(f"  Partition {task.partition_index} with {len(task.nodes)} nodes (syndrome graph size {task.complexity})")
            print(f"  Accuracy: {accuracy}%")
            total_accuracy += accuracy
        print("\n")

    return max_time_taken, total_accuracy

def check_time_limit(args, max_time_taken, combined_resources):
    if max_time_taken > args.time_limit:
        print(f"Total time exceeds the specified time limit of {args.time_limit:.10f} seconds.")
        exceeded_resources = [resource for resource in combined_resources if resource.utilization_time > args.time_limit]
        if exceeded_resources:
            print("Resources that exceeded the time limit:")
            for resource in exceeded_resources:
                print(f"Resource {resource.id} ({resource.type}) took {resource.utilization_time:.10f} seconds")
        else:
            print("No resource exceeded the time limit individually, but the maximum processing time exceeds the limit.")
    else:
        print("All partitions processed within the specified time limit.")

def calculate_net_accuracy(total_accuracy, num_partitions):
    net_accuracy = total_accuracy / num_partitions
    print(f"\nNet accuracy across all partitions: {net_accuracy:.2f}%")
    return net_accuracy

def generate_gantt_chart(combined_resources, partitions, args):
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

    # Add vertical line at time limit if not infinity
    if args.time_limit != float('inf'):
        ax.axvline(x=args.time_limit, linestyle='--', color='r', label='Time Limit')
        ax.legend()

    plt.tight_layout()
    plt.show()

def main_func(args):
    # Create a sample lattice
    lattice = nx.grid_2d_graph(args.size[0], args.size[1])

    partitions = partition_lattice(lattice, args.partitions)
     
    # Add partition index to each partition
    for i, (subgraph, complexity, partition_index) in enumerate(partitions):
        partitions[i] = (subgraph, complexity, partition_index)

    print_partition_details(partitions)

    high_complexity_resources, low_complexity_resources = create_resources(args)

    combined_resources, scheduling_overhead = schedule_partitions(partitions, high_complexity_resources, low_complexity_resources)
    print(f"\nScheduling overhead on this system: {scheduling_overhead:.10f} seconds.")

    max_time_taken, total_accuracy = process_partitions(combined_resources)
    print(f"Maximum time taken by any resource: {max_time_taken:.10f}")
    
    # Combine all partitions in parallel
    all_partitions = [subgraph for subgraph, _, _ in partitions]
    combined_lattice, comb_latency = combine_partitions_parallel(all_partitions, lattice)
    print(f"Combined lattice has {len(combined_lattice.nodes)} nodes.")
    print(f"Total latency during partition combination: {comb_latency:.10f} seconds.")

    max_time_taken += comb_latency
    print(f"Total time: {max_time_taken:.10f}")

    check_time_limit(args, max_time_taken, combined_resources) #TODO factor in combine latency here

    net_accuracy = calculate_net_accuracy(total_accuracy, args.partitions)

    return (combined_resources, partitions, args, max_time_taken, net_accuracy)

if __name__ == "__main__":
    args = parse_arguments()
    combined_resources, partitions, args, max_time_taken, net_accuracy = main_func(args)
    generate_gantt_chart(combined_resources, partitions, args)