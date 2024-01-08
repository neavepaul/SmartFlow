# Read the numbers from the text file
with open('plot_reward_data.txt', 'r') as file:
    numbers = [float(line.strip()) for line in file.readlines()]

# Calculate Mean
mean = sum(numbers) / len(numbers)

# Calculate Median
sorted_numbers = sorted(numbers)
n = len(sorted_numbers)
if n % 2 == 0:
    median = (sorted_numbers[n//2 - 1] + sorted_numbers[n//2]) / 2
else:
    median = sorted_numbers[n//2]

# Calculate Mode
from collections import Counter
number_counter = Counter(numbers)
modes = number_counter.most_common()
mode = [mode[0] for mode in modes if mode[1] == modes[0][1]]

print(f"Mean: {mean}")
print(f"Median: {median}")
print(f"Mode: {mode}")
