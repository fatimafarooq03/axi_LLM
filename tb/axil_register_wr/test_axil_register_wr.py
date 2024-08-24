import itertools
import logging
import os
import random

import cocotb_test.simulator  # Import cocotb's simulator integration with pytest
import pytest  # Import pytest for parameterized test execution

import cocotb  # Import cocotb for co-simulation
from cocotb.clock import Clock  # Import Clock for generating clock signals
from cocotb.triggers import RisingEdge, Timer  # Import triggers for synchronizing with clock edges
from cocotb.regression import TestFactory  # Import TestFactory for generating tests

from cocotbext.axi import AxiLiteBus, AxiLiteMaster, AxiLiteRam  # Import AXI-Lite interfaces from cocotb extension

# Define the testbench class (TB) for managing the simulation environment
class TB(object):
    def __init__(self, dut):
        self.dut = dut  # Store a reference to the Device Under Test (DUT)

        # Set up logging for detailed debug information
        self.log = logging.getLogger("cocotb.tb")  # Create a logger specific to the testbench
        self.log.setLevel(logging.DEBUG)  # Set logging level to DEBUG to capture detailed logs

        # Start a clock for the DUT with a period of 10ns
        cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())  # Launch a clock generator for the DUT

        # Initialize AXI-Lite master interface for sending read commands
        # The AxiLiteMaster is connected to the s_axil interface of the DUT
        self.axil_master = AxiLiteMaster(AxiLiteBus.from_prefix(dut, "s_axil"), dut.clk, dut.rst)
        
        # Initialize AXI-Lite RAM model for memory operations
        # The AxiLiteRam is connected to the m_axil interface of the DUT
        self.axil_ram = AxiLiteRam(AxiLiteBus.from_prefix(dut, "m_axil"), dut.clk, dut.rst, size=2**16)

    def set_idle_generator(self, generator=None):
        """Set a generator to introduce idle periods in the AXI transactions."""
        if generator:
            # Apply the idle generator to the read channels of the AXI-Lite master and RAM
            self.axil_master.read_if.ar_channel.set_pause_generator(generator())
            self.axil_ram.read_if.r_channel.set_pause_generator(generator())

    def set_backpressure_generator(self, generator=None):
        """Set a generator to create backpressure on the AXI-Lite bus."""
        if generator:
            # Apply the backpressure generator to the read response channels
            self.axil_master.read_if.r_channel.set_pause_generator(generator())
            self.axil_ram.read_if.ar_channel.set_pause_generator(generator())

    async def cycle_reset(self):
        """Reset the DUT by toggling the reset signal."""
        self.dut.rst.setimmediatevalue(0)  # Deassert reset initially
        await RisingEdge(self.dut.clk)  # Wait for a rising clock edge
        await RisingEdge(self.dut.clk)  # Wait for another clock edge
        self.dut.rst.value = 1  # Assert reset signal
        await RisingEdge(self.dut.clk)  # Wait for a clock edge while reset is asserted
        await RisingEdge(self.dut.clk)  # Wait for another clock edge with reset asserted
        self.dut.rst.value = 0  # Deassert reset signal
        await RisingEdge(self.dut.clk)  # Wait for a clock edge after reset is deasserted
        await RisingEdge(self.dut.clk)  # Wait for another clock edge after reset

# Define the main test routine for AXI-Lite read functionality
async def run_test_read(dut, data_in=None, idle_inserter=None, backpressure_inserter=None):
    """Test routine for AXI-Lite read functionality."""

    tb = TB(dut)  # Instantiate the testbench with the DUT

    byte_lanes = tb.axil_master.read_if.byte_lanes  # Determine the number of byte lanes on the AXI-Lite read interface

    # Reset the DUT
    await tb.cycle_reset()  # Perform a reset before starting the test

    # Set idle and backpressure generators if provided
    tb.set_idle_generator(idle_inserter)  # Apply idle cycles to the AXI-Lite interface
    tb.set_backpressure_generator(backpressure_inserter)  # Apply backpressure to the AXI-Lite interface

    # Iterate over various lengths and offsets for the read transactions
    for length in range(1, byte_lanes * 2):  # Test with different data lengths
        for offset in range(byte_lanes):  # Test with different address offsets
            tb.log.info("length %d, offset %d", length, offset)  # Log the current test configuration
            addr = offset + 0x1000  # Calculate the address using the offset
            test_data = bytearray([x % 256 for x in range(length)])  # Generate test data with a repeating pattern

            # Write test data to the AXI RAM at the calculated address
            tb.axil_ram.write(addr, test_data)

            # Perform the read transaction from the same address
            data = await tb.axil_master.read(addr, length)

            # Verify that the read data matches the test data
            assert data.data == test_data  # Check that the data read back is the same as what was written

    await RisingEdge(dut.clk)  # Wait for a clock edge at the end of the test
    await RisingEdge(dut.clk)  # Wait for another clock edge at the end of the test

# Define a generator for creating idle periods in the AXI-Lite transactions
def cycle_pause():
    """Generator for creating idle periods."""
    return itertools.cycle([1, 1, 1, 0])  # Generate a repeating pattern of idle cycles

# Register the test with cocotb if the simulation environment is active
if cocotb.SIM_NAME:
    factory = TestFactory(run_test_read)  # Create a TestFactory for the read test
    factory.add_option("idle_inserter", [None, cycle_pause])  # Optionally insert idle cycles
    factory.add_option("backpressure_inserter", [None, cycle_pause])  # Optionally insert backpressure
    factory.generate_tests()  # Generate the test cases based on the provided options

# cocotb-test integration with pytest

tests_dir = os.path.abspath(os.path.dirname(__file__))  # Get the directory of the current test file
rtl_dir = os.path.abspath(os.path.join(tests_dir, '..', '..', 'responses'))  # Define the directory for RTL files

# Define the pytest function for running the simulation
@pytest.mark.parametrize("reg_type", [0, 1, 2])  # Parameterize the test for different register types
@pytest.mark.parametrize("data_width", [8, 16, 32])  # Parameterize the test for different data widths
def test_axil_register_rd(request, data_width, reg_type):
    """Pytest configuration for the AXI-Lite register read testbench."""
    dut = "axil_register_rd"  # Specify the DUT module name
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
    parameters['AR_REG_TYPE'] = reg_type  # Set the type of register used for address reads
    parameters['R_REG_TYPE'] = reg_type  # Set the type of register used for read data

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
    )
