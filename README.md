# axi_LLM

## The steps to run the simulation: 

1. Set up a virtual enviroment: 
- python3 -m venv venv
- source venv/bin/activate

2. Install the required python packages:
- pip3 install -r requirements.txt 

3. Run  `pip install "numpy<2"`

4. Set up the enviroment variable: `OPENAI_API_KEY`

5. Run `python stats.py <framework name> <model name>`

### models available 
- ChatGPT4
- Claude 
- ChatGPT3p5
- ChatGPT4o
- ChatGPT4o-mini
- PaLM
- CodeLlama

### Frameworks so Far: 
- Zero-shot

This repository uses LLMs to generate AXI components and verify these components. Implementation of modules and their testbenches are taken from [this repository](https://github.com/alexforencich/verilog-axi) 
