import matplotlib.pyplot as plt
import simulate

def size_change():
    # Set fixed arguments
    partitions = 8
    num_hr = 2
    num_lr = 3
    thresh_compl = 2
    time_limit = float('inf')

    # Initialize lists to store data
    lattice_sizes = []
    max_times = []
    net_accuracies = []

    # Loop over different lattice sizes
    for rows in range(5, 100, 10):
            size = [rows, rows]
            lattice_sizes.append(rows * rows)
            
            args = simulate.parse_arguments(['--size', str(rows), str(rows), '--partitions', str(partitions), 
                                    '--num_hr', str(num_hr), '--num_lr', str(num_lr), 
                                    '--thresh_compl', str(thresh_compl), '--time_limit', str(time_limit)])
            
            combined_resources, p, a, max_time_taken, net_accuracy = simulate.main_func(args)  # Run the main function with the current arguments
            
            # Collect the maximum time taken by any resource
            max_times.append(max_time_taken)

            # Collect the net accuracy across all partitions
            net_accuracies.append(net_accuracy)

    # Plot the graph
    plt.plot(lattice_sizes, max_times)
    plt.xlabel('Lattice Size (in nodes)')
    plt.ylabel('Maximum Time Taken (seconds)')
    plt.title('Lattice Size vs Maximum Time Taken')
    plt.show()

    # Plot the graph
    plt.plot(lattice_sizes, net_accuracies)
    plt.xlabel('Lattice Size (in nodes)')
    plt.ylabel('Net Accuracy (%)')
    ax = plt.gca()
    #ax.set_ylim([90, 100])
    plt.title('Lattice Size vs Net Accuracy')
    plt.show()

def partition_num_change():
    # Set fixed arguments
    size = [100, 100]
    num_hr = 2
    num_lr = 3
    thresh_compl = 3
    time_limit = float('inf')

    # Initialize lists to store data
    num_partitions = []
    net_accuracies = []
    max_times = []

    # Loop over different numbers of partitions
    for partitions in range(2, 11):
        num_partitions.append(partitions)
        
        args = simulate.parse_arguments(['--size', str(size[0]), str(size[1]), '--partitions', str(partitions),
                                '--num_hr', str(num_hr), '--num_lr', str(num_lr), 
                                '--thresh_compl', str(thresh_compl), '--time_limit', str(time_limit)])
        
        combined_resources, p, a, max_time_taken, net_accuracy = simulate.main_func(args)  # Run the main function with the current arguments
        
        # Collect the net accuracy across all partitions
        net_accuracies.append(net_accuracy)

        # Collect the maximum time taken by any resource
        max_times.append(max_time_taken)

    # Plot the graph
    plt.plot(num_partitions, net_accuracies)
    plt.xlabel('Number of Partitions')
    plt.ylabel('Net Accuracy (%)')
    ax = plt.gca()
    #ax.set_ylim([90, 100])
    plt.title('Number of Partitions vs Net Accuracy')
    plt.show()

    # Plot the graph
    plt.plot(num_partitions, max_times)
    plt.xlabel('Number of Partitions')
    plt.ylabel('Maximum Time Taken (seconds)')
    plt.title('Number of Partitions vs Maximum Time Taken')
    plt.show()

def res_num_change():
    # Set fixed arguments
    size = [50, 50]
    partitions = 8
    thresh_compl = 2
    time_limit = float('inf')

    # Initialize lists to store data
    num_hr_values = []
    num_lr_values = []
    max_time = []
    accuracy = []

    # Loop over different combinations of num_hr and num_lr
    for num_hr in range(2, 6):
        for num_lr in range(2, 6):
            if (num_hr+num_lr >= 5 and num_hr+num_lr <=8 ):
                num_hr_values.append(num_hr)
                num_lr_values.append(num_lr)

                args = simulate.parse_arguments(['--size', str(size[0]), str(size[1]), '--partitions', str(partitions),
                                        '--num_hr', str(num_hr), '--num_lr', str(num_lr),
                                        '--thresh_compl', str(thresh_compl), '--time_limit', str(time_limit)])

                combined_resources, p, a, max_time_taken, net_accuracy = simulate.main_func(args) # Run the main function with the current arguments

                # Collect the scheduling overhead
                max_time.append(max_time_taken)

                accuracy.append(net_accuracy)

    # Plot the graph
    fig, ax = plt.subplots(figsize=(8, 6))
    scatter = ax.scatter(num_hr_values, num_lr_values, c=max_time, cmap='viridis')
    ax.set_xlabel('Number of High-Complexity Resources')
    ax.set_ylabel('Number of Low-Complexity Resources')
    ax.set_title('Max time taken')
    cbar = fig.colorbar(scatter)
    cbar.set_label('Max time taken (seconds)')
    plt.show()

    # Plot the graph
    fig, ax = plt.subplots(figsize=(8, 6))
    scatter = ax.scatter(num_hr_values, num_lr_values, c=accuracy, cmap='plasma')
    ax.set_xlabel('Number of High-Complexity Resources')
    ax.set_ylabel('Number of Low-Complexity Resources')
    ax.set_title('Accuracy')
    cbar = fig.colorbar(scatter)
    cbar.set_label('Accuracy (%)')
    plt.show()

def thresh_compl_change():
    # Set fixed arguments
    size = [100, 100]
    partitions = 8
    num_hr = 2
    num_lr = 3
    time_limit = float('inf')

    # Initialize lists to store data
    thresh_compl_values = []
    max_times = []

    # Loop over different values of thresh_compl
    for thresh_compl in range(3, 10):
        thresh_compl_values.append(thresh_compl)

        args = simulate.parse_arguments(['--size', str(size[0]), str(size[1]), '--partitions', str(partitions),
                                '--num_hr', str(num_hr), '--num_lr', str(num_lr),
                                '--thresh_compl', str(thresh_compl), '--time_limit', str(time_limit)])

        combined_resources, p, a, max_time_taken, net_accuracy = simulate.main_func(args)  # Run the main function with the current arguments

        # Collect the net accuracy across all partitions
        max_times.append(max_time_taken)

    # Plot the graph
    plt.plot(thresh_compl_values, max_times)
    plt.xlabel('Threshold for Low-Complexity Resources')
    plt.ylabel('Max times (in sec)')
    plt.title('Threshold for Low-Complexity Resources vs Latency')
    plt.show()

# def time_lim_change():
#     # Set fixed arguments
#     size = [20, 20]
#     partitions = 8
#     num_hr = 2
#     num_lr = 3
#     thresh_compl = 2

#     # Initialize lists to store data
#     time_limits = []
#     max_times = []
#     exceeded_time_limit = []

#     # Loop over different time limits
#     for time_limit in [0.000000002, 0.000000003, 0.000000004, 0.000000005, 0.000000006, float('inf')]:
#         time_limits.append(time_limit)
#         args = simulate.parse_arguments(['--size', str(size[0]), str(size[1]), '--partitions', str(partitions),
#                                 '--num_hr', str(num_hr), '--num_lr', str(num_lr),
#                                 '--thresh_compl', str(thresh_compl), '--time_limit', str(time_limit)])

#         combined_resources, p, a, max_time_taken, net_accuracy = simulate.main_func(args)  # Run the main function with the current arguments

#         # Collect the maximum time taken by any resource
#         max_times.append(max_time_taken)

#         # Check if the time limit was exceeded
#         if max_time_taken > time_limit:
#             exceeded_time_limit.append(True)
#         else:
#             exceeded_time_limit.append(False)

#     # Plot the graph
#     fig, ax = plt.subplots(figsize=(8, 6))
#     scatter = ax.scatter(time_limits, max_times, c=exceeded_time_limit, cmap='plasma')
#     ax.set_xlabel('Time Limit (seconds)')
#     ax.set_ylabel('Maximum Time Taken (seconds)')
#     ax.set_title('Time Limit vs Maximum Time Taken')
#     cbar = fig.colorbar(scatter)
#     cbar.set_ticks([0, 1])
#     cbar.set_ticklabels(['Exceeded Limit','Within Limit'])
#     plt.show()

def main():
    print("\nChoose an experiment to run:")
    print("1. Lattice Size vs Net Accuracy and Maximum Time Taken")
    print("2. Number of Partitions vs Net Accuracy and Maximum Time Taken")
    print("3. Resource Configuration vs Maximum Time Taken and Accuracy")
    print("4. Threshold for Low-Complexity Resources vs Latency")
    print("5. Exit")

    choice = input("Enter your choice (1-5): ")

    if choice == "1":
        size_change()
    elif choice == "2":
        partition_num_change()
    elif choice == "3":
        res_num_change()
    elif choice == "4":
        thresh_compl_change()
    # elif choice == "5":
    #     time_lim_change()
    elif choice == "5":
        print("Exiting...")
    else:
        print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()