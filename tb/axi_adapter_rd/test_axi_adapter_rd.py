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

class CustomAxiBus:
    def __init__(self, entity, prefix="s_axi", is_master=True):
        # AR Channel
        self.arid = getattr(entity, f"{prefix}_arid")
        self.araddr = getattr(entity, f"{prefix}_araddr")
        self.arlen = getattr(entity, f"{prefix}_arlen")
        self.arsize = getattr(entity, f"{prefix}_arsize")
        self.arburst = getattr(entity, f"{prefix}_arburst")
        self.arlock = getattr(entity, f"{prefix}_arlock")
        self.arcache = getattr(entity, f"{prefix}_arcache")
        self.arprot = getattr(entity, f"{prefix}_arprot")
        self.arqos = getattr(entity, f"{prefix}_arqos")
        self.arregion = getattr(entity, f"{prefix}_arregion")
        self.aruser = getattr(entity, f"{prefix}_aruser", None)  # Optional signal
        self.arvalid = getattr(entity, f"{prefix}_arvalid")
        self.arready = getattr(entity, f"{prefix}_arready")
        
        # R Channel
        self.rid = getattr(entity, f"{prefix}_rid")
        self.rdata = getattr(entity, f"{prefix}_rdata")
        self.rresp = getattr(entity, f"{prefix}_rresp")
        self.rlast = getattr(entity, f"{prefix}_rlast")
        self.ruser = getattr(entity, f"{prefix}_ruser", None)  # Optional signal
        self.rvalid = getattr(entity, f"{prefix}_rvalid")
        self.rready = getattr(entity, f"{prefix}_rready")

        # For master, swap the ready and valid signals
        if is_master:
            self.arvalid, self.arready = self.arready, self.arvalid
            self.rvalid, self.rready = self.rready, self.rvalid


class TB(object):
    def __init__(self, dut):
        self.dut = dut

        self.log = logging.getLogger("cocotb.tb")
        self.log.setLevel(logging.DEBUG)

        cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())

        master_bus = AxiBus()
        # AR Channel
        self.arid = dut.s_axi_arid 
        self.araddr = dut.s_axi_arid
        self.arlen = getattr(entity, f"{prefix}_arlen")
        self.arsize = getattr(entity, f"{prefix}_arsize")
        self.arburst = getattr(entity, f"{prefix}_arburst")
        self.arlock = getattr(entity, f"{prefix}_arlock")
        self.arcache = getattr(entity, f"{prefix}_arcache")
        self.arprot = getattr(entity, f"{prefix}_arprot")
        self.arqos = getattr(entity, f"{prefix}_arqos")
        self.arregion = getattr(entity, f"{prefix}_arregion")
        self.aruser = getattr(entity, f"{prefix}_aruser", None)  # Optional signal
        self.arvalid = getattr(entity, f"{prefix}_arvalid")
        self.arready = getattr(entity, f"{prefix}_arready")
        
        # R Channel
        self.rid = getattr(entity, f"{prefix}_rid")
        self.rdata = getattr(entity, f"{prefix}_rdata")
        self.rresp = getattr(entity, f"{prefix}_rresp")
        self.rlast = getattr(entity, f"{prefix}_rlast")
        self.ruser = getattr(entity, f"{prefix}_ruser", None)  # Optional signal
        self.rvalid = getattr(entity, f"{prefix}_rvalid")
        self.rready = getattr(entity, f"{prefix}_rready")

        # self.axi_master = AxiMaster(AxiBus.from_prefix(dut, "s_axi"), dut.clk, dut.rst)
        # self.axi_ram = AxiRam(AxiBus.from_prefix(dut, "m_axi"), dut.clk, dut.rst, size=2**16)


    def set_idle_generator(self, generator=None):
        if generator:
            self.axi_master.read_if.ar_channel.set_pause_generator(generator())
            self.axi_ram.read_if.r_channel.set_pause_generator(generator())

    def set_backpressure_generator(self, generator=None):
        if generator:
            self.axi_master.read_if.r_channel.set_pause_generator(generator())
            self.axi_ram.read_if.ar_channel.set_pause_generator(generator())

    async def cycle_reset(self):
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
    tb = TB(dut)

    byte_lanes = tb.axi_master.read_if.byte_lanes
    max_burst_size = tb.axi_master.read_if.max_burst_size

    if size is None:
        size = max_burst_size

    await tb.cycle_reset()

    tb.set_idle_generator(idle_inserter)
    tb.set_backpressure_generator(backpressure_inserter)

    for length in list(range(1, byte_lanes * 2)) + [1024]:
        for offset in list(range(byte_lanes, byte_lanes * 2)) + [4096 - byte_lanes]:
            tb.log.info("length %d, offset %d, size %d", length, offset, size)
            addr = offset + 0x1000
            test_data = bytearray([x % 256 for x in range(length)])

            tb.axi_ram.write(addr, test_data)

            data = await tb.axi_master.read(addr, length, size=size)

            assert data.data == test_data

    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)


def cycle_pause():
    return itertools.cycle([1, 1, 1, 0])


if cocotb.SIM_NAME:

    data_width = len(cocotb.top.s_axi_rdata)
    byte_lanes = data_width // 8
    max_burst_size = (byte_lanes - 1).bit_length()

    factory = TestFactory(run_test_read)
    factory.add_option("idle_inserter", [None, cycle_pause])
    factory.add_option("backpressure_inserter", [None, cycle_pause])
    factory.add_option("size", [None] + list(range(max_burst_size)))
    factory.generate_tests()


# cocotb-test

tests_dir = os.path.abspath(os.path.dirname(__file__))
responses_dir = os.path.abspath(os.path.join(tests_dir, '..', '..', 'responses'))


@pytest.mark.parametrize("m_data_width", [8, 16, 32])
@pytest.mark.parametrize("s_data_width", [8, 16, 32])
def test_axi_adapter_rd(request, s_data_width, m_data_width):
    dut = "axi_adapter_rd"
    module = os.path.splitext(os.path.basename(__file__))[0]
    toplevel = dut

    verilog_sources = [
        os.path.join(responses_dir, f"{dut}.v"),
    ]

    parameters = {}

    parameters['ADDR_WIDTH'] = 32
    parameters['S_DATA_WIDTH'] = s_data_width
    parameters['S_STRB_WIDTH'] = parameters['S_DATA_WIDTH'] // 8
    
    parameters['M_DATA_WIDTH'] = m_data_width
    parameters['M_STRB_WIDTH'] = parameters['M_DATA_WIDTH'] // 8
    
    parameters['ID_WIDTH'] = 8
    
    # parameters['AWUSER_ENABLE'] = 0
    # parameters['AWUSER_WIDTH'] = 1
    # parameters['WUSER_ENABLE'] = 0
   # parameters['WUSER_WIDTH'] = 1
    # parameters['BUSER_ENABLE'] = 0
   # parameters['BUSER_WIDTH'] = 1
    parameters['ARUSER_ENABLE'] = 0
    parameters['ARUSER_WIDTH'] = 1
    parameters['RUSER_ENABLE'] = 0
    parameters['RUSER_WIDTH'] = 1
    parameters['CONVERT_BURST'] = 1
    parameters['CONVERT_NARROW_BURST'] = 1
    parameters['FORWARD_ID'] = 1

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
