import itertools
import logging
import os
import random

<<<<<<< HEAD
import cocotb_test.simulator  # Importing cocotb_test's simulator for integration with pytest
import pytest  # Importing pytest for parameterized testing

import cocotb  # Importing cocotb for co-simulation
from cocotb.clock import Clock  # Importing Clock module to generate clock signals in the testbench
from cocotb.triggers import RisingEdge, Timer  # Importing triggers for event-based simulation
from cocotb.regression import TestFactory  # Importing TestFactory for automated test generation

from cocotbext.axi import AxiBus, AxiMaster, AxiRam  # Importing AXI bus components from cocotbext library

# Testbench class definition
class TB(object):
    def __init__(self, dut):
        self.dut = dut  # Device under test (DUT) is passed and stored

        # Set up logging for debug information
        self.log = logging.getLogger("cocotb.tb")  # Logger for the testbench
        self.log.setLevel(logging.DEBUG)  # Setting log level to DEBUG for detailed output

        # Start a clock for the DUT with a period of 10ns
        cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())  # Clock with 10ns period
=======
import cocotb_test.simulator
import pytest

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer
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
>>>>>>> refs/remotes/origin/main

        # Initialize AXI master interface for sending write commands
        # The AxiMaster is connected to the s_axi interface of the axi_fifo_wr module
        self.axi_master = AxiMaster(AxiBus.from_prefix(dut, "s_axi"), dut.clk, dut.rst)
        
        # Initialize AXI RAM model for memory operations
        # The AxiRam is connected to the m_axi interface of the axi_fifo_wr module
        self.axi_ram = AxiRam(AxiBus.from_prefix(dut, "m_axi"), dut.clk, dut.rst, size=2**16)

    def set_idle_generator(self, generator=None):
        """Set a generator to pause the AXI transactions for idle periods."""
        if generator:
<<<<<<< HEAD
            # Apply the pause generator to all channels of the AXI master and RAM interfaces
=======
>>>>>>> refs/remotes/origin/main
            self.axi_master.write_if.aw_channel.set_pause_generator(generator())
            self.axi_master.write_if.w_channel.set_pause_generator(generator())
            self.axi_master.read_if.ar_channel.set_pause_generator(generator())
            self.axi_ram.write_if.b_channel.set_pause_generator(generator())
            self.axi_ram.read_if.r_channel.set_pause_generator(generator())

    def set_backpressure_generator(self, generator=None):
        """Set a generator to create backpressure on the AXI bus."""
        if generator:
<<<<<<< HEAD
            # Apply backpressure to the AXI master and RAM interfaces
=======
>>>>>>> refs/remotes/origin/main
            self.axi_master.write_if.b_channel.set_pause_generator(generator())
            self.axi_master.read_if.r_channel.set_pause_generator(generator())
            self.axi_ram.write_if.aw_channel.set_pause_generator(generator())
            self.axi_ram.write_if.w_channel.set_pause_generator(generator())
            self.axi_ram.read_if.ar_channel.set_pause_generator(generator())

    async def cycle_reset(self):
        """Reset the DUT."""
<<<<<<< HEAD
        self.dut.rst.setimmediatevalue(0)  # Deassert reset initially
        await RisingEdge(self.dut.clk)  # Wait for a rising edge of the clock
        await RisingEdge(self.dut.clk)  # Wait for another rising edge of the clock
        self.dut.rst.value = 1  # Assert reset signal
        await RisingEdge(self.dut.clk)  # Wait for the clock edge with reset asserted
        await RisingEdge(self.dut.clk)  # Wait for another clock edge with reset asserted
        self.dut.rst.value = 0  # Deassert reset signal
        await RisingEdge(self.dut.clk)  # Wait for the clock edge with reset deasserted
        await RisingEdge(self.dut.clk)  # Wait for another clock edge with reset deasserted

# Test routine for AXI write functionality
async def run_test_write(dut, data_in=None, idle_inserter=None, backpressure_inserter=None, size=None):
    """Test routine for AXI write functionality."""

    tb = TB(dut)  # Instantiate the testbench
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
>>>>>>> refs/remotes/origin/main

    # Determine byte lanes and maximum burst size
    byte_lanes = tb.axi_master.write_if.byte_lanes
    max_burst_size = tb.axi_master.write_if.max_burst_size

    if size is None:
<<<<<<< HEAD
        size = max_burst_size  # Use maximum burst size if no specific size is provided
=======
        size = max_burst_size
>>>>>>> refs/remotes/origin/main

    # Reset the DUT
    await tb.cycle_reset()

    # Set idle and backpressure generators
<<<<<<< HEAD
    tb.set_idle_generator(idle_inserter)  # Apply idle cycles if provided
    tb.set_backpressure_generator(backpressure_inserter)  # Apply backpressure if provided

    # Loop through different lengths and offsets for write transactions
    for length in list(range(1, byte_lanes*2))+[1024]:  # Test a range of lengths plus 1024 bytes
        for offset in list(range(byte_lanes, byte_lanes*2))+list(range(4096-byte_lanes, 4096)):  # Test different offsets
            tb.log.info("length %d, offset %d", length, offset)  # Log the length and offset being tested
            addr = offset+0x1000  # Calculate the address for the transaction
            test_data = bytearray([x % 256 for x in range(length)])  # Generate test data of the specified length

            # Write test data to AXI RAM
            tb.axi_ram.write(addr-128, b'\xaa'*(length+256))  # Write padding around the test data

            # Perform the write transaction
            await tb.axi_master.write(addr, test_data, size=size)  # Write the test data to the specified address

            # Check if the written data matches the test data
            tb.log.debug("%s", tb.axi_ram.hexdump_str((addr & ~0xf)-16, (((addr & 0xf)+length-1) & ~0xf)+48))  # Dump memory content for debugging
            assert tb.axi_ram.read(addr, length) == test_data  # Assert that the data read back matches the data written
            assert tb.axi_ram.read(addr-1, 1) == b'\xaa'  # Check that the padding before the data is unchanged
            assert tb.axi_ram.read(addr+length, 1) == b'\xaa'  # Check that the padding after the data is unchanged

    await RisingEdge(dut.clk)  # Wait for a clock edge
    await RisingEdge(dut.clk)  # Wait for another clock edge

def cycle_pause():
    """Generator for creating idle periods."""
    return itertools.cycle([1, 1, 1, 0])  # Generate a repeating pattern for idle cycles

if cocotb.SIM_NAME:
    # Register the test with cocotb
    factory = TestFactory(run_test_write)  # Create a TestFactory for the write test
    factory.add_option("idle_inserter", [None, cycle_pause])  # Add an option for idle cycles
    factory.add_option("backpressure_inserter", [None, cycle_pause])  # Add an option for backpressure
    factory.add_option("size", [None]+list(range(1, 32)))  # Add an option for burst sizes
    factory.generate_tests()  # Generate tests based on the provided options

# cocotb-test integration

tests_dir = os.path.abspath(os.path.dirname(__file__))  # Get the directory of the current test file
rtl_dir = os.path.abspath(os.path.join(tests_dir, '..', '..', 'responses'))  # Define the directory for RTL files

# Define the pytest function for running the simulation
@pytest.mark.parametrize("delay", [0, 1])  # Parameterize the test for different delays
@pytest.mark.parametrize("data_width", [8, 16, 32])  # Parameterize the test for different data widths
def test_axi_fifo_wr(request, data_width, delay):
    """Pytest configuration for the testbench."""
    dut = "axi_fifo_wr"  # Specify the DUT module name
    module = os.path.splitext(os.path.basename(__file__))[0]  # Get the name of the testbench module
    toplevel = dut  # Set the top-level module in the simulation

    # Specify the Verilog source files for the DUT
    verilog_sources = [
        os.path.join(rtl_dir, f"{dut}.v"),
    ]

    # Define parameters to be passed to the Verilog module
    parameters = {}

    parameters['DATA_WIDTH'] = data_width  # Set the data width parameter
    parameters['ADDR_WIDTH'] = 32  # Set the address width parameter
    parameters['STRB_WIDTH'] = parameters['DATA_WIDTH'] // 8  # Set the strobe width based on data width
    parameters['ID_WIDTH'] = 8  # Set the ID width parameter
    parameters['AWUSER_ENABLE'] = 0  # Disable the AWUSER signal
    parameters['AWUSER_WIDTH'] = 1  # Set the AWUSER width to 1 (irrelevant since disabled)
    parameters['WUSER_ENABLE'] = 0  # Disable the WUSER signal
    parameters['WUSER_WIDTH'] = 1  # Set the WUSER width to 1 (irrelevant since disabled)
    # The following parameters are commented out and could be enabled if needed:
    # parameters['ARUSER_ENABLE'] = 0
    # parameters['ARUSER_WIDTH'] = 1
    # parameters['RUSER_ENABLE'] = 0
    # parameters['RUSER_WIDTH'] = 1
    # parameters['WRITE_FIFO_DEPTH'] = 32
    # parameters['WRITE_FIFO_DELAY'] = delay

    # Extra environment variables for simulation
    extra_env = {f'PARAM_{k}': str(v) for k, v in parameters.items()}

    # Directory for storing simulation build artifacts
    sim_build = os.path.join(tests_dir, "sim_build",
        request.node.name.replace('[', '-').replace(']', ''))

    # Run the simulation with the specified configuration
    cocotb_test.simulator.run(
        python_search=[tests_dir],  # Python search path for test scripts
        verilog_sources=verilog_sources,  # List of Verilog sources to compile
        toplevel=toplevel,  # Top-level Verilog module
        module=module,  # Testbench module
        parameters=parameters,  # Parameters to pass to the Verilog module
        sim_build=sim_build,  # Build directory for simulation
        extra_env=extra_env,  # Extra environment variables
=======
    tb.set_idle_generator(idle_inserter)
    tb.set_backpressure_generator(backpressure_inserter)

    # Loop through different lengths and offsets for write transactions
    for length in list(range(1, byte_lanes*2))+[1024]:
        for offset in list(range(byte_lanes, byte_lanes*2))+list(range(4096-byte_lanes, 4096)):
            tb.log.info("length %d, offset %d", length, offset)
            addr = offset+0x1000
            test_data = bytearray([x % 256 for x in range(length)])

            # Write test data to AXI RAM
            tb.axi_ram.write(addr-128, b'\xaa'*(length+256))

            # Perform the write transaction
            await tb.axi_master.write(addr, test_data, size=size)

            # Check if the written data matches the test data
            tb.log.debug("%s", tb.axi_ram.hexdump_str((addr & ~0xf)-16, (((addr & 0xf)+length-1) & ~0xf)+48))
            assert tb.axi_ram.read(addr, length) == test_data
            assert tb.axi_ram.read(addr-1, 1) == b'\xaa'
            assert tb.axi_ram.read(addr+length, 1) == b'\xaa'

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
def test_axi_fifo_wr(request, data_width, delay):
    """Pytest configuration for the testbench."""
    dut = "axi_fifo_wr"
    module = os.path.splitext(os.path.basename(__file__))[0]
    toplevel = dut

    verilog_sources = [
        os.path.join(rtl_dir, f"{dut}.v"),
        os.path.join(rtl_dir, f"{dut}_wr.v"),
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
    parameters['ARUSER_ENABLE'] = 0
    parameters['ARUSER_WIDTH'] = 1
    parameters['RUSER_ENABLE'] = 0
    parameters['RUSER_WIDTH'] = 1
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
