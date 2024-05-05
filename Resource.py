from collections import deque

class Resource:
    def __init__(self, id, max_complexity, type):
        self.id = id
        self.max_complexity = max_complexity
        self.type = type
        self.load = 0
        self.queue = deque()
        self.processing_time = 0
        self.start_time = None
        self.tasks =[]
        self.utilization_time = 0  # New attribute to store the utilization time
        self.max_time_taken = 0  # New attribute to store the maximum time taken
        self.processed_tasks = set()  # Add a set to keep track of processed tasks
        self.processing_times = []  # Store processing times for each task

    def can_handle(self, complexity):
        return complexity <= self.max_complexity

    def assign_task(self, task):
        self.queue.append(task)
        self.load += task.complexity

    def estimate_processing_time(self, task):
        if self.type == 'high':
            if task.complexity <= self.max_complexity:
                processing_time = (task.complexity ** 3) * (10 ** -9)  # O(n^3) complexity for high-complexity resources (MWPM)
        else:
            processing_time = (2 * task.complexity) * (10 ** -9)  # O(2n) complexity for low-complexity resources (Union Find)

        self.processing_times.append(processing_time)
        return processing_time

    def process_queue(self):
        start_time = 0
        processed_tasks = []
        for task in self.queue:
            if task not in self.processed_tasks:  # Check if the task has already been processed
                processing_time = self.estimate_processing_time(task)
                end_time = start_time + processing_time
                self.tasks.append((start_time, end_time, task))
                start_time = end_time
                accuracy = task.accuracy
                if self.type == 'low':
                    accuracy -= 5  # Reduce accuracy by 5% if processed by a low-complexity resource
                processed_tasks.append((task, processing_time, accuracy))
                self.processed_tasks.add(task)  # Mark the task as processed

        self.utilization_time = sum(self.processing_times)
        return processed_tasks

def dynamic_load_balancing(partitions, high_complexity_resources, low_complexity_resources):
    # Sort partitions by complexity in descending order
    partitions.sort(key=lambda x: x[1], reverse=True)

    # Assign high-complexity partitions to high-complexity resources
    high_complexity_partitions = [(partition, complexity, partition_index) for partition, complexity, partition_index in partitions
                                  if complexity > low_complexity_resources[0].max_complexity]
    high_resources = least_loaded(high_complexity_partitions, high_complexity_resources, max_complexity=float('inf'))

    # Assign remaining partitions to available low-complexity resources
    remaining_partitions = [(partition, complexity, partition_index) for partition, complexity, partition_index in partitions
                            if (partition, complexity, partition_index) not in [task for resource in high_resources for task in resource.queue]]
    remaining_resources = least_loaded(remaining_partitions, low_complexity_resources, max_complexity=low_complexity_resources[0].max_complexity)

    # Combine high-complexity and remaining resources
    combined_resources = high_resources + remaining_resources
    return combined_resources

def least_loaded(partitions, resources, max_complexity):
    # Sort partitions by complexity in ascending order (shortest job first)
    partitions.sort(key=lambda x: x[1])

    for partition, complexity, partition_index in partitions:
        compatible_resources = [r for r in resources if r.can_handle(complexity)]
        if not compatible_resources:
            continue  # Skip partitions that cannot be handled by any resource

        # Find the least loaded resource among compatible resources
        least_loaded = min(compatible_resources, key=lambda r: r.load)

        # If there are multiple least loaded resources, choose the one with the smallest queue
        if sum(r.load == least_loaded.load for r in compatible_resources) > 1:
            least_loaded = min(compatible_resources, key=lambda r: (r.load, len(r.queue)))

        least_loaded.assign_task(Partition(partition, complexity, partition_index))

    return resources

# def hierarchical_schedule(partitions, high_complexity_resources, low_complexity_resources, complexity_threshold):
#     # Sort partitions by complexity in descending order
#     partitions.sort(key=lambda x: x[1], reverse=True)

#     # Schedule high-complexity partitions to high-complexity resources
#     high_complexity_partitions = [(partition, complexity) for partition, complexity in partitions if complexity > complexity_threshold]
#     high_resources = least_loaded(high_complexity_partitions, high_complexity_resources, max_complexity=float('inf'))

#     # Schedule remaining partitions to low-complexity resources
#     low_complexity_partitions = [(partition, complexity) for partition, complexity in partitions if complexity <= complexity_threshold]
#     low_resources = least_loaded(low_complexity_partitions, low_complexity_resources, max_complexity=complexity_threshold)

#     # Assign unassigned partitions to any available resource
#     unassigned_partitions = [(partition, complexity) for partition, complexity in partitions if not any(partition in r.queue for r in high_resources + low_resources)]
#     all_resources = high_resources + low_resources
#     least_loaded(unassigned_partitions, all_resources, max_complexity=float('inf'))

#     print("\nHigh-Complexity Resources:")
#     for resource in high_resources:
#         resource.process_queue()

#     print("\nLow-Complexity Resources:")
#     for resource in low_resources:
#         resource.process_queue()

#     return high_resources, low_resources

class Partition:
    def __init__(self, subgraph, complexity, partition_index):
        self.nodes = subgraph.nodes
        self.complexity = complexity
        self.partition_index = partition_index
        self.accuracy = 100  # Initialize accuracy to 100%

    def __len__(self):
        return len(self.nodes)