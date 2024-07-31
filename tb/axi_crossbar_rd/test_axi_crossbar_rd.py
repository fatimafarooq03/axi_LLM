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
        # Initialize the testbench with the device under test (DUT)
        self.dut = dut

        # Get the number of slave and master interfaces
        s_count = len(dut.axi_crossbar_rd_inst.s_axi_arvalid)
        m_count = len(dut.axi_crossbar_rd_inst.m_axi_arvalid)

        # Set up logging for debugging
        self.log = logging.getLogger("cocotb.tb")
        self.log.setLevel(logging.DEBUG)

        # Start a 10ns clock
        cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())

        # Create AXI master and AXI RAM instances
        self.axi_master = [AxiMaster(AxiBus.from_prefix(dut, f"s{k:02d}_axi"), dut.clk, dut.rst) for k in range(s_count)]
        self.axi_ram = [AxiRam(AxiBus.from_prefix(dut, f"m{k:02d}_axi"), dut.clk, dut.rst, size=2**16) for k in range(m_count)]

        # Initialize bid and rid to prevent X propagation
        for ram in self.axi_ram:
            ram.write_if.b_channel.bus.bid.setimmediatevalue(0)
            ram.read_if.r_channel.bus.rid.setimmediatevalue(0)

    def set_idle_generator(self, generator=None):
        # Set idle cycles in AXI channels
        if generator:
            for master in self.axi_master:
                master.write_if.aw_channel.set_pause_generator(generator())
                master.write_if.w_channel.set_pause_generator(generator())
                master.read_if.ar_channel.set_pause_generator(generator())
            for ram in self.axi_ram:
                ram.write_if.b_channel.set_pause_generator(generator())
                ram.read_if.r_channel.set_pause_generator(generator())

    def set_backpressure_generator(self, generator=None):
        # Set backpressure in AXI channels
        if generator:
            for master in self.axi_master:
                master.write_if.b_channel.set_pause_generator(generator())
                master.read_if.r_channel.set_pause_generator(generator())
            for ram in self.axi_ram:
                ram.write_if.aw_channel.set_pause_generator(generator())
                ram.write_if.w_channel.set_pause_generator(generator())
                ram.read_if.ar_channel.set_pause_generator(generator())

    async def cycle_reset(self):
        # Reset the DUT
        self.dut.rst.setimmediatevalue(0)
        await RisingEdge(self.dut.clk)
        await RisingEdge(self.dut.clk)
        self.dut.rst.value = 1
        await RisingEdge(self.dut.clk)
        await RisingEdge(self.dut.clk)
        self.dut.rst.value = 0
        await RisingEdge(self.dut.clk)
        await RisingEdge(self.dut.clk)


async def run_test_read(dut, data_in=None, idle_inserter=None, backpressure_inserter=None, size=None, s=0, m=0):
    # Function to test read functionality
    tb = TB(dut)

    byte_lanes = tb.axi_master[s].write_if.byte_lanes
    max_burst_size = tb.axi_master[s].write_if.max_burst_size

    if size is None:
        size = max_burst_size

    await tb.cycle_reset()

    tb.set_idle_generator(idle_inserter)
    tb.set_backpressure_generator(backpressure_inserter)

    # Test different lengths and offsets for reading data
    for length in list(range(1, byte_lanes*2))+[1024]:
        for offset in list(range(byte_lanes, byte_lanes*2))+list(range(4096-byte_lanes, 4096)):
            tb.log.info("length %d, offset %d, size %d", length, offset, size)
            ram_addr = offset+0x1000
            addr = ram_addr + m*0x1000000
            test_data = bytearray([x % 256 for x in range(length)])

            tb.axi_ram[m].write(ram_addr, test_data)

            data = await tb.axi_master[s].read(addr, length, size=size)

            assert data.data == test_data

    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)


def cycle_pause():
    # Helper function to create cycle pause generator
    return itertools.cycle([1, 1, 1, 0])


if cocotb.SIM_NAME:
    # If running in a simulation environment, set up test factory and run tests
    s_count = len(cocotb.top.axi_crossbar_rd_inst.s_axi_arvalid)
    m_count = len(cocotb.top.axi_crossbar_rd_inst.m_axi_arvalid)

    data_width = len(cocotb.top.s00_axi_wdata)
    byte_lanes = data_width // 8
    max_burst_size = (byte_lanes-1).bit_length()

    factory = TestFactory(run_test_read)
    factory.add_option("idle_inserter", [None, cycle_pause])
    factory.add_option("backpressure_inserter", [None, cycle_pause])
    factory.add_option("s", range(min(s_count, 2)))
    factory.add_option("m", range(min(m_count, 2)))
    factory.generate_tests()

# cocotb-test integration

tests_dir = os.path.abspath(os.path.dirname(__file__))
rtl_dir = os.path.abspath(os.path.join(tests_dir, '..', '..', 'responses'))

@pytest.mark.parametrize("data_width", [8, 16, 32])
@pytest.mark.parametrize("m_count", [1, 4])
@pytest.mark.parametrize("s_count", [1, 4])
def test_axi_crossbar_rd(request, s_count, m_count, data_width):
    # Pytest function to integrate cocotb tests
    dut = "axi_crossbar_rd"
    wrapper = f"{dut}_wrap_{s_count}x{m_count}"
    module = os.path.splitext(os.path.basename(__file__))[0]
    toplevel = wrapper

    # Generate wrapper file if it does not exist
    wrapper_file = os.path.join(tests_dir, f"{wrapper}.v")
    if not os.path.exists(wrapper_file):
        subprocess.Popen(
            [os.path.join(rtl_dir, f"{dut}_wrap.py"), "-p", f"{s_count}", f"{m_count}"],
            cwd=tests_dir
        ).wait()

    verilog_sources = [
        wrapper_file,
        os.path.join(rtl_dir, f"{dut}.v"),
        os.path.join(rtl_dir, f"{dut}_addr.v"),
        os.path.join(rtl_dir, f"{dut}_rd.v"),
        os.path.join(rtl_dir, "axi_register_rd.v"),
        os.path.join(rtl_dir, "arbiter.v"),
        os.path.join(rtl_dir, "priority_encoder.v"),
    ]

    parameters = {}

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
    parameters['ARUSER_ENABLE'] = 0
    parameters['ARUSER_WIDTH'] = 1
    parameters['RUSER_ENABLE'] = 0
    parameters['RUSER_WIDTH'] = 1
    parameters['M_REGIONS'] = 1

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
