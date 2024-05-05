# Resource-Constrained Surface Code Decoding: Analysis and Optimization Strategies

## Overview
This code implements a system for partitioning a surface code lattice into subgraphs, assigning these subgraphs to decoding units (resources) based on their complexity (number of nodes in syndrome graph), and processing the syndrome graphs in parallel. The system utilizes a dynamic load balancing approach to distribute the decosding of partitions among high-complexity-handling units and low-complexity-handling units efficiently.

## Main Script (`main.py`)

### Functions

1. `spatial_hash(node_position, grid_size, lattice_size, num_partitions)`
   - Calculates the spatial hash value for a given node position based on the grid size, lattice size, and the number of partitions.
   - Returns the partition index for the node.

2. `partition_lattice(lattice, num_partitions)`
   - Partitions the input lattice into subgraphs using the spatial hash function.
   - Adjusts the grid size dynamically to ensure all partitions are non-empty.
   - Calculates the complexity of each subgraph based on the physical error rate.
   - Handles shared nodes between partitions by adding them to both subgraphs.
   - Returns a list of tuples containing each subgraph, its complexity, and partition index.

3. `combine_partitions(subgraph1, subgraph2)`
   - Combines two subgraphs into a single graph.
   - Adds nodes and edges from both subgraphs to the combined graph.
   - Returns the combined graph.

4. `combine_partitions_parallel(subgraphs)`
   - Combines all subgraphs in parallel by combining pairs of subgraphs using a pool of workers.
   - Recursively combines subgraphs until only one subgraph remains.
   - Returns the final combined subgraph.

### Main Execution

1. Parse command-line arguments:
   - `--size`: Size of the lattice grid (rows, cols). Default: [5, 5].
   - `--partitions`: Number of partitions to create. Default: 8.
   - `--num_hr`: Number of high-complexity resources. Default: 2.
   - `--num_lr`: Number of low-complexity resources. Default: 3.
   - `--thresh_compl`: Number of low-complexity resources. Default: 2.

2. Create a sample lattice using the specified size.

3. Partition the lattice into subgraphs with random complexity using `partition_lattice()`.

4. Create high-complexity and low-complexity resources based on the command-line arguments.

5. Perform dynamic load balancing and schedule partitions sequentially using `dynamic_load_balancing()`.

6. Print the scheduling overhead.

7. Print all partitions and their associated complexities.

8. Estimate processing times for each resource in parallel.

9. Generate a Gantt chart to visualize the partition execution timeline.

10. Combine all partitions in parallel using `combine_partitions_parallel()`.

11. Print the lattice formation time and the number of nodes in the combined lattice.

12. Print the maximum time taken by any resource.

## Resource Class (`Resource.py`)

### Class: `Resource`

#### Attributes
- `id`: Unique identifier for the resource.
- `max_complexity`: Maximum complexity the resource can handle.
- `type`: Type of the resource ('high' or 'low').
- `load`: Current load on the resource.
- `queue`: Queue of tasks assigned to the resource.
- `processing_time`: Total processing time of tasks assigned to the resource.
- `start_time`: Start time of task processing.
- `tasks`: List of tasks assigned to the resource.
- `utilization_time`: Total utilization time of the resource.
- `max_time_taken`: Maximum time taken by the resource.
- `processed_tasks`: Set of tasks already processed by the resource.

#### Methods
- `can_handle(complexity)`: Checks if the resource can handle a given complexity.
- `assign_task(task)`: Assigns a task to the resource's queue and updates the load.
- `estimate_processing_time(task)`: Estimates the processing time for a task based on its complexity and the resource type.
- `process_queue()`: Processes the tasks in the resource's queue and returns the processed tasks and their processing times.

### Functions

1. `dynamic_load_balancing(partitions, high_complexity_resources, low_complexity_resources)`
   - Sorts partitions by complexity in descending order.
   - Assigns high-complexity partitions to high-complexity resources using `least_loaded()`.
   - Assigns remaining partitions to available resources based on load using `least_loaded()`.
   - Returns the combined list of resources.

2. `least_loaded(partitions, resources, max_complexity)`
   - Assigns partitions to the least loaded compatible resource.
   - Skips partitions that cannot be handled by any resource.
   - Returns the updated list of resources.

## Partition Class (`Resource.py`)

### Class: `Partition`

#### Attributes
- `nodes`: Nodes in the partition subgraph.
- `complexity`: Complexity of the partition.
- `partition_index`: Index of the partition.

#### Methods
- `__len__()`: Returns the number of nodes in the partition.

## Usage

1. Run the main script with the desired command-line arguments:
   ```
   python main.py --size 5 5 --partitions 8 --num_hr 2 --num_lr 3 --thresh_compl 2
   ```

2. The script will partition the lattice, assign partitions to resources, and process the partitions in parallel.

3. The output will include:
   - All partitions and their associated complexities.
   - Scheduling overhead.
   - Estimated processing times for each resource.
   - Gantt chart visualizing the partition execution timeline.
   - Lattice formation time and the number of nodes in the combined lattice.
   - Maximum time taken by any resource.

## Dependencies
- `networkx`: Graph library for creating and manipulating the lattice graph.
- `random`: Library for generating random numbers.
- `multiprocessing`: Library for parallel processing.
- `argparse`: Library for parsing command-line arguments.
- `math`: Library for mathematical operations.
- `time`: Library for measuring execution time.
- `matplotlib`: Library for generating the Gantt chart.
- `numpy`: Library for numerical operations.
- `Resource`: Custom module containing the `Resource` and `Partition` classes.
