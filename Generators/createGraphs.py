import matplotlib.pyplot as plt
import re
from collections import defaultdict

def read_time_speeds(file_path: str):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    data = []
    current_algorithm = None
    current_dataset = None
    current_times = []
    
    for line in lines:
        if line.startswith("Algorithm:"):
            if current_algorithm is not None:
                data.append((current_algorithm, current_dataset, current_times))
            current_algorithm = line.split(":")[1].strip()
            current_times = []
        elif line.startswith("Dataset:"):
            current_dataset = line.split(":")[1].strip()
        elif re.match(r"^\d+(\.\d+)?$", line.strip()):
            current_times.append(float(line.strip()))
    
    if current_algorithm is not None:
        data.append((current_algorithm, current_dataset, current_times))
    
    return data

def group_by_dataset(data):
    grouped_data = defaultdict(list)
    for algorithm, dataset, times in data:
        grouped_data[dataset].append((algorithm, times))
    return grouped_data

def plot_time_speeds(grouped_data):
    for dataset, algorithms in grouped_data.items():
        plt.figure(figsize=(10, 6))
        for algorithm, times in algorithms:
            plt.plot(times, label=algorithm, marker='o')
            avg_time = sum(times) / len(times)
            plt.text(len(times) - 1, times[-1], f'Avg: {avg_time:.2f}', fontsize=9, verticalalignment='bottom')
        
        plt.xlabel('Run')
        plt.ylabel('Time (seconds)')
        plt.title(f'Programs time to solve for: {dataset}')
        plt.legend()
        plt.grid(True)
        plt.show()
    
def main():
    file_path = './timeSpeeds.txt'
    data = read_time_speeds(file_path)
    grouped_data = group_by_dataset(data)
    plot_time_speeds(grouped_data)

if __name__ == "__main__":
    main()