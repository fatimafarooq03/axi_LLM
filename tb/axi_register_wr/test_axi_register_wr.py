import itertools
import logging
import os

<<<<<<< HEAD
import cocotb_test.simulator  # Import the cocotb test simulator for running simulations with pytest
import pytest  # Import pytest for running parameterized tests

import cocotb  # Import cocotb for co-simulation
from cocotb.clock import Clock  # Import Clock from cocotb to generate clock signals in the testbench
from cocotb.triggers import RisingEdge  # Import RisingEdge trigger for synchronizing with clock edges
from cocotb.regression import TestFactory  # Import TestFactory for creating test cases in cocotb

from cocotbext.axi import AxiBus, AxiMaster, AxiRam  # Import AXI components from cocotb extension library

# Testbench class definition
class TB(object):
    def __init__(self, dut):
        self.dut = dut  # Store a reference to the Device Under Test (DUT)

        # Set up logging for debug information
        self.log = logging.getLogger("cocotb.tb")  # Create a logger for the testbench
        self.log.setLevel(logging.DEBUG)  # Set logging level to DEBUG to capture detailed information

        # Start a clock for the DUT with a period of 10ns
        cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())  # Start the clock with a 10ns period

        # Initialize AXI master interface for sending write commands
        # The AxiMaster is connected to the s_axi interface of the axi_register_wr module
        self.axi_master = AxiMaster(AxiBus.from_prefix(dut, "s_axi"), dut.clk, dut.rst)
        
        # Initialize AXI RAM model for memory operations
        # The AxiRam is connected to the m_axi interface of the axi_register_wr module
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

        # Initialize AXI master interface for sending write commands
        self.axi_master = AxiMaster(AxiBus.from_prefix(dut, "s_axi"), dut.clk, dut.rst)
        
        # Initialize AXI RAM model for memory operations
>>>>>>> refs/remotes/origin/main
        self.axi_ram = AxiRam(AxiBus.from_prefix(dut, "m_axi"), dut.clk, dut.rst, size=2**16)

    def set_idle_generator(self, generator=None):
        """Set a generator to pause the AXI transactions for idle periods."""
        if generator:
<<<<<<< HEAD
            # Apply the idle generator to the AXI master's write channels and the AXI RAM's B channel
=======
>>>>>>> refs/remotes/origin/main
            self.axi_master.write_if.aw_channel.set_pause_generator(generator())
            self.axi_master.write_if.w_channel.set_pause_generator(generator())
            self.axi_ram.write_if.b_channel.set_pause_generator(generator())

    def set_backpressure_generator(self, generator=None):
        """Set a generator to create backpressure on the AXI bus."""
        if generator:
<<<<<<< HEAD
            # Apply the backpressure generator to the AXI master's B channel and the AXI RAM's write channels
=======
>>>>>>> refs/remotes/origin/main
            self.axi_master.write_if.b_channel.set_pause_generator(generator())
            self.axi_ram.write_if.aw_channel.set_pause_generator(generator())
            self.axi_ram.write_if.w_channel.set_pause_generator(generator())

    async def cycle_reset(self):
        """Reset the DUT."""
<<<<<<< HEAD
        self.dut.rst.setimmediatevalue(0)  # Deassert reset initially
        await RisingEdge(self.dut.clk)  # Wait for a clock edge
        await RisingEdge(self.dut.clk)  # Wait for another clock edge
        self.dut.rst.value = 1  # Assert reset signal
        await RisingEdge(self.dut.clk)  # Wait for a clock edge while reset is asserted
        await RisingEdge(self.dut.clk)  # Wait for another clock edge with reset asserted
        self.dut.rst.value = 0  # Deassert reset signal
        await RisingEdge(self.dut.clk)  # Wait for a clock edge after reset is deasserted
        await RisingEdge(self.dut.clk)  # Wait for another clock edge after reset

# Test routine for AXI write functionality
async def run_test_write(dut, data_in=None, idle_inserter=None, backpressure_inserter=None, size=None):
    """Test routine for AXI write functionality."""

    tb = TB(dut)  # Instantiate the testbench with the DUT

    # Determine byte lanes and maximum burst size
    byte_lanes = tb.axi_master.write_if.byte_lanes  # Get the number of byte lanes in the AXI master interface
    max_burst_size = tb.axi_master.write_if.max_burst_size  # Get the maximum burst size allowed by the AXI master

    if size is None:
        size = max_burst_size  # Use the maximum burst size if not specified

    # Reset the DUT
    await tb.cycle_reset()  # Perform a reset on the DUT

    # Set idle and backpressure generators
    tb.set_idle_generator(idle_inserter)  # Apply idle cycles if an idle generator is provided
    tb.set_backpressure_generator(backpressure_inserter)  # Apply backpressure if a backpressure generator is provided

    # Loop through different lengths and offsets for write transactions
    for length in list(range(1, byte_lanes * 2)) + [1024]:  # Test various write lengths, including 1024 bytes
        for offset in list(range(byte_lanes, byte_lanes * 2)) + list(range(4096 - byte_lanes, 4096)):  # Test different offsets within a range
            tb.log.info("length %d, offset %d, size %d", length, offset, size)  # Log the parameters of the current test
            addr = offset + 0x1000  # Calculate the address for the write transaction
            test_data = bytearray([x % 256 for x in range(length)])  # Generate test data of the specified length

            # Prepare the AXI RAM for testing by writing a pattern around the test area
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

async def run_test_write(dut, data_in=None, idle_inserter=None, backpressure_inserter=None, size=None):
    """Test routine for AXI write functionality."""

    tb = TB(dut)

    # Determine byte lanes and maximum burst size
    byte_lanes = tb.axi_master.write_if.byte_lanes
    max_burst_size = tb.axi_master.write_if.max_burst_size

    if size is None:
        size = max_burst_size

    # Reset the DUT
    await tb.cycle_reset()

    # Set idle and backpressure generators
    tb.set_idle_generator(idle_inserter)
    tb.set_backpressure_generator(backpressure_inserter)

    # Loop through different lengths and offsets for write transactions
    for length in list(range(1, byte_lanes * 2)) + [1024]:
        for offset in list(range(byte_lanes, byte_lanes * 2)) + list(range(4096 - byte_lanes, 4096)):
            tb.log.info("length %d, offset %d, size %d", length, offset, size)
            addr = offset + 0x1000
            test_data = bytearray([x % 256 for x in range(length)])

            # Prepare the AXI RAM for testing
>>>>>>> refs/remotes/origin/main
            tb.axi_ram.write(addr - 128, b'\xaa' * (length + 256))

            # Perform the write transaction
            await tb.axi_master.write(addr, test_data, size=size)

<<<<<<< HEAD
            # Log the write operation to show the memory content around the written data
            tb.log.debug("%s", tb.axi_ram.hexdump_str((addr & ~0xf) - 16, (((addr & 0xf) + length - 1) & ~0xf) + 48))

            # Verify that the data was written correctly by reading back the written data and surrounding areas
            assert tb.axi_ram.read(addr, length) == test_data  # Check if the main data was written correctly
            assert tb.axi_ram.read(addr - 1, 1) == b'\xaa'  # Ensure that the data before the written area remains unchanged
            assert tb.axi_ram.read(addr + length, 1) == b'\xaa'  # Ensure that the data after the written area remains unchanged

    await RisingEdge(dut.clk)  # Wait for a clock edge after the test
    await RisingEdge(dut.clk)  # Wait for another clock edge after the test

# Idle cycle generator function
def cycle_pause():
    """Generator for creating idle periods."""
    return itertools.cycle([1, 1, 1, 0])  # Generate a repeating pattern of idle cycles

if cocotb.SIM_NAME:
    # Register the test with cocotb
    factory = TestFactory(run_test_write)  # Create a TestFactory for the write test
    factory.add_option("idle_inserter", [None, cycle_pause])  # Add an option to include idle cycles in the test
    factory.add_option("backpressure_inserter", [None, cycle_pause])  # Add an option to include backpressure in the test
    factory.add_option("size", [None]+list(range(1, 32)))  # Add an option to test different burst sizes
    factory.generate_tests()  # Generate the tests based on the provided options

# cocotb-test integration for pytest

tests_dir = os.path.abspath(os.path.dirname(__file__))  # Get the directory of the current test file
rtl_dir = os.path.abspath(os.path.join(tests_dir, '..', '..', 'responses'))  # Define the directory for RTL files

# Define the pytest function for running the simulation
@pytest.mark.parametrize("delay", [0, 1])  # Parameterize the test for different delays
@pytest.mark.parametrize("data_width", [8, 16, 32])  # Parameterize the test for different data widths
def test_axi_register_wr(request, data_width, delay):
    """Pytest configuration for the testbench."""
    dut = "axi_register_wr"  # Specify the DUT module name
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
    parameters['AWUSER_ENABLE'] = 0  # Disable the AWUSER signal
    parameters['AWUSER_WIDTH'] = 1  # Set AWUSER width (only relevant if AWUSER is enabled)
    parameters['WUSER_ENABLE'] = 0  # Disable the WUSER signal
    parameters['WUSER_WIDTH'] = 1  # Set WUSER width (only relevant if WUSER is enabled)
    parameters['BUSER_ENABLE'] = 0  # Disable the BUSER signal
    parameters['BUSER_WIDTH'] = 1  # Set BUSER width (only relevant if BUSER is enabled)
    # Additional parameters for FIFO depth and delay can be added if needed

    extra_env = {f'PARAM_{k}': str(v) for k, v in parameters.items()}  # Convert parameters to environment variables

    sim_build = os.path.join(tests_dir, "sim_build",  # Define the build directory for the simulation
        request.node.name.replace('[', '-').replace(']', ''))

    # Run the simulation using cocotb_test's simulator function
    cocotb_test.simulator.run(
        python_search=[tests_dir],  # Specify the search path for Python test scripts
        verilog_sources=verilog_sources,  # List of Verilog source files to compile
        toplevel=toplevel,  # Specify the top-level Verilog module
        module=module,  # Specify the testbench module to run
        parameters=parameters,  # Pass the parameters to the Verilog module
        sim_build=sim_build,  # Directory where the simulation build files will be stored
        extra_env=extra_env,  # Pass extra environment variables to the simulation
=======
            # Log the write operation
            tb.log.debug("%s", tb.axi_ram.hexdump_str((addr & ~0xf) - 16, (((addr & 0xf) + length - 1) & ~0xf) + 48))

            # Verify that the data was written correctly
            assert tb.axi_ram.read(addr, length) == test_data
            assert tb.axi_ram.read(addr - 1, 1) == b'\xaa'
            assert tb.axi_ram.read(addr + length, 1) == b'\xaa'

    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)

def cycle_pause():
    """Generator for creating idle periods."""
    return itertools.cycle([1, 1, 1, 0])

if cocotb.SIM_NAME:
    # Register the test with cocotb
    factory = TestFactory(run_test_write)
    factory.add_option("idle_inserter", [None, cycle_pause])
    factory.add_option("backpressure_inserter", [None, cycle_pause])
    factory.add_option("size", [None]+list(range(1, 32)))  # Modify range as needed
    factory.generate_tests()

# cocotb-test

tests_dir = os.path.abspath(os.path.dirname(__file__))
rtl_dir = os.path.abspath(os.path.join(tests_dir, '..', '..', 'responses'))

@pytest.mark.parametrize("delay", [0, 1])
@pytest.mark.parametrize("data_width", [8, 16, 32])
def test_axi_register_wr(request, data_width, delay):
    """Pytest configuration for the testbench."""
    dut = "axi_register_wr"
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
    parameters['AWUSER_ENABLE'] = 0
    parameters['AWUSER_WIDTH'] = 1
    parameters['WUSER_ENABLE'] = 0
    parameters['WUSER_WIDTH'] = 1
    parameters['BUSER_ENABLE'] = 0
    parameters['BUSER_WIDTH'] = 1
    parameters['WRITE_FIFO_DEPTH'] = 32
    parameters['WRITE_FIFO_DELAY'] = delay

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
