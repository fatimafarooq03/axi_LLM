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

        # Initialize AXI-Lite master interface for sending read commands
        self.axil_master = AxiLiteMaster(AxiLiteBus.from_prefix(dut, "s_axil"), dut.clk, dut.rst)
        # Initialize AXI-Lite RAM model for memory operations
        self.axil_ram = AxiLiteRam(AxiLiteBus.from_prefix(dut, "m_axil"), dut.clk, dut.rst, size=2**16)

    def set_idle_generator(self, generator=None):
        """Set a generator to pause the AXI transactions for idle periods."""
        if generator:
            self.axil_master.read_if.ar_channel.set_pause_generator(generator())
            self.axil_ram.read_if.r_channel.set_pause_generator(generator())

    def set_backpressure_generator(self, generator=None):
        """Set a generator to create backpressure on the AXI bus."""
        if generator:
            self.axil_master.read_if.r_channel.set_pause_generator(generator())
            self.axil_ram.read_if.ar_channel.set_pause_generator(generator())

    async def cycle_reset(self):
        """Reset the DUT."""
        self.dut.rst.setimmediatevalue(0)
        await RisingEdge(self.dut.clk)
        await RisingEdge(self.dut.clk)
        self.dut.rst.value = 1
        await RisingEdge(self.dut.clk)
        await RisingEdge(self.dut.clk)
        self.dut.rst.value = 0
        await RisingEdge(self.dut.clk)
        await RisingEdge(self.dut.clk)


async def run_test_read(dut, data_in=None, idle_inserter=None, backpressure_inserter=None):
    """Test routine for AXI-Lite read functionality."""

    tb = TB(dut)

    byte_lanes = tb.axil_master.read_if.byte_lanes  # Determine byte lanes for the read interface

    # Reset the DUT
    await tb.cycle_reset()

    # Set idle and backpressure generators
    tb.set_idle_generator(idle_inserter)
    tb.set_backpressure_generator(backpressure_inserter)

    # Iterate over various lengths and offsets for the read transactions
    for length in range(1, byte_lanes*2):
        for offset in range(byte_lanes):
            tb.log.info("length %d, offset %d", length, offset)
            addr = offset + 0x1000  # Calculate the address with the offset
            test_data = bytearray([x % 256 for x in range(length)])  # Generate test data

            # Write test data to AXI RAM
            tb.axil_ram.write(addr, test_data)

            # Perform the read transaction
            data = await tb.axil_master.read(addr, length)

            # Verify that the read data matches the test data
            assert data.data == test_data

    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)


def cycle_pause():
    """Generator for creating idle periods."""
    return itertools.cycle([1, 1, 1, 0])


if cocotb.SIM_NAME:

    factory = TestFactory(run_test_read)
    factory.add_option("idle_inserter", [None, cycle_pause])
    factory.add_option("backpressure_inserter", [None, cycle_pause])
    factory.generate_tests()


# cocotb-test

tests_dir = os.path.abspath(os.path.dirname(__file__))
rtl_dir = os.path.abspath(os.path.join(tests_dir, '..', '..', 'responses'))


@pytest.mark.parametrize("reg_type", [0, 1, 2])
@pytest.mark.parametrize("data_width", [8, 16, 32])
def test_axil_register_rd(request, data_width, reg_type):
    dut = "axil_register_rd"
    module = os.path.splitext(os.path.basename(__file__))[0]
    toplevel = dut

    verilog_sources = [
        os.path.join(rtl_dir, f"{dut}.v")
    ]

    parameters = {}

    parameters['DATA_WIDTH'] = data_width
    parameters['ADDR_WIDTH'] = 32
    parameters['STRB_WIDTH'] = parameters['DATA_WIDTH'] // 8
    parameters['AR_REG_TYPE'] = reg_type
    parameters['R_REG_TYPE'] = reg_type

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
    )
