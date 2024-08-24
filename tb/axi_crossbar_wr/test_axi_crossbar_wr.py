import itertools
import logging
import os
import random
import subprocess

import cocotb_test.simulator
import pytest

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer
from cocotb.regression import TestFactory

from cocotbext.axi import AxiBus, AxiMaster, AxiRam

class TB(object):
    def __init__(self, dut):
        # Initialize the testbench class with the DUT (Device Under Test)
        self.dut = dut

        # Determine the number of AXI slave and master interfaces based on the DUT signals
        s_count = len(dut.s_axi_awvalid)
        m_count = len(dut.m_axi_awvalid)

        # Setup a logger for the testbench with debugging enabled
        self.log = logging.getLogger("cocotb.tb")
        self.log.setLevel(logging.DEBUG)

        # Start a 10ns clock on the 'clk' signal of the DUT
        cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())

        # Initialize AXI Master interfaces for each slave interface on the DUT
        self.axi_master = [AxiMaster(AxiBus.from_prefix(dut, f"s{k:02d}_axi"), dut.clk, dut.rst) for k in range(s_count)]
        
        # Initialize AXI RAM instances for each master interface on the DUT
        self.axi_ram = [AxiRam(AxiBus.from_prefix(dut, f"m{k:02d}_axi"), dut.clk, dut.rst, size=2**16) for k in range(m_count)]

        # Set initial values for 'bid' and 'rid' to prevent X propagation in simulation
        for ram in self.axi_ram:
            ram.write_if.b_channel.bus.bid.setimmediatevalue(0)
            ram.read_if.r_channel.bus.rid.setimmediatevalue(0)

    def set_idle_generator(self, generator=None):
        # Method to introduce idle cycles in AXI channels if a generator function is provided
        if generator:
            for master in self.axi_master:
                master.write_if.aw_channel.set_pause_generator(generator())
                master.write_if.w_channel.set_pause_generator(generator())
                master.read_if.ar_channel.set_pause_generator(generator())
            for ram in self.axi_ram:
                ram.write_if.b_channel.set_pause_generator(generator())
                ram.read_if.r_channel.set_pause_generator(generator())

    def set_backpressure_generator(self, generator=None):
        # Method to introduce backpressure in AXI channels if a generator function is provided
        if generator:
            for master in self.axi_master:
                master.write_if.b_channel.set_pause_generator(generator())
                master.read_if.r_channel.set_pause_generator(generator())
            for ram in self.axi_ram:
                ram.write_if.aw_channel.set_pause_generator(generator())
                ram.write_if.w_channel.set_pause_generator(generator())
                ram.read_if.ar_channel.set_pause_generator(generator())

    async def cycle_reset(self):
        # Method to reset the DUT by cycling the reset signal ('rst')
        self.dut.rst.setimmediatevalue(0)  # Set reset to 0 initially
        await RisingEdge(self.dut.clk)     # Wait for two rising edges of the clock
        await RisingEdge(self.dut.clk)
        self.dut.rst.value = 1             # Set reset to 1 (active)
        await RisingEdge(self.dut.clk)     # Wait for two more rising edges
        await RisingEdge(self.dut.clk)
        self.dut.rst.value = 0             # De-assert the reset (back to 0)
        await RisingEdge(self.dut.clk)     # Wait for two rising edges to complete reset cycle
        await RisingEdge(self.dut.clk)


async def run_test_write(dut, data_in=None, idle_inserter=None, backpressure_inserter=None, size=None, s=0, m=0):
    # Function to run write tests on the DUT
    tb = TB(dut)  # Create an instance of the testbench

    byte_lanes = tb.axi_master[s].write_if.byte_lanes  # Get the number of byte lanes for the selected slave interface
    max_burst_size = tb.axi_master[s].write_if.max_burst_size  # Get the maximum burst size for the selected slave interface

    if size is None:
        size = max_burst_size  # If size is not provided, use the maximum burst size

    await tb.cycle_reset()  # Perform a reset cycle on the DUT

    tb.set_idle_generator(idle_inserter)  # Set idle cycle generator if provided
    tb.set_backpressure_generator(backpressure_inserter)  # Set backpressure generator if provided

    # Loop through different lengths and offsets for writing data to test the DUT's behavior
    for length in list(range(1, byte_lanes*2))+[1024]:
        for offset in list(range(byte_lanes, byte_lanes*2))+list(range(4096-byte_lanes, 4096)):
            tb.log.info("length %d, offset %d, size %d", length, offset, size)
            ram_addr = offset+0x1000  # Calculate the RAM address for the write
            addr = ram_addr + m*0x1000000  # Calculate the actual address with an offset for the master interface
            test_data = bytearray([x % 256 for x in range(length)])  # Generate test data

            tb.axi_ram[m].write(ram_addr-128, b'\xaa'*(length+256))  # Pre-fill RAM with known data

            await tb.axi_master[s].write(addr, test_data, size=size)  # Write test data to the DUT

            tb.log.debug("%s", tb.axi_ram[m].hexdump_str((ram_addr & ~0xf)-16, (((ram_addr & 0xf)+length-1) & ~0xf)+48))

            # Assertions to verify correct data was written
            assert tb.axi_ram[m].read(ram_addr, length) == test_data
            assert tb.axi_ram[m].read(ram_addr-1, 1) == b'\xaa'
            assert tb.axi_ram[m].read(ram_addr+length, 1) == b'\xaa'

    await RisingEdge(dut.clk)  # Wait for two rising edges after the test is complete
    await RisingEdge(dut.clk)


def cycle_pause():
    # Generator function to create a pause cycle pattern
    return itertools.cycle([1, 1, 1, 0])  # Introduce pauses every 4th cycle


if cocotb.SIM_NAME:
    # If running in a simulation environment, set up test factory and run tests
    s_count = len(cocotb.top.s_axi_awvalid)  # Get the number of slave interfaces
    m_count = len(cocotb.top.m_axi_awvalid)  # Get the number of master interfaces

    data_width = len(cocotb.top.s_axi_wdata)  # Determine the data width from the slave interface
    byte_lanes = data_width // 8  # Calculate the number of byte lanes
    max_burst_size = (byte_lanes-1).bit_length()  # Calculate the maximum burst size

    # Create a test factory for running multiple test cases with different configurations
    factory = TestFactory(run_test_write)
    factory.add_option("idle_inserter", [None, cycle_pause])  # Add idle cycle generator as an option
    factory.add_option("backpressure_inserter", [None, cycle_pause])  # Add backpressure generator as an option
    factory.add_option("s", range(min(s_count, 2)))  # Test using up to 2 slave interfaces
    factory.add_option("m", range(min(m_count, 2)))  # Test using up to 2 master interfaces
    factory.generate_tests()  # Generate test cases based on these configurations

# cocotb-test integration
tests_dir = os.path.abspath(os.path.dirname(__file__))  # Get the directory for test files
rtl_dir = os.path.abspath(os.path.join(tests_dir, '..', '..', 'responses'))  # Define the RTL directory

@pytest.mark.parametrize("data_width", [8, 16, 32])
@pytest.mark.parametrize("m_count", [1, 4])
@pytest.mark.parametrize("s_count", [1, 4])
def test_axi_crossbar_wr(request, s_count, m_count, data_width):
    # Pytest function to integrate cocotb tests
    dut = "axi_crossbar_wr"  # Set the DUT module name
    module = os.path.splitext(os.path.basename(__file__))[0]  # Get the current script name (without extension)
    toplevel = dut  # Use the DUT module as the top-level module

    verilog_sources = [
        os.path.join(rtl_dir, f"{dut}.v"),  # Main Verilog file for DUT
        os.path.join(rtl_dir, "axi_crossbar_addr.v"),  # AXI crossbar address module
        os.path.join(rtl_dir, "axi_register_wr.v"),  # AXI register write module
        os.path.join(rtl_dir, "arbiter.v"),  # Arbiter module
        os.path.join(rtl_dir, "priority_encoder.v"),  # Priority encoder module
    ]

    parameters = {}

    # Define parameters to be passed to the simulation
    parameters['S_COUNT'] = s_count
    parameters['M_COUNT'] = m_count
    parameters['DATA_WIDTH'] = data_width
    parameters['ADDR_WIDTH'] = 32
    parameters['STRB_WIDTH'] = parameters['DATA_WIDTH'] // 8
    parameters['S_ID_WIDTH'] = 8
    parameters['M_ID_WIDTH'] = parameters['S_ID_WIDTH'] + (s_count-1).bit_length()
    parameters['AWUSER_ENABLE'] = 0
    parameters['AWUSER_WIDTH'] = 1
    parameters['WUSER_ENABLE'] = 0
    parameters['WUSER_WIDTH'] = 1
    parameters['BUSER_ENABLE'] = 0
    parameters['BUSER_WIDTH'] = 1
    parameters['M_REGIONS'] = 1

    extra_env = {f'PARAM_{k}': str(v) for k, v in parameters.items()}  # Pass parameters as environment variables

    # Define the simulation build directory
    sim_build = os.path.join(tests_dir, "sim_build",
        request.node.name.replace('[', '-').replace(']', ''))

    # Run the simulation using cocotb_test
    cocotb_test.simulator.run(
        python_search=[tests_dir],
        verilog_sources=verilog_sources,
        toplevel=toplevel,
        module=module,
        parameters=parameters,
        sim_build=sim_build,
        extra_env=extra_env,
    )
