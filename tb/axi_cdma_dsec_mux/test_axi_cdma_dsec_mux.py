'''
import itertools
import logging
import os

import cocotb_test.simulator
import pytest

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge
from cocotb.regression import TestFactory

from cocotbext.axi import AxiBus, AxiRam
from cocotbext.axi.stream import define_stream

# Define stream interfaces for descriptors
DescBus, DescTransaction, DescSource, DescSink, DescMonitor = define_stream("Desc",
    signals=["read_addr", "write_addr", "len", "tag", "valid", "ready"]
)

DescStatusBus, DescStatusTransaction, DescStatusSource, DescStatusSink, DescStatusMonitor = define_stream("DescStatus",
    signals=["tag", "error", "valid"]
)

class TB(object):
    def __init__(self, dut):
        self.dut = dut

        # Set up logging for debug information
        self.log = logging.getLogger("cocotb.tb")
        self.log.setLevel(logging.DEBUG)

        # Start a clock for the DUT
        cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())

        # Create descriptor sources for each port
        self.desc_sources = [DescSource(DescBus.from_prefix(dut, f"s_axis_desc_{i}"), dut.clk, dut.rst) for i in range(dut.PORTS)]
        # Create a descriptor status sink
        self.desc_status_sink = DescStatusSink(DescStatusBus.from_prefix(dut, "m_axis_desc_status"), dut.clk, dut.rst)

        # Create an AXI RAM model
        self.axi_ram = AxiRam(AxiBus.from_prefix(dut, "m_axi"), dut.clk, dut.rst, size=2**16)

        # Set initial value for enable signal
        dut.enable.setimmediatevalue(0)

    def set_idle_generator(self, generator=None):
        """Set a generator to pause the AXI transactions for idle periods."""
        if generator:
            for desc_source in self.desc_sources:
                desc_source.set_pause_generator(generator())
            self.axi_ram.write_if.b_channel.set_pause_generator(generator())
            self.axi_ram.read_if.r_channel.set_pause_generator(generator())

    def set_backpressure_generator(self, generator=None):
        """Set a generator to create backpressure on the AXI bus."""
        if generator:
            self.axi_ram.write_if.aw_channel.set_pause_generator(generator())
            self.axi_ram.write_if.w_channel.set_pause_generator(generator())
            self.axi_ram.read_if.ar_channel.set_pause_generator(generator())

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

    async def send_descriptor_from_port(self, port, read_addr, write_addr, length, tag):
        """Send a descriptor from the specified port."""
        # Create test data
        test_data = bytearray([x % 256 for x in range(length)])
        # Write test data to AXI RAM
        self.axi_ram.write(read_addr, test_data)
        self.axi_ram.write(write_addr & 0xffff80, b'\xaa'*(len(test_data)+256))

        # Create a descriptor transaction
        desc = DescTransaction(read_addr=read_addr, write_addr=write_addr, len=length, tag=tag)
        # Send the descriptor
        await self.desc_sources[port].send(desc)

    async def run_test(self, data_in=None, idle_inserter=None, backpressure_inserter=None):
        """Main test routine to run the descriptor mux test."""
        # Reset the DUT
        await self.cycle_reset()

        # Set idle and backpressure generators
        self.set_idle_generator(idle_inserter)
        self.set_backpressure_generator(backpressure_inserter)

        # Enable the DUT
        self.dut.enable.value = 1

        # Create a list to hold all concurrent tasks
        tasks = []
        cur_tag = 1
        byte_lanes = self.axi_ram.write_if.byte_lanes
        step_size = 1 if int(os.getenv("PARAM_ENABLE_UNALIGNED")) else byte_lanes

        # Generate and send descriptors from all ports concurrently
        for port in range(len(self.desc_sources)):
            for length in list(range(1, byte_lanes*4+1))+[128]:
                for read_offset in list(range(8, 8+byte_lanes*2, step_size))+list(range(4096-byte_lanes*2, 4096, step_size)):
                    for write_offset in list(range(8, 8+byte_lanes*2, step_size))+list(range(4096-byte_lanes*2, 4096, step_size)):
                        read_addr = read_offset+0x1000
                        write_addr = 0x00008000+write_offset+0x1000
                        # Start a task to send a descriptor from the specified port
                        task = cocotb.start_soon(self.send_descriptor_from_port(port, read_addr, write_addr, length, cur_tag))
                        tasks.append(task)
                        cur_tag += 1

        # Wait for all tasks to complete
        for task in tasks:
            await task

        # Receive and check the status of each descriptor
        for _ in range(len(tasks)):
            status = await self.desc_status_sink.recv()
            self.log.info("status: %s", status)
            assert int(status.tag) < cur_tag
            assert int(status.error) == 0

        await RisingEdge(self.dut.clk)
        await RisingEdge(self.dut.clk)

def cycle_pause():
    """Generator for creating idle periods."""
    return itertools.cycle([1, 1, 1, 0])

if cocotb.SIM_NAME:
    # Register the test with cocotb
    for test in [TB.run_test]:
        factory = TestFactory(test)
        factory.add_option("idle_inserter", [None, cycle_pause])
        factory.add_option("backpressure_inserter", [None, cycle_pause])
        factory.generate_tests()

# cocotb-test configuration
tests_dir = os.path.abspath(os.path.dirname(__file__))
responses_dir = os.path.abspath(os.path.join(tests_dir, '..', '..', 'responses'))

@pytest.mark.parametrize("unaligned", [0, 1])
@pytest.mark.parametrize("axi_data_width", [8, 16, 32])
def test_axi_cdma_desc_mux(request, axi_data_width, unaligned):
    """Pytest configuration for the testbench."""
    dut = "axi_cdma_desc_mux"
    module = os.path.splitext(os.path.basename(__file__))[0]
    toplevel = dut

    # Specify the Verilog sources
    verilog_sources = [
        os.path.join(responses_dir, f"{dut}.v"),
    ]

    # Define parameters for the DUT
    parameters = {}
    parameters['AXI_DATA_WIDTH'] = axi_data_width
    parameters['AXI_ADDR_WIDTH'] = 16
    parameters['AXI_STRB_WIDTH'] = parameters['AXI_DATA_WIDTH'] // 8
    parameters['LEN_WIDTH'] = 20
    parameters['TAG_WIDTH'] = 8
    parameters['ENABLE_UNALIGNED'] = unaligned

    # Extra environment variables for simulation
    extra_env = {f'PARAM_{k}': str(v) for k, v in parameters.items()}

    # Build the simulation
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
'''
import itertools
import logging
import os

import cocotb_test.simulator  # Used to run cocotb tests with various simulators
import pytest  # Pytest for running parameterized tests

import cocotb  # Main cocotb library for testbench creation
from cocotb.clock import Clock  # Provides clock generation capabilities
from cocotb.triggers import RisingEdge  # Trigger that waits for a rising edge of a signal
from cocotb.regression import TestFactory  # Automates test generation based on parameters

from cocotbext.axi import AxiBus, AxiRam  # Extensions for AXI protocol handling
from cocotbext.axi.stream import define_stream  # Helper to define AXI Stream interfaces

# Define stream interfaces for descriptors
DescBus, DescTransaction, DescSource, DescSink, DescMonitor = define_stream("Desc",
    signals=["read_addr", "write_addr", "len", "tag", "valid", "ready"]
)

# Define stream interfaces for descriptor status
DescStatusBus, DescStatusTransaction, DescStatusSource, DescStatusSink, DescStatusMonitor = define_stream("DescStatus",
    signals=["tag", "error", "valid"]
)

class TB(object):
    def __init__(self, dut):
        """Testbench initialization."""
        self.dut = dut  # Reference to the DUT (Design Under Test)

        # Set up logging for debug information
        self.log = logging.getLogger("cocotb.tb")
        self.log.setLevel(logging.DEBUG)

        # Start a clock for the DUT (10 ns period)
        cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())

        # Initialize reset signal to 0
        dut.rst.setimmediatevalue(0)

        # Create descriptor sources for each port
        # Using int() to convert dut.PORTS to a usable integer value
        self.desc_sources = [DescSource(DescBus.from_prefix(dut, f"s_axis_desc_{i}"), dut.clk, dut.rst) for i in range(int(dut.PORTS))]

        # Create a descriptor status sink to receive status updates
        self.desc_status_sink = DescStatusSink(DescStatusBus.from_prefix(dut, "m_axis_desc_status"), dut.clk, dut.rst)

        # Create an AXI RAM model with a size of 2^16 bytes
        self.axi_ram = AxiRam(AxiBus.from_prefix(dut, "m_axi"), dut.clk, dut.rst, size=2**16)

        # Set initial value for enable signal to 0
        dut.enable.setimmediatevalue(0)

    async def cycle_reset(self):
        """Reset the DUT by toggling the reset signal."""
        # Set reset low initially
        self.dut.rst.setimmediatevalue(0)
        # Wait for two clock cycles
        await RisingEdge(self.dut.clk)
        await RisingEdge(self.dut.clk)
        # Set reset high for two clock cycles
        self.dut.rst.value = 1
        await RisingEdge(self.dut.clk)
        await RisingEdge(self.dut.clk)
        # Set reset low again
        self.dut.rst.value = 0
        # Wait for two clock cycles
        await RisingEdge(self.dut.clk)
        await RisingEdge(self.dut.clk)

    def set_idle_generator(self, generator=None):
        """Set a generator to pause the AXI transactions for idle periods."""
        if generator:
            # Apply the generator to each descriptor source
            for desc_source in self.desc_sources:
                desc_source.set_pause_generator(generator())
            # Apply the generator to the AXI RAM's write and read channels
            self.axi_ram.write_if.b_channel.set_pause_generator(generator())
            self.axi_ram.read_if.r_channel.set_pause_generator(generator())

    def set_backpressure_generator(self, generator=None):
        """Set a generator to create backpressure on the AXI bus."""
        if generator:
            # Apply the generator to various AXI channels to simulate backpressure
            self.axi_ram.write_if.aw_channel.set_pause_generator(generator())
            self.axi_ram.write_if.w_channel.set_pause_generator(generator())
            self.axi_ram.read_if.ar_channel.set_pause_generator(generator())

    async def send_descriptor_from_port(self, port, read_addr, write_addr, length, tag):
        """Send a descriptor from the specified port."""
        # Create test data to write to memory
        test_data = bytearray([x % 256 for x in range(length)])
        # Write the test data to the AXI RAM at the read address
        self.axi_ram.write(read_addr, test_data)
        # Write additional data to the AXI RAM at the write address
        self.axi_ram.write(write_addr & 0xffff80, b'\xaa'*(len(test_data)+256))

        # Create a descriptor transaction
        desc = DescTransaction(read_addr=read_addr, write_addr=write_addr, len=length, tag=tag)
        # Send the descriptor through the appropriate port
        await self.desc_sources[port].send(desc)

    async def run_test(self, data_in=None, idle_inserter=None, backpressure_inserter=None):
        """Main test routine to run the descriptor mux test."""
        # Reset the DUT
        await self.cycle_reset()

        # Set idle and backpressure generators if provided
        self.set_idle_generator(idle_inserter)
        self.set_backpressure_generator(backpressure_inserter)

        # Enable the DUT
        self.dut.enable.value = 1

        # Create a list to hold all concurrent tasks
        tasks = []
        cur_tag = 1  # Start tag for tracking transactions
        byte_lanes = int(self.axi_ram.write_if.byte_lanes)  # Number of byte lanes in AXI RAM
        step_size = byte_lanes  # Step size for address generation

        # Generate and send descriptors from all ports concurrently
        for port in range(len(self.desc_sources)):
            for length in list(range(1, byte_lanes*4+1))+[128]:
                for read_offset in list(range(8, 8+byte_lanes*2, step_size))+list(range(4096-byte_lanes*2, 4096, step_size)):
                    for write_offset in list(range(8, 8+byte_lanes*2, step_size))+list(range(4096-byte_lanes*2, 4096, step_size)):
                        read_addr = read_offset+0x1000  # Adjust read address
                        write_addr = 0x00008000+write_offset+0x1000  # Adjust write address
                        # Start a task to send a descriptor from the specified port
                        task = cocotb.start_soon(self.send_descriptor_from_port(port, read_addr, write_addr, length, cur_tag))
                        tasks.append(task)  # Add task to the list
                        cur_tag += 1  # Increment tag for the next transaction

        # Wait for all tasks to complete
        for task in tasks:
            await task

        # Receive and check the status of each descriptor
        for _ in range(len(tasks)):
            status = await self.desc_status_sink.recv()  # Receive status
            self.log.info("status: %s", status)  # Log the status
            assert int(status.tag) < cur_tag  # Ensure the tag is within expected range
            assert int(status.error) == 0  # Ensure no errors occurred

        # Wait for a few more clock cycles before finishing
        await RisingEdge(self.dut.clk)
        await RisingEdge(self.dut.clk)

def cycle_pause():
    """Generator for creating idle periods."""
    return itertools.cycle([1, 1, 1, 0])  # Cycle through a pattern of idle and active cycles

if cocotb.SIM_NAME:
    # Define a function to run the testbench
    async def run_tb(dut, data_in=None, idle_inserter=None, backpressure_inserter=None):
        """Instantiate TB and run the test."""
        tb = TB(dut)  # Create an instance of the testbench class
        await tb.run_test(data_in, idle_inserter, backpressure_inserter)  # Run the test

    # Create a TestFactory to automatically generate tests
    factory = TestFactory(run_tb)
    factory.add_option("idle_inserter", [None, cycle_pause])
    factory.add_option("backpressure_inserter", [None, cycle_pause])
    factory.generate_tests()

# cocotb-test configuration
tests_dir = os.path.abspath(os.path.dirname(__file__))  # Get the directory of the current file
responses_dir = os.path.abspath(os.path.join(tests_dir, '..', '..', 'responses'))  # Path to response files

@pytest.mark.parametrize("axi_data_width", [8, 16, 32])
def test_axi_cdma_desc_mux(request, axi_data_width):
    """Pytest configuration for the testbench."""
    dut = "axi_cdma_desc_mux"  # Name of the DUT
    module = os.path.splitext(os.path.basename(__file__))[0]  # Get the module name from the file name
    toplevel = dut  # Specify the top-level module for simulation

    # Specify the Verilog sources
    verilog_sources = [
        os.path.join(responses_dir, f"{dut}.v"),  # DUT Verilog source
        os.path.join(responses_dir, "arbiter.v"),  # Include arbiter module
        os.path.join(responses_dir, "priority_encoder.v"),  # Include priority encoder module
    ]

    # Define parameters for the DUT
    parameters = {}
    parameters['AXI_ADDR_WIDTH'] = 16
    parameters['LEN_WIDTH'] = 20
    parameters['S_TAG_WIDTH'] = 8
    parameters['M_TAG_WIDTH'] = parameters['S_TAG_WIDTH'] + 1  # Example calculation
    parameters['PORTS'] = 2
    parameters['ARB_TYPE_ROUND_ROBIN'] = 1
    parameters['ARB_LSB_HIGH_PRIORITY'] = 1

    # Extra environment variables for simulation
    extra_env = {f'PARAM_{k}': str(v) for k, v in parameters.items()}

    # Build the simulation
    sim_build = os.path.join(tests_dir, "sim_build",
        request.node.name.replace('[', '-').replace(']', ''))

    # Run the cocotb test with the specified parameters
    cocotb_test.simulator.run(
        python_search=[tests_dir],  # Path to Python test files
        verilog_sources=verilog_sources,  # Verilog source files
        toplevel=toplevel,  # Top-level module for simulation
        module=module,  # Name of the Python test module
        parameters=parameters,  # DUT parameters
        sim_build=sim_build,  # Directory to build the simulation
        extra_env=extra_env,  # Additional environment variables
    )
