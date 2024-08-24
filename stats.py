import subprocess
import os
import glob
import sys

def check_test_results(file_path):
    with open(file_path, 'r') as file:
        content = file.readlines()

    # Check for simulation completion
    simulation_successful = any("Simulation completed successfully." in line for line in content)
    
    # Count the number of tests passed
    passed_tests = sum(1 for line in content if "passed!" in line)
    
    # Count the total number of tests
    total_tests = sum(1 for line in content if line.startswith("Test"))

    if not simulation_successful:
        return False, 0, total_tests

    if passed_tests == total_tests:
        return True, passed_tests, total_tests
    else:
        return False, passed_tests, total_tests

# Ensure the script is called with exactly one argument
if len(sys.argv) != 2:
    print("Usage: python script_name.py <framework_name>")
    sys.exit(1)

# Get the framework name from the command line arguments
framework_name = sys.argv[1]

succ_counter = {}
os.environ['framework_name'] = framework_name

# Define the directory paths based on framework_name
if framework_name == "RaR":
    framework_directory = os.path.join(os.getcwd(), "RaR")
    script_path = os.path.join(framework_directory, "rar.py")
    # Update prompts and stats directory for RaR framework
    prompts_dir = os.path.join(framework_directory, 'prompts')
    stats_dir = os.path.join(framework_directory, 'stats')
elif framework_name == "RoEm":
    framework_directory = os.path.join(os.getcwd(), "RoEm")
    script_path = os.path.join(framework_directory, "roem.py")
    # Update prompts and stats directory for RaR framework
    prompts_dir = os.path.join(framework_directory, 'prompts')
    stats_dir = os.path.join(framework_directory, 'stats')
else:
    # For other frameworks, use the framework_name directly
    prompts_dir = os.path.join(framework_name, 'prompts')
    stats_dir = os.path.join(framework_name, 'stats')

# Perform iterations
for i in range(5):
    if framework_name == "RaR":
        print(f"Executing rar.py for framework {framework_name} (iteration {i + 1})...")
        try:
            subprocess.run(['python', script_path], check=True)
            print(f"Execution of {script_path} completed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error executing {script_path}: {e}")
            continue
    elif framework_name == "RoEm":
        print(f"Executing roem.py for framework {framework_name} (iteration {i + 1})...")
        try:
            subprocess.run(['python', script_path], check=True)
            print(f"Execution of {script_path} completed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error executing {script_path}: {e}")
            continue
    subprocess.run(['python', 'main.py', framework_name], check=True)

    # Get all log files in the stats directory
    stats_files = glob.glob(os.path.join(stats_dir, '*.txt'))

    # Iterate through each log file and check the test results
    for stats_file in stats_files:
        stats_file_name = os.path.splitext(os.path.basename(stats_file))[0]

        # Initialize the dictionary entry to 0 if it doesn't exist
        if stats_file_name not in succ_counter:
            succ_counter[stats_file_name] = [0, 0, 0]

        results = check_test_results(stats_file)

        if results[0]:
            succ_counter[stats_file_name][0] += 1
        
        succ_counter[stats_file_name][1] += results[1]
        succ_counter[stats_file_name][2] += results[2]
        succ_counter[stats_file_name].append(results[1] / results[2] if results[2] != 0 else 0)

# Ensure the metrics directory exists
metrics_dir = framework_name
if not os.path.exists(metrics_dir):
    os.makedirs(metrics_dir)

# Write the results to metrics.txt
metrics_file_path = os.path.join(metrics_dir, 'metrics.txt')

with open(metrics_file_path, 'w') as metrics_file:
    # Define the column widths
    name_width = 17
    success_width = 13
    ratio_width = 24
    total_success_width = 10
    overall_success_width = 7

    # Writing header
    metrics_file.write(f"{'Name'.ljust(name_width)} | {'Overall Success'.ljust(success_width)} | "
                       f"{'Success Ratio Iteration 1'.ljust(ratio_width)} | "
                       f"{'Success Ratio Iteration 2'.ljust(ratio_width)} | "
                       f"{'Success Ratio Iteration 3'.ljust(ratio_width)} | "
                       f"{'Success Ratio Iteration 4'.ljust(ratio_width)} | "
                       f"{'Success Ratio Iteration 5'.ljust(ratio_width)} | "
                       f"{'Total Success'.ljust(total_success_width)} | "
                       f"{'Sum of Ratios'.ljust(overall_success_width)}\n")
    for key, value in succ_counter.items():
        # Formatting the output for Total Success with "/5"
        total_success = f"{value[0]}/5".ljust(success_width)
        success_ratios = ' | '.join(f"{ratio:24.2f}" for ratio in value[3:])
        overall_success_ratio = value[1] / value[2] if value[2] != 0 else 0.0  # Prevent division by zero
        sum_of_ratios = sum(value[3:])  # Calculate the sum of success ratios from value[3:]
        metrics_file.write(f"{key.ljust(name_width)} | {total_success} | {success_ratios} | "
                           f"{overall_success_ratio:24.2f} | {sum_of_ratios:7.2f}\n")

print(f"Metrics saved to {metrics_file_path}")
