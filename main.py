import os
import subprocess
import glob
import sys

# Ensure the script is called with the correct number of arguments
if len(sys.argv) != 2:
    print("Usage: python script_name.py <framework_name>")
    sys.exit(1)

# Get the framework name from the command line arguments
framework_name = sys.argv[1]

# Set the environment variable
os.environ['framework_name'] = framework_name
print(f"framework_name environment variable set to: {os.environ['framework_name']}")

prompts_dir = os.path.join(framework_name, 'prompts')
testbench_dir = 'tb'

# Create a directory for logs within the framework directory
stats_dir = os.path.join(framework_name, 'stats')
os.makedirs(stats_dir, exist_ok=True)
print(f"Logs will be stored in: {stats_dir}")

print(prompts_dir)

# Get all .v files in the prompts directory
v_files = glob.glob(os.path.join(prompts_dir, '*.v'))

# Execute the commands for each .v file
for v_file in v_files:
    # Extract the base name (without extension) to use as the module name
    base_name = os.path.basename(v_file).replace('.v', '')
    testbench_file = os.path.join(testbench_dir, f'test_{base_name}.py')

    # Set environment variables for the current iteration
    os.environ['testbench'] = testbench_file
    print(f"testbench environment variable set to: {os.environ['testbench']}")
    os.environ['module_name'] = base_name
    print(f"module_name environment variable set to: {os.environ['module_name']}")

    # Define the commands
    commands = [
        ['python', 'response.py', '--prompt', v_file, '--name', base_name],
        ['python', 'regex.py']
    ]
    
    # Add pytest command if the testbench exists
    if os.path.exists(testbench_file):
        commands.append(['pytest', testbench_file])
    else:
        print(f"Testbench file {testbench_file} does not exist. Skipping pytest for {v_file}.")

    # Execute each command in sequence
    for command in commands:
        print("hi")
        try:
            if 'pytest' in command:  # Check if the command is running the testbench
                stat_file_path = os.path.join(stats_dir, f"{base_name}.txt")
                with open(stat_file_path, "w") as statfile:
                    result = subprocess.run(command, check=True, stdout=statfile, stderr=statfile)
            else:
                result = subprocess.run(command, check=True)
            print(f"Command {' '.join(command)} executed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error executing command {' '.join(command)}: {e}")
            break

    # Print a new line after each iteration
    print("\n\n\n\n")
