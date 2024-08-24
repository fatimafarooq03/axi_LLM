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
<<<<<<< HEAD
# These streams are used to define custom AXI stream interfaces for descriptors and their status.
=======
>>>>>>> refs/remotes/origin/main
DescBus, DescTransaction, DescSource, DescSink, DescMonitor = define_stream("Desc",
    signals=["addr", "len", "tag", "id", "dest", "user", "valid", "ready"]
)

DescStatusBus, DescStatusTransaction, DescStatusSource, DescStatusSink, DescStatusMonitor = define_stream("DescStatus",
    signals=["len", "tag", "id", "dest", "user", "error", "valid"]
)

class TB(object):
    def __init__(self, dut):
<<<<<<< HEAD
        # Initialize the testbench with the device under test (DUT)
=======
>>>>>>> refs/remotes/origin/main
        self.dut = dut

        # Set up logging for debug information
        self.log = logging.getLogger("cocotb.tb")
        self.log.setLevel(logging.DEBUG)

<<<<<<< HEAD
        # Start a clock for the DUT with a period of 10ns
        cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())

        # Create descriptor sources for each port
        # This creates a descriptor source for each port on the DUT, allowing the testbench to send descriptor transactions.
        self.desc_sources = [DescSource(DescBus.from_prefix(dut, f"s_axis_desc_{i}"), dut.clk, dut.rst) for i in range(dut.PORTS)]
        
        # Create a descriptor status sink
        # This sink receives the status of processed descriptors.
        self.desc_status_sink = DescStatusSink(DescStatusBus.from_prefix(dut, "s_axis_desc_status"), dut.clk, dut.rst)

        # Create an AXI RAM model
        # This models the RAM that the DUT will interface with over AXI.
        self.axi_ram = AxiRam(AxiBus.from_prefix(dut, "m_axi"), dut.clk, dut.rst, size=2**16)

        # Set the initial value for the enable signal to 0 (disabled)
=======
        # Start a clock for the DUT
        cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())

        # Create descriptor sources for each port
        self.desc_sources = [DescSource(DescBus.from_prefix(dut, f"s_axis_desc_{i}"), dut.clk, dut.rst) for i in range(dut.PORTS)]
        # Create a descriptor status sink
        self.desc_status_sink = DescStatusSink(DescStatusBus.from_prefix(dut, "s_axis_desc_status"), dut.clk, dut.rst)

        # Create an AXI RAM model
        self.axi_ram = AxiRam(AxiBus.from_prefix(dut, "m_axi"), dut.clk, dut.rst, size=2**16)

        # Set initial value for enable signal
>>>>>>> refs/remotes/origin/main
        dut.enable.setimmediatevalue(0)

    def set_idle_generator(self, generator=None):
        """Set a generator to pause the AXI transactions for idle periods."""
        if generator:
<<<<<<< HEAD
            # Pause transactions on descriptor sources and AXI RAM channels
=======
>>>>>>> refs/remotes/origin/main
            for desc_source in self.desc_sources:
                desc_source.set_pause_generator(generator())
            self.axi_ram.write_if.b_channel.set_pause_generator(generator())
            self.axi_ram.read_if.r_channel.set_pause_generator(generator())

    def set_backpressure_generator(self, generator=None):
        """Set a generator to create backpressure on the AXI bus."""
        if generator:
<<<<<<< HEAD
            # Apply backpressure on the AXI write and read channels
=======
>>>>>>> refs/remotes/origin/main
            self.axi_ram.write_if.aw_channel.set_pause_generator(generator())
            self.axi_ram.write_if.w_channel.set_pause_generator(generator())
            self.axi_ram.read_if.ar_channel.set_pause_generator(generator())

    async def cycle_reset(self):
        """Reset the DUT."""
<<<<<<< HEAD
        # Apply a reset sequence to the DUT
=======
>>>>>>> refs/remotes/origin/main
        self.dut.rst.setimmediatevalue(0)
        await RisingEdge(self.dut.clk)
        await RisingEdge(self.dut.clk)
        self.dut.rst.value = 1
        await RisingEdge(self.dut.clk)
        await RisingEdge(self.dut.clk)
        self.dut.rst.value = 0
        await RisingEdge(self.dut.clk)
        await RisingEdge(self.dut.clk)

    async def send_descriptor_from_port(self, port, addr, length, tag, axi_id, dest, user):
        """Send a descriptor from the specified port."""
<<<<<<< HEAD
        # Create test data for the transaction
        test_data = bytearray([x % 256 for x in range(length)])
        
        # Write test data to AXI RAM at the specified address
        self.axi_ram.write(addr, test_data)
        
        # Write padding data around the test data to verify boundary conditions
        self.axi_ram.write((addr & 0xffff80), b'\xaa'*(len(test_data)+256))

        # Create a descriptor transaction with the specified parameters
        desc = DescTransaction(addr=addr, len=length, tag=tag, id=axi_id, dest=dest, user=user)
        
        # Send the descriptor to the DUT through the specified port
=======
        # Create test data
        test_data = bytearray([x % 256 for x in range(length)])
        # Write test data to AXI RAM
        self.axi_ram.write(addr, test_data)
        self.axi_ram.write((addr & 0xffff80), b'\xaa'*(len(test_data)+256))

        # Create a descriptor transaction
        desc = DescTransaction(addr=addr, len=length, tag=tag, id=axi_id, dest=dest, user=user)
        # Send the descriptor
>>>>>>> refs/remotes/origin/main
        await self.desc_sources[port].send(desc)

    async def run_test(self, data_in=None, idle_inserter=None, backpressure_inserter=None):
        """Main test routine to run the descriptor mux test."""
<<<<<<< HEAD
        # Reset the DUT before starting the test
        await self.cycle_reset()

        # Set idle and backpressure generators for the AXI transactions
=======
        # Reset the DUT
        await self.cycle_reset()

        # Set idle and backpressure generators
>>>>>>> refs/remotes/origin/main
        self.set_idle_generator(idle_inserter)
        self.set_backpressure_generator(backpressure_inserter)

        # Enable the DUT
        self.dut.enable.value = 1

<<<<<<< HEAD
        # Create a list to hold all concurrent tasks (one for each descriptor sent)
        tasks = []
        cur_tag = 1  # Initialize the tag counter
        byte_lanes = self.axi_ram.write_if.byte_lanes  # Determine the number of byte lanes in the AXI interface
        step_size = 1 if int(os.getenv("PARAM_ENABLE_UNALIGNED")) else byte_lanes  # Step size depends on alignment

        # Generate and send descriptors from all ports concurrently
        for port in range(len(self.desc_sources)):
            # Iterate over a variety of lengths and addresses
            for length in list(range(1, byte_lanes*4+1))+[128]:
                for addr_offset in list(range(8, 8+byte_lanes*2, step_size))+list(range(4096-byte_lanes*2, 4096, step_size)):
                    addr = addr_offset + 0x1000  # Calculate the address
                    axi_id = port  # AXI ID corresponds to the port number
                    dest = 0  # Destination is set to 0 (could be used for routing)
                    user = 0  # User signal is set to 0 (can carry additional info)
                    
                    # Start a task to send the descriptor and add it to the task list
                    task = cocotb.start_soon(self.send_descriptor_from_port(port, addr, length, cur_tag, axi_id, dest, user))
                    tasks.append(task)
                    cur_tag += 1  # Increment the tag for the next descriptor

        # Wait for all descriptor send tasks to complete
=======
        # Create a list to hold all concurrent tasks
        tasks = []
        cur_tag = 1
        byte_lanes = self.axi_ram.write_if.byte_lanes
        step_size = 1 if int(os.getenv("PARAM_ENABLE_UNALIGNED")) else byte_lanes

        # Generate and send descriptors from all ports concurrently
        for port in range(len(self.desc_sources)):
            for length in list(range(1, byte_lanes*4+1))+[128]:
                for addr_offset in list(range(8, 8+byte_lanes*2, step_size))+list(range(4096-byte_lanes*2, 4096, step_size)):
                    addr = addr_offset + 0x1000
                    axi_id = port
                    dest = 0
                    user = 0
                    # Start a task to send a descriptor from the specified port
                    task = cocotb.start_soon(self.send_descriptor_from_port(port, addr, length, cur_tag, axi_id, dest, user))
                    tasks.append(task)
                    cur_tag += 1

        # Wait for all tasks to complete
>>>>>>> refs/remotes/origin/main
        for task in tasks:
            await task

        # Receive and check the status of each descriptor
        for _ in range(len(tasks)):
<<<<<<< HEAD
            status = await self.desc_status_sink.recv()  # Receive status from the DUT
            self.log.info("status: %s", status)  # Log the received status
            assert int(status.tag) < cur_tag  # Ensure the tag is within expected range
            assert int(status.error) == 0  # Ensure no error occurred during the transaction

        # Wait for a few clock cycles before completing the test
=======
            status = await self.desc_status_sink.recv()
            self.log.info("status: %s", status)
            assert int(status.tag) < cur_tag
            assert int(status.error) == 0

>>>>>>> refs/remotes/origin/main
        await RisingEdge(self.dut.clk)
        await RisingEdge(self.dut.clk)

def cycle_pause():
    """Generator for creating idle periods."""
<<<<<<< HEAD
    return itertools.cycle([1, 1, 1, 0])  # Cycle to introduce pauses in the transaction flow
=======
    return itertools.cycle([1, 1, 1, 0])
>>>>>>> refs/remotes/origin/main

if cocotb.SIM_NAME:
    # Register the test with cocotb
    for test in [TB.run_test]:
        factory = TestFactory(test)
<<<<<<< HEAD
        factory.add_option("idle_inserter", [None, cycle_pause])  # Add options for idle cycles
        factory.add_option("backpressure_inserter", [None, cycle_pause])  # Add options for backpressure
        factory.generate_tests()  # Generate the test cases

# cocotb-test configuration

tests_dir = os.path.abspath(os.path.dirname(__file__))  # Get the directory of the test
responses_dir = os.path.abspath(os.path.join(tests_dir, '..', '..', 'responses'))  # Path to the directory containing the RTL code

@pytest.mark.parametrize("unaligned", [0, 1])  # Parametrize the test for aligned and unaligned transactions
@pytest.mark.parametrize("axi_data_width", [8, 16, 32])  # Test with different AXI data widths
def test_axi_dma_desc_mux(request, axi_data_width, unaligned):
    """Pytest configuration for the testbench."""
    dut = "axi_dma_desc_mux"  # Name of the DUT
    module = os.path.splitext(os.path.basename(__file__))[0]  # The Python module name (this file)
    toplevel = dut  # Top-level module in the simulation

    # Specify the Verilog sources
    verilog_sources = [
        os.path.join(responses_dir, f"{dut}.v"),  # DUT Verilog source
        os.path.join(responses_dir, "arbiter.v"),  # Include arbiter module
        os.path.join(responses_dir, "priority_encoder.v"),  # Include priority encoder module
=======
        factory.add_option("idle_inserter", [None, cycle_pause])
        factory.add_option("backpressure_inserter", [None, cycle_pause])
        factory.generate_tests()

# cocotb-test configuration
tests_dir = os.path.abspath(os.path.dirname(__file__))
responses_dir = os.path.abspath(os.path.join(tests_dir, '..', '..', 'responses'))

@pytest.mark.parametrize("unaligned", [0, 1])
@pytest.mark.parametrize("axi_data_width", [8, 16, 32])
def test_axi_dma_desc_mux(request, axi_data_width, unaligned):
    """Pytest configuration for the testbench."""
    dut = "axi_dma_desc_mux"
    module = os.path.splitext(os.path.basename(__file__))[0]
    toplevel = dut

    # Specify the Verilog sources
    verilog_sources = [
        os.path.join(responses_dir, f"{dut}.v"),
>>>>>>> refs/remotes/origin/main
    ]

    # Define parameters for the DUT
    parameters = {}
<<<<<<< HEAD
    parameters['AXI_ADDR_WIDTH'] = 16  # AXI address width
    parameters['LEN_WIDTH'] = 20  # Width of the length field
    parameters['S_TAG_WIDTH'] = 8  # Source tag width
    parameters['M_TAG_WIDTH'] = parameters['S_TAG_WIDTH'] + 1  # Master tag width, assuming PORTS=2
    parameters['AXIS_ID_ENABLE'] = 1  # Enable ID field in AXI stream
    parameters['AXIS_ID_WIDTH'] = 8  # Width of the ID field
    parameters['AXIS_DEST_ENABLE'] = 1  # Enable destination field in AXI stream
    parameters['AXIS_DEST_WIDTH'] = 8  # Width of the destination field
    parameters['AXIS_USER_ENABLE'] = 1  # Enable user field in AXI stream
    parameters['AXIS_USER_WIDTH'] = 1  # Width of the user field
    parameters['ARB_TYPE_ROUND_ROBIN'] = 1  # Use round-robin arbitration
    parameters['ARB_LSB_HIGH_PRIORITY'] = 1  # LSB has high priority in arbitration

    # Extra environment variables for simulation
    extra_env = {f'PARAM_{k}': str(v) for k, v in parameters.items()}  # Convert parameters to environment variables

    # Build the simulation
    sim_build = os.path.join(tests_dir, "sim_build",
        request.node.name.replace('[', '-').replace(']', ''))  # Path to store the simulation build
=======
    parameters['AXI_DATA_WIDTH'] = axi_data_width
    parameters['AXI_ADDR_WIDTH'] = 16
    parameters['AXI_STRB_WIDTH'] = parameters['AXI_DATA_WIDTH'] // 8
    parameters['LEN_WIDTH'] = 20
    parameters['S_TAG_WIDTH'] = 8
    parameters['M_TAG_WIDTH'] = parameters['S_TAG_WIDTH'] + 1  # Assuming PORTS=2 for this example
    parameters['AXIS_ID_ENABLE'] = 1
    parameters['AXIS_ID_WIDTH'] = 8
    parameters['AXIS_DEST_ENABLE'] = 1
    parameters['AXIS_DEST_WIDTH'] = 8
    parameters['AXIS_USER_ENABLE'] = 1
    parameters['AXIS_USER_WIDTH'] = 1
    parameters['ARB_TYPE_ROUND_ROBIN'] = 1
    parameters['ARB_LSB_HIGH_PRIORITY'] = 1
    parameters['ENABLE_UNALIGNED'] = unaligned

    # Extra environment variables for simulation
    extra_env = {f'PARAM_{k}': str(v) for k, v in parameters.items()}

    # Build the simulation
    sim_build = os.path.join(tests_dir, "sim_build",
        request.node.name.replace('[', '-').replace(']', ''))
>>>>>>> refs/remotes/origin/main

    cocotb_test.simulator.run(
        python_search=[tests_dir],
        verilog_sources=verilog_sources,
<<<<<<< HEAD
        toplevel=toplevel,  # Specify the top-level module in the simulation
        module=module,  # Specify the Python module to run
        parameters=parameters,  # Pass parameters to the simulation
        sim_build=sim_build,  # Directory to store build artifacts
        extra_env=extra_env,  # Environment variables for parameters
=======
        toplevel=toplevel,
        module=module,
        parameters=parameters,
        sim_build=sim_build,
        extra_env=extra_env,
>>>>>>> refs/remotes/origin/main
    )
