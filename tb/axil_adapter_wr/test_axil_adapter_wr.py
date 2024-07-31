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

from cocotbext.axi import AxiLiteBus, AxiLiteMaster, AxiLiteRam


class TB(object):
    def __init__(self, dut):
        self.dut = dut

        # Set up logging for debug information
        self.log = logging.getLogger("cocotb.tb")
        self.log.setLevel(logging.DEBUG)

        # Start a clock for the DUT with a period of 10ns
        cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())

        # Initialize AXI-Lite master interface for sending commands
        self.axil_master = AxiLiteMaster(AxiLiteBus.from_prefix(dut, "s_axil"), dut.clk, dut.rst)
        # Initialize AXI-Lite RAM model for memory operations
        self.axil_ram = AxiLiteRam(AxiLiteBus.from_prefix(dut, "m_axil"), dut.clk, dut.rst, size=2**16)

    def set_idle_generator(self, generator=None):
        """Set a generator to pause the AXI transactions for idle periods."""
        if generator:
            self.axil_master.write_if.aw_channel.set_pause_generator(generator())
            self.axil_master.write_if.w_channel.set_pause_generator(generator())
            self.axil_ram.write_if.b_channel.set_pause_generator(generator())

    def set_backpressure_generator(self, generator=None):
        """Set a generator to create backpressure on the AXI bus."""
        if generator:
            self.axil_master.write_if.b_channel.set_pause_generator(generator())
            self.axil_ram.write_if.aw_channel.set_pause_generator(generator())
            self.axil_ram.write_if.w_channel.set_pause_generator(generator())

    async def cycle_reset(self):
        """Reset the DUT."""
        self.dut.rst.setimmediatevalue(0)  # Initially set reset to 0
        await RisingEdge(self.dut.clk)  # Wait for a clock edge
        await RisingEdge(self.dut.clk)
        self.dut.rst.value = 1  # Assert reset
        await RisingEdge(self.dut.clk)
        await RisingEdge(self.dut.clk)
        self.dut.rst.value = 0  # Deassert reset
        await RisingEdge(self.dut.clk)
        await RisingEdge(self.dut.clk)


async def run_test_write(dut, data_in=None, idle_inserter=None, backpressure_inserter=None):
    """Test routine for AXI-Lite write functionality."""

    tb = TB(dut)

    # Determine byte lanes for the write interface
    byte_lanes = tb.axil_master.write_if.byte_lanes

    # Reset the DUT
    await tb.cycle_reset()

    # Set idle and backpressure generators
    tb.set_idle_generator(idle_inserter)
    tb.set_backpressure_generator(backpressure_inserter)

    # Iterate over various lengths and offsets for the write transactions
    for length in range(1, byte_lanes*2):
        for offset in range(byte_lanes):
            tb.log.info("length %d, offset %d", length, offset)
            addr = offset + 0x1000  # Calculate the address with the offset
            test_data = bytearray([x % 256 for x in range(length)])  # Generate test data

            # Write some initial data to the RAM for testing
            tb.axil_ram.write(addr-128, b'\xaa'*(length+256))

            # Perform the write transaction using AXI-Lite master
            await tb.axil_master.write(addr, test_data)

            tb.log.debug("%s", tb.axil_ram.hexdump_str((addr & ~0xf)-16, (((addr & 0xf)+length-1) & ~0xf)+48))

            # Assert that the data written matches the data in the RAM
            assert tb.axil_ram.read(addr, length) == test_data
            assert tb.axil_ram.read(addr-1, 1) == b'\xaa'
            assert tb.axil_ram.read(addr+length, 1) == b'\xaa'

    # Wait for a few clock cycles
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)


def cycle_pause():
    """Generator for creating idle periods."""
    return itertools.cycle([1, 1, 1, 0])  # Create a cycle of pauses


if cocotb.SIM_NAME:
    # Register the write test with cocotb
    factory = TestFactory(run_test_write)
    factory.add_option("idle_inserter", [None, cycle_pause])  # Option to insert idle cycles
    factory.add_option("backpressure_inserter", [None, cycle_pause])  # Option to insert backpressure
    factory.generate_tests()


# cocotb-test

tests_dir = os.path.abspath(os.path.dirname(__file__))
rtl_dir = os.path.abspath(os.path.join(tests_dir, '..', '..', 'responses'))

@pytest.mark.parametrize("m_data_width", [8, 16, 32])
@pytest.mark.parametrize("s_data_width", [8, 16, 32])
def test_axil_adapter_wr(request, s_data_width, m_data_width):
    """Pytest configuration for the testbench."""
    dut = "axil_adapter_wr"  # Name of the DUT module
    module = os.path.splitext(os.path.basename(__file__))[0]
    toplevel = dut

    # List of Verilog sources required for the testbench
    verilog_sources = [
        os.path.join(rtl_dir, f"{dut}.v")
    ]

    parameters = {}

    # Set the parameters for the DUT
    parameters['ADDR_WIDTH'] = 32
    parameters['S_DATA_WIDTH'] = s_data_width
    parameters['S_STRB_WIDTH'] = parameters['S_DATA_WIDTH'] // 8
    parameters['M_DATA_WIDTH'] = m_data_width
    parameters['M_STRB_WIDTH'] = parameters['M_DATA_WIDTH'] // 8

    # Environment variables for passing parameters to the simulator
    extra_env = {f'PARAM_{k}': str(v) for k, v in parameters.items()}

    # Directory for simulation build
    sim_build = os.path.join(tests_dir, "sim_build",
        request.node.name.replace('[', '-').replace(']', ''))

    # Run the cocotb simulation
    cocotb_test.simulator.run(
        python_search=[tests_dir],
        verilog_sources=verilog_sources,
        toplevel=toplevel,
        module=module,
        parameters=parameters,
        sim_build=sim_build,
        extra_env=extra_env,
    )
