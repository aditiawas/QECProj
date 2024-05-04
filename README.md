# Surface Code Lattice Partitioning and Processing

This code provides functionality for partitioning a surface code lattice into subgraphs, assigning tasks to resources based on complexity, and processing the tasks using different scheduling algorithms.

## Table of Contents
1. [Dependencies](#dependencies)
2. [Classes](#classes)
   - [Resource](#resource)
   - [Partition](#partition)
3. [Functions](#functions)
   - [partition_lattice](#partition_lattice)
   - [analyze_complexity_distribution](#analyze_complexity_distribution)
   - [combine_partitions](#combine_partitions)
   - [combine_partitions_parallel](#combine_partitions_parallel)
   - [dynamic_load_balancing](#dynamic_load_balancing)
   - [least_loaded](#least_loaded)
   - [round_robin_schedule](#round_robin_schedule)
   - [shortest_job_first](#shortest_job_first)
   - [hierarchical_schedule](#hierarchical_schedule)
   - [process_queue_wrapper](#process_queue_wrapper)
4. [Main Execution](#main-execution)

## Dependencies

The code relies on the following dependencies:
- `networkx`: For creating and manipulating graphs.
- `random`: For generating random complexity values.
- `time`: For simulating processing time.
- `multiprocessing`: For parallel processing of tasks.
- `argparse`: For parsing command-line arguments.
- `collections.deque`: For efficient queue operations.

## Classes

### Resource

The `Resource` class represents a resource that can process tasks. It has the following attributes:
- `id`: The unique identifier of the resource.
- `max_complexity`: The maximum complexity the resource can handle.
- `type`: The type of the resource (e.g., 'high' or 'low').
- `load`: The current load on the resource.
- `queue`: A deque of tasks assigned to the resource.
- `processing_time`: The total processing time of tasks by the resource.
- `start_time`: The start time of processing tasks.

The `Resource` class provides the following methods:
- `can_handle(complexity)`: Checks if the resource can handle a given complexity.
- `assign_task(task)`: Assigns a task to the resource's queue.
- `process_task(task)`: Processes a task based on its complexity and the resource's type.
- `process_queue()`: Processes all tasks in the resource's queue.

### Partition

The `Partition` class represents a partition of the surface code lattice. It has the following attributes:
- `nodes`: The nodes of the subgraph representing the partition.
- `complexity`: The complexity of the partition.

## Functions

### partition_lattice

```python
def partition_lattice(lattice, num_partitions):
    """
    Partition the given surface code lattice into num_partitions subgraphs.
    
    Args:
        lattice (nx.Graph): The surface code lattice graph.
        num_partitions (int): The number of partitions to create.
        
    Returns:
        list: A list of subgraphs representing the partitions along with their complexity.
    """
```

This function partitions the given surface code lattice into `num_partitions` subgraphs. It assigns nodes to partitions in a round-robin fashion and creates subgraphs from the node lists. It also calculates the complexity of each partition based on the maximum number of edges in a complete subgraph.

### analyze_complexity_distribution

```python
def analyze_complexity_distribution(complexities, target_percentage=0.8):
    """
    Analyze the distribution of partition complexities and identify the value `X`
    where `target_percentage` (e.g., 80% or 90%) of partitions have a complexity less than or equal to `X`.

    Args:
        complexities (list): A list of partition complexities.
        target_percentage (float): The target percentage of partitions to consider (default: 0.8 or 80%).

    Returns:
        int: The value `X` where `target_percentage` of partitions have a complexity less than or equal to `X`.
    """
```

This function analyzes the distribution of partition complexities and identifies the value `X` where `target_percentage` (default: 80%) of partitions have a complexity less than or equal to `X`. It sorts the complexities in ascending order and returns the complexity at the target index.

### combine_partitions

```python
def combine_partitions(subgraph1, subgraph2):
    """
    Combine two subgraphs by merging their nodes and edges.

    Args:
        subgraph1 (nx.Graph): The first subgraph.
        subgraph2 (nx.Graph): The second subgraph.

    Returns:
        nx.Graph: The combined subgraph.
    """
```

This function combines two subgraphs by merging their nodes and edges. It creates a new graph and adds the nodes and edges from both subgraphs to the combined graph. It also simulates processing time proportional to the number of boundary nodes between the subgraphs.

### combine_partitions_parallel

```python
def combine_partitions_parallel(subgraphs):
    """
    Combine all subgraphs in parallel by combining pairs of subgraphs using a pool of workers.

    Args:
        subgraphs (list): A list of subgraphs to be combined.

    Returns:
        nx.Graph: The combined subgraph.
    """
```

This function combines all subgraphs in parallel by combining pairs of subgraphs using a pool of workers. It iteratively combines pairs of subgraphs until only one subgraph remains, which represents the combined lattice.

### dynamic_load_balancing

```python
def dynamic_load_balancing(partitions, high_complexity_resources, low_complexity_resources):
```

This function performs dynamic load balancing by assigning partitions to resources based on their complexity. It first assigns high-complexity partitions to high-complexity resources, and then assigns the remaining partitions to available resources based on their load. It returns a list of combined resources.

### least_loaded

```python
def least_loaded(partitions, resources, max_complexity):
```

This function assigns partitions to the least loaded compatible resource. It iterates over the partitions and finds the least loaded resource that can handle the partition's complexity. It assigns the partition to the resource's queue and updates the resource's load.

### round_robin_schedule

```python
def round_robin_schedule(partitions, num_resources):
```

This function schedules partitions using a round-robin approach. It creates a specified number of resources and assigns partitions to resources in a round-robin manner. It processes the tasks in each resource's queue and returns the list of resources.

### shortest_job_first

```python
def shortest_job_first(partitions, num_resources):
```

This function schedules partitions using the shortest job first approach. It creates a specified number of resources and assigns partitions to the least loaded resource based on their complexity. It processes each task immediately after assignment and returns the list of resources.

### hierarchical_schedule

```python
def hierarchical_schedule(partitions, high_complexity_resources, low_complexity_resources, complexity_threshold):
```

This function performs hierarchical scheduling of partitions. It assigns high-complexity partitions to high-complexity resources, low-complexity partitions to low-complexity resources, and any remaining unassigned partitions to any available resource. It processes the tasks in each resource's queue and returns the lists of high-complexity and low-complexity resources.

### process_queue_wrapper

```python
def process_queue_wrapper(resource):
```

This function is a wrapper for the `process_queue` method of the `Resource` class. It is used for parallel processing of tasks using multiprocessing.

## Main Execution

The main execution of the code performs the following steps:
1. Parses command-line arguments for the size of the lattice grid, number of partitions, number of high-complexity resources, and number of low-complexity resources.
2. Creates a sample lattice using the specified grid size.
3. Partitions the lattice into subgraphs with random complexity.
4. Analyzes the distribution of partition complexities and identifies the value `X` where 90% of partitions have a complexity less than or equal to `X`.
5. Creates high-complexity and low-complexity resources.
6. Performs dynamic load balancing and schedules partitions to resources.
7. Processes queues in parallel using multiprocessing.
8. Prints which partition was processed on which resource.
9. Combines all partitions in parallel to form the combined lattice.
10. Prints the number of nodes in the combined lattice and the total time taken for execution.

The main execution provides an example of how to use the various functions and classes defined in the code for partitioning a surface code lattice, assigning tasks to resources, and processing the tasks using different scheduling algorithms.
