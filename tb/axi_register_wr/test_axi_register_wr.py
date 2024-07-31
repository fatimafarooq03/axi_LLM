import itertools
import logging
import os

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
        self.axi_ram = AxiRam(AxiBus.from_prefix(dut, "m_axi"), dut.clk, dut.rst, size=2**16)

    def set_idle_generator(self, generator=None):
        """Set a generator to pause the AXI transactions for idle periods."""
        if generator:
            self.axi_master.write_if.aw_channel.set_pause_generator(generator())
            self.axi_master.write_if.w_channel.set_pause_generator(generator())
            self.axi_ram.write_if.b_channel.set_pause_generator(generator())

    def set_backpressure_generator(self, generator=None):
        """Set a generator to create backpressure on the AXI bus."""
        if generator:
            self.axi_master.write_if.b_channel.set_pause_generator(generator())
            self.axi_ram.write_if.aw_channel.set_pause_generator(generator())
            self.axi_ram.write_if.w_channel.set_pause_generator(generator())

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
            tb.axi_ram.write(addr - 128, b'\xaa' * (length + 256))

            # Perform the write transaction
            await tb.axi_master.write(addr, test_data, size=size)

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
    )
