# axi_LLM

## The steps to run the test Benches: 

- Ensure you have the following tools installed on your system: 
Icarus Verilog (iverilog)
Verilator
- Install the necessary Python packages by running the following command in your project directory:
`pip install -r requirements.txt`
- Run the Test Benches: 
`pytest path/to/your_test_file.py`

This repository uses LLMs to generate AXI components and verify these components. Implementation of modules and their testbenches are taken from [this repository](https://github.com/alexforencich/verilog-axi) 
