import networkx as nx
from collections import deque
import time

class Resource:
    def __init__(self, id, max_complexity, type):
        self.id = id
        self.max_complexity = max_complexity
        self.type = type
        self.load = 0
        self.queue = deque()
        self.processing_time = 0
        self.start_time = None

    def can_handle(self, complexity):
        return complexity <= self.max_complexity

    def assign_task(self, task):
        self.queue.append(task)
        self.load += task.complexity

    def process_task(self, task):
        n = len(task.nodes)
        if self.type == 'high':
            if task.complexity <= self.max_complexity:
                processing_time = n ** 3  # O(n^3) complexity for high-complexity resources
            else:
                processing_time = n ** 4  # Higher complexity for low-complexity partitions on high-complexity resources
        else:
            processing_time = n ** 2  # O(n^2) complexity for low-complexity resources

        # Simulate processing time
        time.sleep(processing_time / 1000000)  # Divide by 1000000 to reduce actual waiting time
        self.processing_time += processing_time

    def process_queue(self):
        self.start_time = time.time()  # Record the start time
        while self.queue:
            task = self.queue.popleft()
            self.process_task(task)
        total_time = time.time() - self.start_time  # Calculate the total time taken
        print(f"Resource {self.id} ({self.type}) took {total_time:.6f} seconds to process all tasks.")

    def __repr__(self):
        return f"Resource {self.id} ({self.type}, load={self.load}, processing_time={self.processing_time})"

def partition_lattice(lattice, num_partitions):
    """
    Partition the given surface code lattice into num_partitions subgraphs.
    
    Args:
        lattice (nx.Graph): The surface code lattice graph.
        num_partitions (int): The number of partitions to create.
        
    Returns:
        list: A list of subgraphs representing the partitions along with their complexity.
    """
    # Get the number of nodes in the lattice
    num_nodes = len(lattice.nodes)
    
    # Calculate the number of nodes per partition
    nodes_per_partition = num_nodes // num_partitions
    
    # Create a list of node lists, one for each partition
    partitions = [[] for _ in range(num_partitions)]
    
    # Assign nodes to partitions in a round-robin fashion
    for i, node in enumerate(lattice.nodes):
        partition_index = i // nodes_per_partition
        partitions[partition_index].append(node)
    
    # Create subgraphs from the node lists and calculate their complexity
    subgraphs = []
    for nodes in partitions:
        subgraph = lattice.subgraph(nodes)
        n = len(nodes)
        complexity = n * (n - 1) // 2  # Maximum number of edges in a complete subgraph
        subgraphs.append((subgraph, complexity))
    
    return subgraphs

def dynamic_load_balancing(partitions, high_complexity_resources, low_complexity_resources):
    # Sort partitions by complexity in descending order
    partitions.sort(key=lambda x: x[1], reverse=True)

    # Assign high-complexity partitions to high-complexity resources
    high_complexity_partitions = [(partition, complexity) for partition, complexity in partitions
                                  if complexity > low_complexity_resources[0].max_complexity]
    high_resources = least_loaded(high_complexity_partitions, high_complexity_resources, max_complexity=float('inf'))

    # Assign remaining partitions to available resources
    remaining_partitions = [(partition, complexity) for partition, complexity in partitions
                            if (partition, complexity) not in high_resources[0].queue]
    all_resources = high_resources + low_complexity_resources

    # Distribute remaining partitions based on load
    remaining_resources = least_loaded(remaining_partitions, all_resources, max_complexity=float('inf'))

    # Combine high-complexity and remaining resources
    combined_resources = high_resources + remaining_resources
    return combined_resources

def least_loaded(partitions, resources, max_complexity):
    for partition, complexity in partitions:
        compatible_resources = [r for r in resources if r.can_handle(complexity)]
        if not compatible_resources:
            continue  # Skip partitions that cannot be handled by any resource

        least_loaded = min(compatible_resources, key=lambda r: r.load)
        least_loaded.assign_task(Partition(partition, complexity))
        least_loaded.process_task(Partition(partition, complexity))  # Process the assigned task

    return resources

def round_robin_schedule(partitions, num_resources):
    resources = [Resource(i, max_complexity=float('inf'), type='high') for i in range(num_resources)]
    resource_index = 0

    for partition, complexity in partitions:
        resources[resource_index].assign_task(Partition(partition, complexity))
        resource_index = (resource_index + 1) % num_resources

    print("\nRound-Robin Scheduling:")
    for resource in resources:
        resource.process_queue()

    return resources

def shortest_job_first(partitions, num_resources):
    resources = [Resource(i, max_complexity=float('inf'), type='high') for i in range(num_resources)]
    partitions = sorted(partitions, key=lambda p: p[1])  # Sort by complexity

    for partition, complexity in partitions:
        least_loaded = min(resources, key=lambda r: r.load)
        least_loaded.assign_task(Partition(partition, complexity))
        least_loaded.process_task(Partition(partition, complexity))

    print("\nShortest Job First Scheduling:")
    for resource in resources:
        resource.process_queue()

    return resources

def hierarchical_schedule(partitions, high_complexity_resources, low_complexity_resources, complexity_threshold):
    # Sort partitions by complexity in descending order
    partitions.sort(key=lambda x: x[1], reverse=True)

    # Schedule high-complexity partitions to high-complexity resources
    high_complexity_partitions = [(partition, complexity) for partition, complexity in partitions if complexity > complexity_threshold]
    high_resources = least_loaded(high_complexity_partitions, high_complexity_resources, max_complexity=float('inf'))

    # Schedule remaining partitions to low-complexity resources
    low_complexity_partitions = [(partition, complexity) for partition, complexity in partitions if complexity <= complexity_threshold]
    low_resources = least_loaded(low_complexity_partitions, low_complexity_resources, max_complexity=complexity_threshold)

    # Assign unassigned partitions to any available resource
    unassigned_partitions = [(partition, complexity) for partition, complexity in partitions if not any(partition in r.queue for r in high_resources + low_resources)]
    all_resources = high_resources + low_resources
    least_loaded(unassigned_partitions, all_resources, max_complexity=float('inf'))

    print("\nHigh-Complexity Resources:")
    for resource in high_resources:
        resource.process_queue()

    print("\nLow-Complexity Resources:")
    for resource in low_resources:
        resource.process_queue()

    return high_resources, low_resources

def process_queue_wrapper(resource):
    resource.process_queue()

class Partition:
    def __init__(self, subgraph, complexity):
        self.nodes = subgraph.nodes
        self.complexity = complexity

    def __len__(self):
        return len(self.nodes)