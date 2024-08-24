import itertools
import logging
import os
import random

import cocotb_test.simulator
import pytest

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer
from cocotb.regression import TestFactory

from cocotbext.axi import AxiBus, AxiMaster, AxiRam

class TB(object):
    def __init__(self, dut):
        # Initialize the testbench with the device under test (DUT)
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

    def set_idle_generator(self, generator=None):
        """Set a generator to pause the AXI transactions for idle periods."""
        if generator:
            self.axi_master.write_if.aw_channel.set_pause_generator(generator())
            self.axi_master.write_if.w_channel.set_pause_generator(generator())
            self.axi_master.read_if.ar_channel.set_pause_generator(generator())
            self.axi_ram.write_if.b_channel.set_pause_generator(generator())
            self.axi_ram.read_if.r_channel.set_pause_generator(generator())

    def set_backpressure_generator(self, generator=None):
        """Set a generator to create backpressure on the AXI bus."""
        if generator:
            self.axi_master.write_if.b_channel.set_pause_generator(generator())
            self.axi_master.read_if.r_channel.set_pause_generator(generator())
            self.axi_ram.write_if.aw_channel.set_pause_generator(generator())
            self.axi_ram.write_if.w_channel.set_pause_generator(generator())
            self.axi_ram.read_if.ar_channel.set_pause_generator(generator())

    async def cycle_reset(self):
        """Reset the DUT."""
        self.dut.rst.setimmediatevalue(0)  # Deassert reset initially
        await RisingEdge(self.dut.clk)
        await RisingEdge(self.dut.clk)
        self.dut.rst.value = 1  # Assert reset signal
        await RisingEdge(self.dut.clk)
        await RisingEdge(self.dut.clk)
        self.dut.rst.value = 0  # Deassert reset signal
        await RisingEdge(self.dut.clk)
        await RisingEdge(self.dut.clk)

async def run_test_read(dut, data_in=None, idle_inserter=None, backpressure_inserter=None, size=None):
    """Test routine for AXI read functionality."""

    # Instantiate the testbench class with the DUT
    tb = TB(dut)

    # Determine byte lanes and maximum burst size for the AXI master interface
    byte_lanes = tb.axi_master.write_if.byte_lanes
    max_burst_size = tb.axi_master.write_if.max_burst_size

    if size is None:
        size = max_burst_size

    # Reset the DUT
    await tb.cycle_reset()

    # Set idle and backpressure generators if provided
    tb.set_idle_generator(idle_inserter)
    tb.set_backpressure_generator(backpressure_inserter)

    # Loop through different lengths and offsets for read transactions
    for length in list(range(1, byte_lanes*2))+[1024]:
        for offset in list(range(byte_lanes, byte_lanes*2))+list(range(4096-byte_lanes, 4096)):
            tb.log.info("length %d, offset %d", length, offset)
            addr = offset+0x1000
            test_data = bytearray([x % 256 for x in range(length)])

            # Write test data to AXI RAM at the specified address
            tb.axi_ram.write(addr, test_data)

            # Perform the read transaction from the AXI master
            data = await tb.axi_master.read(addr, length, size=size)

            # Check if the read data matches the test data
            assert data.data == test_data

    # Wait for a few clock cycles to ensure all transactions are completed
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)

def cycle_pause():
    """Generator for creating idle periods."""
    return itertools.cycle([1, 1, 1, 0])  # Create a pattern for idle cycles

if cocotb.SIM_NAME:
    # Register the test with cocotb
    factory = TestFactory(run_test_read)
    factory.add_option("idle_inserter", [None, cycle_pause])  # Add option for idle periods
    factory.add_option("backpressure_inserter", [None, cycle_pause])  # Add option for backpressure
    factory.add_option("size", [None]+list(range(1, 32)))  # Specify different burst sizes to test
    factory.generate_tests()  # Generate test cases based on the provided options

# cocotb-test integration

tests_dir = os.path.abspath(os.path.dirname(__file__))  # Get the directory of the current test
rtl_dir = os.path.abspath(os.path.join(tests_dir, '..', '..', 'responses'))  # Define the RTL directory

@pytest.mark.parametrize("delay", [0, 1])  # Parametrize the test to run with and without delay
@pytest.mark.parametrize("data_width", [8, 16, 32])  # Parametrize the test for different data widths
def test_axi_fifo_rd(request, data_width, delay):
    """Pytest configuration for the testbench."""
    dut = "axi_fifo_rd"  # Specify the name of the DUT
    module = os.path.splitext(os.path.basename(__file__))[0]  # Get the name of the current testbench module
    toplevel = dut  # Set the top-level module in the simulation

    # List of Verilog sources to be used in the simulation
    verilog_sources = [
        os.path.join(rtl_dir, f"{dut}.v"),
    ]

    # Parameters to be passed to the Verilog module
    parameters = {}

    parameters['DATA_WIDTH'] = data_width  # Set the data width parameter
    parameters['ADDR_WIDTH'] = 32  # Set the address width parameter
    parameters['STRB_WIDTH'] = parameters['DATA_WIDTH'] // 8  # Set the strobe width based on data width
    parameters['ID_WIDTH'] = 8  # Set the ID width parameter
    parameters['ARUSER_ENABLE'] = 0  # Disable the ARUSER signal
    parameters['ARUSER_WIDTH'] = 1  # Set the ARUSER width to 1 (since it's disabled, width is irrelevant)
    parameters['RUSER_ENABLE'] = 0  # Disable the RUSER signal
    parameters['RUSER_WIDTH'] = 1  # Set the RUSER width to 1 (since it's disabled, width is irrelevant)

    # Additional environment variables for the simulation
    extra_env = {f'PARAM_{k}': str(v) for k, v in parameters.items()}

    # Directory to store simulation build artifacts
    sim_build = os.path.join(tests_dir, "sim_build",
        request.node.name.replace('[', '-').replace(']', ''))

    # Run the simulation with the specified configuration
    cocotb_test.simulator.run(
        python_search=[tests_dir],
        verilog_sources=verilog_sources,
        toplevel=toplevel,
        module=module,
        parameters=parameters,
        sim_build=sim_build,
        extra_env=extra_env,
    )
