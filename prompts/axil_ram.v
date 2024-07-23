// Create a Verilog module named axil_ram

// The module should serve as an AXI lite RAM with parametrizable data and address interface widths.
// Handles read and write operations to an internal memory array. It supports an optional pipeline register for read data to improve performance
// Only supports single, discrete read and write transactions

// comprises of internal memory array initialized to 0

// Check if both write address and write data are valid and there are no pending write responses.
// If true, acknowledge the address and data, and enable memory write
// Update memory array with new data using write strobe masking.

// Check if the read address is valid and there is no pending read data.
// If true, acknowledge the address and enable memory read (mem_rd_en).
// Retrieve data from memory array.
// If PIPELINE_OUTPUT is enabled, pipelines the read data

// Drives output signals based on the internal state

// Develop a Verilog module that includes the following parameters and ports:

module axil_ram #
(
    // Parameters
    parameter DATA_WIDTH = 32,  // Width of data bus in bits
    parameter ADDR_WIDTH = 16,  // Width of address bus in bits
    parameter STRB_WIDTH = (DATA_WIDTH/8),  // Width of wstrb (width of data bus in words)
    parameter PIPELINE_OUTPUT = 0  // Extra pipeline register on output
)
(
    // Ports
    input  wire                   clk,  // Clock signal
    input  wire                   rst,  // Reset signal

    input  wire [ADDR_WIDTH-1:0]  s_axil_awaddr,  // Write address
    input  wire [2:0]             s_axil_awprot,  // Write protection type
    input  wire                   s_axil_awvalid,  // Write address valid
    output wire                   s_axil_awready,  // Write address ready
    input  wire [DATA_WIDTH-1:0]  s_axil_wdata,  // Write data
    input  wire [STRB_WIDTH-1:0]  s_axil_wstrb,  // Write strobe
    input  wire                   s_axil_wvalid,  // Write data valid
    output wire                   s_axil_wready,  // Write data ready
    output wire [1:0]             s_axil_bresp,  // Write response
    output wire                   s_axil_bvalid,  // Write response valid
    input  wire                   s_axil_bready,  // Write response ready
    input  wire [ADDR_WIDTH-1:0]  s_axil_araddr,  // Read address
    input  wire [2:0]             s_axil_arprot,  // Read protection type
    input  wire                   s_axil_arvalid,  // Read address valid
    output wire                   s_axil_arready,  // Read address ready
    output wire [DATA_WIDTH-1:0]  s_axil_rdata,  // Read data
    output wire [1:0]             s_axil_rresp,  // Read response
    output wire                   s_axil_rvalid,  // Read response valid
    input  wire                   s_axil_rready  // Read response ready
);

endmodule