# Resource-Constrained Surface Code Decoding: Analysis and Optimization Strategies

A good command to run:
```
   python3 main.py --size 100 100 --partitions 10 --thresh_compl 3 --time_limit 0.00000005
```

This project implements a system for partitioning and processing a surface code lattice using high-complexity and low-complexity resources. The system aims to optimize the scheduling and processing of partitions to maximize accuracy and minimize latency.

## Table of Contents

1. [Features](#features)
2. [Installation](#installation)
3. [Usage](#usage)
4. [Code Structure](#code-structure)
   - [simulate.py](#simulate.py)
   - [Resource.py](#resource.py)
   - [Experiments.py](#experiments.py)
5. [Algorithms and Techniques](#algorithms-and-techniques)
   - [Spatial Hash Partitioning](#spatial-hash-partitioning)
   - [Dynamic Load Balancing](#dynamic-load-balancing)
   - [Parallel Partition Combination](#parallel-partition-combination)
6. [Experimental Analysis](#experimental-analysis)
   - [Lattice Size vs Maximum Time Taken](#lattice-size-vs-maximum-time-taken)
   - [Number of Partitions vs Net Accuracy and Maximum Time Taken](#number-of-partitions-vs-net-accuracy-and-maximum-time-taken)
   - [Resource Configuration vs Maximum Time Taken and Accuracy](#resource-configuration-vs-maximum-time-taken-and-accuracy)
   - [Threshold for Low-Complexity Resources vs Latency](#threshold-for-low-complexity-resources-vs-latency)
   - [Time Limit vs Maximum Time Taken](#time-limit-vs-maximum-time-taken)
7. [License](#license)

## Features

- Partitioning of a surface code lattice using spatial hash partitioning
- Dynamic load balancing for scheduling partitions to high-complexity and low-complexity resources
- Parallel combination of partitions to form the final lattice
- Estimation of processing times and accuracies for each partition
- Gantt chart visualization of partition execution
- Experimental analysis of various system parameters and their impact on performance

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/aditiawas/QECProj.git
   ```
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Run the `simulate.py` script with the desired command-line arguments (all of them are optional):
   ```
   python3 simulate.py --size 100 100 --partitions 8 --num_hr 2 --num_lr 3 --thresh_compl 3 --time_limit 0.00000005
   ```
   - `--size`: Size of the lattice grid (rows, cols)
   - `--partitions`: Number of partitions to create
   - `--num_hr`: Number of high-complexity resources
   - `--num_lr`: Number of low-complexity resources
   - `--thresh_compl`: Threshold for low-complexity resources
   - `--time_limit`: Time limit for running the partitions (in seconds)

2. Run the `Experiments.py` script to perform experimental analysis:
   ```
   python3 Experiments.py
   ```

## Code Structure

### simulate.py

This file contains the main simulation code for partitioning and processing the surface code lattice. It includes functions for:
- Parsing command-line arguments
- Creating the lattice and partitioning it using spatial hash partitioning
- Creating high-complexity and low-complexity resources
- Scheduling partitions to resources using dynamic load balancing
- Processing partitions and estimating their processing times and accuracies
- Combining partitions in parallel to form the final lattice
- Generating a Gantt chart visualization of partition execution

### Resource.py

This file defines the `Resource` class, which represents a processing resource (either high-complexity or low-complexity). It includes methods for:
- Assigning tasks (partitions) to the resource
- Estimating the processing time for a task
- Processing the assigned tasks and updating the resource's utilization time

### Experiments.py

This file contains functions for performing experimental analysis on the surface code lattice partitioning and processing system. It includes experiments for:
- Lattice size vs maximum time taken
- Number of partitions vs net accuracy and maximum time taken
- Resource configuration (number of high-complexity and low-complexity resources) vs maximum time taken and accuracy
- Threshold for low-complexity resources vs latency
- Time limit vs maximum time taken

## Algorithms and Techniques

### Spatial Hash Partitioning

The spatial hash partitioning algorithm is used to divide the surface code lattice into smaller partitions. It works by:
1. Defining a grid size based on the desired number of partitions and the lattice size.
2. Assigning each node in the lattice to a partition based on its spatial coordinates and the grid size.
3. Ensuring that neighboring nodes are assigned to the same partition to maintain locality.

### Dynamic Load Balancing

The dynamic load balancing algorithm is used to schedule partitions to high-complexity and low-complexity resources. It works by:
1. Sorting the partitions by complexity in descending order.
2. Assigning high-complexity partitions to high-complexity resources using the least-loaded approach.
3. Assigning the remaining partitions to available low-complexity resources using the least-loaded approach.

### Parallel Partition Combination

The parallel partition combination algorithm is used to combine the processed partitions into the final lattice. It works by:
1. Combining pairs of partitions in parallel using a pool of worker processes.
2. Merging the subgraphs of the partitions and removing duplicate nodes.
3. Calculating the total boundary nodes and latency during the combination process.

## Experimental Analysis

The `Experiments.py` script performs various experiments to analyze the performance of the surface code lattice partitioning and processing system. The experiments include:

### Lattice Size vs Maximum Time Taken

This experiment investigates the relationship between the lattice size and the maximum time taken by any resource to process the partitions. It varies the lattice size while keeping other parameters fixed and plots the results.

### Number of Partitions vs Net Accuracy and Maximum Time Taken

This experiment explores the impact of the number of partitions on the net accuracy and maximum time taken. It varies the number of partitions while keeping other parameters fixed and plots the results.

### Resource Configuration vs Maximum Time Taken and Accuracy

This experiment analyzes the effect of different resource configurations (number of high-complexity and low-complexity resources) on the maximum time taken and accuracy. It varies the number of high-complexity and low-complexity resources and creates scatter plots to visualize the results.

### Threshold for Low-Complexity Resources vs Latency

This experiment examines the relationship between the threshold for low-complexity resources and the latency. It varies the threshold value while keeping other parameters fixed and plots the results.

### Time Limit vs Maximum Time Taken

This experiment investigates the impact of the time limit on the maximum time taken by any resource. It varies the time limit and plots the maximum time taken, indicating whether the time limit was exceeded or not.

## License

This project is licensed under the [MIT License](LICENSE).