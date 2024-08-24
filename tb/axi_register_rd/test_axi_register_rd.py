import itertools
import logging
import os

<<<<<<< HEAD
import cocotb_test.simulator  # Importing the simulator interface from cocotb_test for pytest integration
import pytest  # Importing pytest for parameterized testing

import cocotb  # Importing cocotb for co-simulation
from cocotb.clock import Clock  # Importing the Clock module to generate clock signals in the testbench
from cocotb.triggers import RisingEdge  # Importing triggers for event-based simulation
from cocotb.regression import TestFactory  # Importing TestFactory for automated test generation

from cocotbext.axi import AxiBus, AxiMaster, AxiRam  # Importing AXI components from cocotbext library

# Testbench class definition
class TB(object):
    def __init__(self, dut):
        self.dut = dut  # Storing the device under test (DUT) reference

        # Set up logging for debug information
        self.log = logging.getLogger("cocotb.tb")  # Setting up a logger named "cocotb.tb"
        self.log.setLevel(logging.DEBUG)  # Configuring the logger to display debug-level messages

        # Start a clock for the DUT with a period of 10ns
        cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())  # Creating a clock signal with a 10ns period

        # Initialize AXI master interface for sending read commands
        self.axi_master = AxiMaster(AxiBus.from_prefix(dut, "s_axi"), dut.clk, dut.rst)  # Connecting the AxiMaster to the DUT's s_axi interface
        
        # Initialize AXI RAM model for memory operations
        self.axi_ram = AxiRam(AxiBus.from_prefix(dut, "m_axi"), dut.clk, dut.rst, size=2**16)  # Connecting the AxiRam to the DUT's m_axi interface
=======
import cocotb_test.simulator
import pytest

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge
from cocotb.regression import TestFactory

from cocotbext.axi import AxiBus, AxiMaster, AxiRam

class TB(object):
    def __init__(self, dut):
        self.dut = dut

        # Set up logging for debug information
        self.log = logging.getLogger("cocotb.tb")
        self.log.setLevel(logging.DEBUG)

        # Start a clock for the DUT with a period of 10ns
        cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())

        # Initialize AXI master interface for sending read commands
        self.axi_master = AxiMaster(AxiBus.from_prefix(dut, "s_axi"), dut.clk, dut.rst)
        
        # Initialize AXI RAM model for memory operations
        self.axi_ram = AxiRam(AxiBus.from_prefix(dut, "m_axi"), dut.clk, dut.rst, size=2**16)
>>>>>>> refs/remotes/origin/main

    def set_idle_generator(self, generator=None):
        """Set a generator to pause the AXI transactions for idle periods."""
        if generator:
<<<<<<< HEAD
            # Apply the pause generator to the read channels of the AXI master and AXI RAM interfaces
=======
>>>>>>> refs/remotes/origin/main
            self.axi_master.read_if.ar_channel.set_pause_generator(generator())
            self.axi_ram.read_if.r_channel.set_pause_generator(generator())

    def set_backpressure_generator(self, generator=None):
        """Set a generator to create backpressure on the AXI bus."""
        if generator:
<<<<<<< HEAD
            # Apply backpressure to the AXI master and AXI RAM read channels
=======
>>>>>>> refs/remotes/origin/main
            self.axi_master.read_if.r_channel.set_pause_generator(generator())
            self.axi_ram.read_if.ar_channel.set_pause_generator(generator())

    async def cycle_reset(self):
        """Reset the DUT."""
<<<<<<< HEAD
        self.dut.rst.setimmediatevalue(0)  # Deassert reset signal initially
        await RisingEdge(self.dut.clk)  # Wait for a rising edge of the clock
        await RisingEdge(self.dut.clk)  # Wait for another rising edge of the clock
        self.dut.rst.value = 1  # Assert the reset signal
        await RisingEdge(self.dut.clk)  # Wait for a clock edge with reset asserted
        await RisingEdge(self.dut.clk)  # Wait for another clock edge with reset asserted
        self.dut.rst.value = 0  # Deassert the reset signal
        await RisingEdge(self.dut.clk)  # Wait for the clock edge with reset deasserted
        await RisingEdge(self.dut.clk)  # Wait for another clock edge with reset deasserted

# Test routine for AXI read functionality
async def run_test_read(dut, data_in=None, idle_inserter=None, backpressure_inserter=None, size=None):
    """Test routine for AXI read functionality."""

    tb = TB(dut)  # Instantiate the testbench

    # Determine byte lanes and maximum burst size
    byte_lanes = tb.axi_master.read_if.byte_lanes  # Number of byte lanes in the AXI master interface
    max_burst_size = tb.axi_master.read_if.max_burst_size  # Maximum burst size allowed by the AXI master

    if size is None:
        size = max_burst_size  # Use the maximum burst size if no specific size is provided

    # Reset the DUT
    await tb.cycle_reset()  # Perform a reset of the DUT

    # Set idle and backpressure generators
    tb.set_idle_generator(idle_inserter)  # Apply idle cycles if an idle generator is provided
    tb.set_backpressure_generator(backpressure_inserter)  # Apply backpressure if a backpressure generator is provided

    # Loop through different lengths and offsets for read transactions
    for length in list(range(1, byte_lanes * 2)) + [1024]:  # Test various lengths, including 1024 bytes
        for offset in list(range(byte_lanes, byte_lanes * 2)) + list(range(4096 - byte_lanes, 4096)):  # Test different offsets within a range
            tb.log.info("length %d, offset %d, size %d", length, offset, size)  # Log the parameters of the current test
            addr = offset + 0x1000  # Calculate the address for the read transaction
            test_data = bytearray([x % 256 for x in range(length)])  # Generate test data of the specified length

            # Write test data to AXI RAM at the calculated address
            tb.axi_ram.write(addr, test_data)

            # Perform the read transaction from the AXI master
            data = await tb.axi_master.read(addr, length, size=size)

            # Check if the read data matches the test data
            assert data.data == test_data  # Validate the correctness of the read operation

    await RisingEdge(dut.clk)  # Wait for a clock edge after the test
    await RisingEdge(dut.clk)  # Wait for another clock edge after the test

# Idle cycle generator function
def cycle_pause():
    """Generator for creating idle periods."""
    return itertools.cycle([1, 1, 1, 0])  # Generate a repeating pattern of idle cycles

if cocotb.SIM_NAME:
    # Register the test with cocotb
    factory = TestFactory(run_test_read)  # Create a TestFactory for the read test
    factory.add_option("idle_inserter", [None, cycle_pause])  # Add an option to include idle cycles in the test
    factory.add_option("backpressure_inserter", [None, cycle_pause])  # Add an option to include backpressure in the test
    factory.add_option("size", [None] + list(range(1, 32)))  # Add an option to test different burst sizes
    factory.generate_tests()  # Generate the tests based on the provided options

# cocotb-test integration for pytest

tests_dir = os.path.abspath(os.path.dirname(__file__))  # Get the directory of the current test file
rtl_dir = os.path.abspath(os.path.join(tests_dir, '..', '..', 'responses'))  # Define the directory for RTL files

# Define the pytest function for running the simulation
@pytest.mark.parametrize("delay", [0, 1])  # Parameterize the test for different delays
@pytest.mark.parametrize("data_width", [8, 16, 32])  # Parameterize the test for different data widths
def test_axi_register_rd(request, data_width, delay):
    """Pytest configuration for the testbench."""
    dut = "axi_register_rd"  # Specify the DUT module name
    module = os.path.splitext(os.path.basename(__file__))[0]  # Get the name of the testbench module
    toplevel = dut  # Set the top-level module in the simulation

    # Specify the Verilog source files for the DUT
    verilog_sources = [
        os.path.join(rtl_dir, f"{dut}.v"),  # Path to the Verilog source of the DUT
    ]

    # Define parameters to be passed to the Verilog module
    parameters = {}
    parameters['DATA_WIDTH'] = data_width  # Set the data width parameter
    parameters['ADDR_WIDTH'] = 32  # Set the address width parameter
    parameters['STRB_WIDTH'] = parameters['DATA_WIDTH'] // 8  # Set the strobe width based on data width
    parameters['ID_WIDTH'] = 8  # Set the ID width parameter
    parameters['ARUSER_ENABLE'] = 0  # Disable the ARUSER signal
    parameters['ARUSER_WIDTH'] = 1  # Set the ARUSER width to 1 (irrelevant since disabled)
    parameters['RUSER_ENABLE'] = 0  # Disable the RUSER signal
    parameters['RUSER_WIDTH'] = 1  # Set the RUSER width to 1 (irrelevant since disabled)
    # The following parameters are commented out but could be enabled if needed:
    # parameters['READ_FIFO_DEPTH'] = 32
    # parameters['READ_FIFO_DELAY'] = delay

    # Extra environment variables for simulation
    extra_env = {f'PARAM_{k}': str(v) for k, v in parameters.items()}

    # Directory for storing simulation build artifacts
    sim_build = os.path.join(tests_dir, "sim_build", request.node.name.replace('[', '-').replace(']', ''))

    # Run the simulation with the specified configuration
    cocotb_test.simulator.run(
        python_search=[tests_dir],  # Python search path for test scripts
        verilog_sources=verilog_sources,  # List of Verilog sources to compile
        toplevel=toplevel,  # Top-level Verilog module
        module=module,  # Testbench module
        parameters=parameters,  # Parameters to pass to the Verilog module
        sim_build=sim_build,  # Build directory for simulation
        extra_env=extra_env,  # Extra environment variables for simulation
=======
        self.dut.rst.setimmediatevalue(0)
        await RisingEdge(self.dut.clk)
        await RisingEdge(self.dut.clk)
        self.dut.rst.value = 1
        await RisingEdge(self.dut.clk)
        await RisingEdge(self.dut.clk)
        self.dut.rst.value = 0
        await RisingEdge(self.dut.clk)
        await RisingEdge(self.dut.clk)

async def run_test_read(dut, data_in=None, idle_inserter=None, backpressure_inserter=None, size=None):
    """Test routine for AXI read functionality."""

    tb = TB(dut)

    # Determine byte lanes and maximum burst size
    byte_lanes = tb.axi_master.read_if.byte_lanes
    max_burst_size = tb.axi_master.read_if.max_burst_size

    if size is None:
        size = max_burst_size

    # Reset the DUT
    await tb.cycle_reset()

    # Set idle and backpressure generators
    tb.set_idle_generator(idle_inserter)
    tb.set_backpressure_generator(backpressure_inserter)

    # Loop through different lengths and offsets for read transactions
    for length in list(range(1, byte_lanes * 2)) + [1024]:
        for offset in list(range(byte_lanes, byte_lanes * 2)) + list(range(4096 - byte_lanes, 4096)):
            tb.log.info("length %d, offset %d, size %d", length, offset, size)
            addr = offset + 0x1000
            test_data = bytearray([x % 256 for x in range(length)])

            # Write test data to AXI RAM
            tb.axi_ram.write(addr, test_data)

            # Perform the read transaction
            data = await tb.axi_master.read(addr, length, size=size)

            # Check if the read data matches the test data
            assert data.data == test_data

    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)

def cycle_pause():
    """Generator for creating idle periods."""
    return itertools.cycle([1, 1, 1, 0])

if cocotb.SIM_NAME:
    # Register the test with cocotb
    factory = TestFactory(run_test_read)
    factory.add_option("idle_inserter", [None, cycle_pause])
    factory.add_option("backpressure_inserter", [None, cycle_pause])
    factory.add_option("size", [None]+list(range(1, 32)))  # Modify range as needed
    factory.generate_tests()

# cocotb-test

tests_dir = os.path.abspath(os.path.dirname(__file__))
rtl_dir = os.path.abspath(os.path.join(tests_dir, '..', '..', 'responses'))

@pytest.mark.parametrize("delay", [0, 1])
@pytest.mark.parametrize("data_width", [8, 16, 32])
def test_axi_register_rd(request, data_width, delay):
    """Pytest configuration for the testbench."""
    dut = "axi_register_rd"
    module = os.path.splitext(os.path.basename(__file__))[0]
    toplevel = dut

    verilog_sources = [
        os.path.join(rtl_dir, f"{dut}.v"),
    ]

    parameters = {}

    parameters['DATA_WIDTH'] = data_width
    parameters['ADDR_WIDTH'] = 32
    parameters['STRB_WIDTH'] = parameters['DATA_WIDTH'] // 8
    parameters['ID_WIDTH'] = 8
    parameters['ARUSER_ENABLE'] = 0
    parameters['ARUSER_WIDTH'] = 1
    parameters['RUSER_ENABLE'] = 0
    parameters['RUSER_WIDTH'] = 1
    parameters['READ_FIFO_DEPTH'] = 32
    parameters['READ_FIFO_DELAY'] = delay

    extra_env = {f'PARAM_{k}': str(v) for k, v in parameters.items()}

    sim_build = os.path.join(tests_dir, "sim_build",
        request.node.name.replace('[', '-').replace(']', ''))

    cocotb_test.simulator.run(
        python_search=[tests_dir],
        verilog_sources=verilog_sources,
        toplevel=toplevel,
        module=module,
        parameters=parameters,
        sim_build=sim_build,
        extra_env=extra_env,
>>>>>>> refs/remotes/origin/main
    )
