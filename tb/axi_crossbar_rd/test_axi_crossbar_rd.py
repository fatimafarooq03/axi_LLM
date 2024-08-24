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

<<<<<<< HEAD
        # Get the number of AXI slave and master interfaces from the DUT
        s_count = len(dut.s_axi_arvalid)
        m_count = len(dut.m_axi_arvalid)

        # Set up logging for the testbench with DEBUG level verbosity
        self.log = logging.getLogger("cocotb.tb")
        self.log.setLevel(logging.DEBUG)

        # Start a 10ns clock for the DUT
        cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())

        # Create AXI master and AXI RAM instances for each slave and master interface
        self.axi_master = [AxiMaster(AxiBus.from_prefix(dut, f"s{k:02d}_axi"), dut.clk, dut.rst) for k in range(s_count)]
        self.axi_ram = [AxiRam(AxiBus.from_prefix(dut, f"m{k:02d}_axi"), dut.clk, dut.rst, size=2**16) for k in range(m_count)]

        # Initialize the bid and rid fields in the RAM interface to prevent X (undefined) propagation
=======
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
>>>>>>> refs/remotes/origin/main
        for ram in self.axi_ram:
            ram.write_if.b_channel.bus.bid.setimmediatevalue(0)
            ram.read_if.r_channel.bus.rid.setimmediatevalue(0)

    def set_idle_generator(self, generator=None):
<<<<<<< HEAD
        # Set the idle cycle generator for the AXI channels
        # This introduces idle cycles (delays) in the communication
=======
        # Set idle cycles in AXI channels
>>>>>>> refs/remotes/origin/main
        if generator:
            for master in self.axi_master:
                master.write_if.aw_channel.set_pause_generator(generator())
                master.write_if.w_channel.set_pause_generator(generator())
                master.read_if.ar_channel.set_pause_generator(generator())
            for ram in self.axi_ram:
                ram.write_if.b_channel.set_pause_generator(generator())
                ram.read_if.r_channel.set_pause_generator(generator())

    def set_backpressure_generator(self, generator=None):
<<<<<<< HEAD
        # Set the backpressure generator for the AXI channels
        # This simulates the effect of backpressure in the communication, where the receiver
        # is temporarily unable to accept more data, causing delays
=======
        # Set backpressure in AXI channels
>>>>>>> refs/remotes/origin/main
        if generator:
            for master in self.axi_master:
                master.write_if.b_channel.set_pause_generator(generator())
                master.read_if.r_channel.set_pause_generator(generator())
            for ram in self.axi_ram:
                ram.write_if.aw_channel.set_pause_generator(generator())
                ram.write_if.w_channel.set_pause_generator(generator())
                ram.read_if.ar_channel.set_pause_generator(generator())

    async def cycle_reset(self):
<<<<<<< HEAD
        # Asynchronously apply a reset cycle to the DUT
        # This simulates a reset condition to initialize the DUT
        self.dut.rst.setimmediatevalue(0)  # Initially set reset to low
        await RisingEdge(self.dut.clk)     # Wait for a clock edge
        await RisingEdge(self.dut.clk)     # Wait for another clock edge
        self.dut.rst.value = 1             # Set reset high to reset the DUT
        await RisingEdge(self.dut.clk)     # Wait for a clock edge
        await RisingEdge(self.dut.clk)     # Wait for another clock edge
        self.dut.rst.value = 0             # Set reset low to resume normal operation
        await RisingEdge(self.dut.clk)     # Wait for a clock edge
        await RisingEdge(self.dut.clk)     # Wait for another clock edge


async def run_test_read(dut, data_in=None, idle_inserter=None, backpressure_inserter=None, size=None, s=0, m=0):
    # Function to test the read functionality of the DUT

    tb = TB(dut)  # Create an instance of the testbench

    # Determine the byte lanes and max burst size based on the AXI master's write interface
=======
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

>>>>>>> refs/remotes/origin/main
    byte_lanes = tb.axi_master[s].write_if.byte_lanes
    max_burst_size = tb.axi_master[s].write_if.max_burst_size

    if size is None:
<<<<<<< HEAD
        size = max_burst_size  # Use the maximum burst size if no size is specified

    await tb.cycle_reset()  # Perform a reset cycle on the DUT

    # Set idle and backpressure generators if provided
    tb.set_idle_generator(idle_inserter)
    tb.set_backpressure_generator(backpressure_inserter)

    # Test different lengths and offsets for reading data from RAM via AXI
    for length in list(range(1, byte_lanes*2))+[1024]:
        for offset in list(range(byte_lanes, byte_lanes*2))+list(range(4096-byte_lanes, 4096)):
            tb.log.info("length %d, offset %d, size %d", length, offset, size)
            ram_addr = offset + 0x1000  # Calculate RAM address based on offset
            addr = ram_addr + m * 0x1000000  # Calculate AXI address for the master interface
            test_data = bytearray([x % 256 for x in range(length)])  # Generate test data

            tb.axi_ram[m].write(ram_addr, test_data)  # Write test data to RAM

            data = await tb.axi_master[s].read(addr, length, size=size)  # Read data from RAM via AXI

            assert data.data == test_data  # Verify that the read data matches the written data

    await RisingEdge(dut.clk)  # Wait for a clock edge
    await RisingEdge(dut.clk)  # Wait for another clock edge


def cycle_pause():
    # Helper function to create a cycle pause generator
    # This generator produces a pause pattern to simulate idle cycles in the AXI channels
=======
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
>>>>>>> refs/remotes/origin/main
    return itertools.cycle([1, 1, 1, 0])


if cocotb.SIM_NAME:
<<<<<<< HEAD
    # Check if the script is running within a simulation environment
    # If so, set up the test factory and generate test cases

    s_count = len(cocotb.top.s_axi_arvalid)  # Get the number of slave interfaces
    m_count = len(cocotb.top.m_axi_arvalid)  # Get the number of master interfaces

    # Determine data width based on the size of the s_axi_rdata signal
    data_width = len(cocotb.top.s_axi_rdata)
    byte_lanes = data_width // 8  # Calculate the number of byte lanes
    max_burst_size = (byte_lanes - 1).bit_length()  # Calculate the maximum burst size

    # Create a test factory for running read tests
    factory = TestFactory(run_test_read)
    factory.add_option("idle_inserter", [None, cycle_pause])  # Add idle cycle options
    factory.add_option("backpressure_inserter", [None, cycle_pause])  # Add backpressure options
    factory.add_option("s", range(min(s_count, 2)))  # Test up to two slave interfaces
    factory.add_option("m", range(min(m_count, 2)))  # Test up to two master interfaces
    factory.generate_tests()  # Generate the test cases


# cocotb-test integration

# Determine the directory paths for the tests and RTL files
=======
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

>>>>>>> refs/remotes/origin/main
tests_dir = os.path.abspath(os.path.dirname(__file__))
rtl_dir = os.path.abspath(os.path.join(tests_dir, '..', '..', 'responses'))

@pytest.mark.parametrize("data_width", [8, 16, 32])
@pytest.mark.parametrize("m_count", [1, 4])
@pytest.mark.parametrize("s_count", [1, 4])
def test_axi_crossbar_rd(request, s_count, m_count, data_width):
<<<<<<< HEAD
    # Pytest function for integrating cocotb tests with pytest
    dut = "axi_crossbar_rd"  # Specify the top-level module (DUT) to be tested
    module = os.path.splitext(os.path.basename(__file__))[0]  # Get the Python module name
    toplevel = dut  # Use axi_crossbar_rd as the top-level module

    # List of Verilog source files required for the simulation
    verilog_sources = [
        os.path.join(rtl_dir, f"{dut}.v"),  # Include the axi_crossbar_rd.v file
        os.path.join(rtl_dir, "axi_crossbar_addr.v"),  # Include the axi_crossbar_addr.v file
        os.path.join(rtl_dir, "axi_register_rd.v"),  # Include the axi_register_rd.v file
        os.path.join(rtl_dir, "arbiter.v"),  # Include the arbiter.v file
        os.path.join(rtl_dir, "priority_encoder.v"),  # Include the priority_encoder.v file
    ]

    # Define the parameters for the simulation
    parameters = {
        'S_COUNT': s_count,
        'M_COUNT': m_count,
        'DATA_WIDTH': data_width,
        'ADDR_WIDTH': 32,
        'STRB_WIDTH': data_width // 8,
        'S_ID_WIDTH': 8,
        'M_ID_WIDTH': 8 + (s_count-1).bit_length(),
        'ARUSER_ENABLE': 0,  # ARUSER parameters required by the module
        'ARUSER_WIDTH': 1,   # Set correct ARUSER parameters
        'RUSER_ENABLE': 0,   # RUSER parameters required by the module
        'RUSER_WIDTH': 1,    # Set correct RUSER parameters
        'M_REGIONS': 1,
    }

    # Convert parameters to environment variables
    extra_env = {f'PARAM_{k}': str(v) for k, v in parameters.items()}

    # Define the build directory for simulation artifacts
    sim_build = os.path.join(tests_dir, "sim_build",
                             request.node.name.replace('[', '-').replace(']', ''))

    # Run the simulation using cocotb_test.simulator
    cocotb_test.simulator.run(
        python_search=[tests_dir],  # Search path for Python modules
        verilog_sources=verilog_sources,  # List of Verilog source files
        toplevel=toplevel,  # Specify the top-level Verilog module
        module=module,  # Specify the Python module containing the test
        parameters=parameters,  # Pass parameters to the simulation
        sim_build=sim_build,  # Specify the build directory
        extra_env=extra_env,  # Pass environment variables
=======
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
>>>>>>> refs/remotes/origin/main
    )
