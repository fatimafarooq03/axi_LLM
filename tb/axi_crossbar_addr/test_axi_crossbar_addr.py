import itertools
import logging
import os

import cocotb_test.simulator
import pytest

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge
from cocotb.regression import TestFactory

# Test case definitions: (input address, expected master select, expected region)
# These test cases map specific input addresses to their expected output master select and region
test_cases = [
    (0x00000000, 0, 0),  # Address maps to master 0, region 0
    (0x01000000, 1, 0),  # Address maps to master 1, region 0
    (0x02000000, 2, 0),  # Address maps to master 2, region 0
    (0x03000000, 3, 0),  # Address maps to master 3, region 0
    (0x00010000, 0, 0),  # Address within the same range for master 0, region 0
    (0x01010000, 1, 0),  # Address within the same range for master 1, region 0
    (0xFFFFFFFF, 3, 0),  # Highest address value, should map to the highest master and region
]

class TB:
    def __init__(self, dut):
        """ Testbench class for the DUT (Design Under Test) """
        self.dut = dut
        self.log = logging.getLogger("cocotb.tb")
        self.log.setLevel(logging.DEBUG)

        # Start a clock with a period of 10ns
        cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())

    async def cycle_reset(self):
        """ Cycle the reset signal to initialize the DUT """
        self.dut.rst.setimmediatevalue(0)
        await RisingEdge(self.dut.clk)
        await RisingEdge(self.dut.clk)
        self.dut.rst.value = 1
        await RisingEdge(self.dut.clk)
        await RisingEdge(self.dut.clk)
        self.dut.rst.value = 0
        await RisingEdge(self.dut.clk)
        await RisingEdge(self.dut.clk)

    async def run_test(self, address, expected_m_select, expected_m_axi_aregion):
        """ Run a single test case with the given address and expected results """
        
        # Set the input address and signal valid
        self.dut.s_axi_aaddr.value = address
        self.dut.s_axi_avalid.value = 1

        # Wait for a clock edge and then clear the valid signal
        await RisingEdge(self.dut.clk)
        self.dut.s_axi_avalid.value = 0

        # Wait until the address is ready
        while not self.dut.s_axi_aready.value:
            await RisingEdge(self.dut.clk)

        # Check the outputs against the expected values
        assert self.dut.m_select.value == expected_m_select, f"Address: {hex(address)}, Expected m_select: {expected_m_select}, Got: {self.dut.m_select.value}"
        assert self.dut.m_axi_aregion.value == expected_m_axi_aregion, f"Address: {hex(address)}, Expected m_axi_aregion: {expected_m_axi_aregion}, Got: {self.dut.m_axi_aregion.value}"

        # Log the successful test case
        self.log.info(f"Test passed for address: {hex(address)}")

@cocotb.test()
async def test_axi_crossbar_addr(dut):
    """ Test the axi_crossbar_addr module """

    tb = TB(dut)
    await tb.cycle_reset()

    # Run all test cases
    for address, expected_m_select, expected_m_axi_aregion in test_cases:
        await tb.run_test(address, expected_m_select, expected_m_axi_aregion)

    tb.log.info("All test cases passed!")

# cocotb-test integration
tests_dir = os.path.abspath(os.path.dirname(__file__))
rtl_dir = os.path.abspath(os.path.join(tests_dir, '..', '..', 'responses'))

@pytest.mark.parametrize("parameters", [
    {
        'S': 0,
        'S_COUNT': 4,
        'M_COUNT': 4,
        'ADDR_WIDTH': 32,
        'ID_WIDTH': 8,
        'S_THREADS': 2,
        'S_ACCEPT': 16,
        'M_REGIONS': 1,
        'M_BASE_ADDR': 0,
        'M_ADDR_WIDTH': "{4{{32'd24}}}",
        'M_CONNECT': "{4{{4'b1111}}}",
        'M_SECURE': "{4'b0000}",
        'WC_OUTPUT': 0,
    }
])
def test_axi_crossbar_addr_pytest(request, parameters):
    """ Pytest function for running the cocotb simulation """

    dut = "axi_crossbar_addr"
    module = os.path.splitext(os.path.basename(__file__))[0]
    toplevel = dut

    verilog_sources = [
        os.path.join(rtl_dir, f"{dut}.v"),
    ]

    extra_env = {f'PARAM_{k}': str(v) for k, v in parameters.items()}

    sim_build = os.path.join(tests_dir, "sim_build", request.node.name.replace('[', '-').replace(']', ''))

    cocotb_test.simulator.run(
        python_search=[tests_dir],
        verilog_sources=verilog_sources,
        toplevel=toplevel,
        module=module,
        parameters=parameters,
        sim_build=sim_build,
        extra_env=extra_env,
    )
