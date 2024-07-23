// Create a Verilog module named axi_ram.

// The module should serve as an AXI RAM with parametrizable data and address interface widths.
// It should support FIXED and INCR burst types as well as narrow bursts.
// Implements a RAM model with AXI slave interface, using state machines to handle read and write transactions

// Comprises of Internal Memory: 
// an internal memory array (mem) defined as a register array
// memory size is determined by the address width

// Comprises of Write State Machine: 
// WRITE_STATE_IDLE: Waits for a write address valid (s_axi_awvalid). Once valid, captures the address and prepares for data
// WRITE_STATE_BURST: Handles the burst write operations, writing data to memory as it is received. Manages the address increment and count decrement
// WRITE_STATE_RESP: Sends the write response once the burst is complete

// Comprises of Read State Machine:
// READ_STATE_IDLE: Waits for a read address valid (s_axi_arvalid). Once valid, captures the address and prepares for data
// READ_STATE_BURST: Handles the burst read operations, reading data from memory and sending it to the AXI master

// Comprises of optional pipeline registers for output data

// Develop a Verilog module that includes the following parameters and ports:

module axi_ram #
(
    // Parameters
    parameter DATA_WIDTH = 32,  // Width of data bus in bits
    parameter ADDR_WIDTH = 16,  // Width of address bus in bits
    parameter STRB_WIDTH = (DATA_WIDTH/8),  // Width of wstrb (width of data bus in words)
    parameter ID_WIDTH = 8,  // Width of ID signal
    parameter PIPELINE_OUTPUT = 0  // Extra pipeline register on output
)
(
    // Ports
    input  wire                   clk,  // Clock signal
    input  wire                   rst,  // Reset signal

    input  wire [ID_WIDTH-1:0]    s_axi_awid,
    input  wire [ADDR_WIDTH-1:0]  s_axi_awaddr,
    input  wire [7:0]             s_axi_awlen,
    input  wire [2:0]             s_axi_awsize,
    input  wire [1:0]             s_axi_awburst,
    input  wire                   s_axi_awlock,
    input  wire [3:0]             s_axi_awcache,
    input  wire [2:0]             s_axi_awprot,
    input  wire                   s_axi_awvalid,
    output wire                   s_axi_awready,
    input  wire [DATA_WIDTH-1:0]  s_axi_wdata,
    input  wire [STRB_WIDTH-1:0]  s_axi_wstrb,
    input  wire                   s_axi_wlast,
    input  wire                   s_axi_wvalid,
    output wire                   s_axi_wready,
    output wire [ID_WIDTH-1:0]    s_axi_bid,
    output wire [1:0]             s_axi_bresp,
    output wire                   s_axi_bvalid,
    input  wire                   s_axi_bready,
    input  wire [ID_WIDTH-1:0]    s_axi_arid,
    input  wire [ADDR_WIDTH-1:0]  s_axi_araddr,
    input  wire [7:0]             s_axi_arlen,
    input  wire [2:0]             s_axi_arsize,
    input  wire [1:0]             s_axi_arburst,
    input  wire                   s_axi_arlock,
    input  wire [3:0]             s_axi_arcache,
    input  wire [2:0]             s_axi_arprot,
    input  wire                   s_axi_arvalid,
    output wire                   s_axi_arready,
    output wire [ID_WIDTH-1:0]    s_axi_rid,
    output wire [DATA_WIDTH-1:0]  s_axi_rdata,
    output wire [1:0]             s_axi_rresp,
    output wire                   s_axi_rlast,
    output wire                   s_axi_rvalid,
    input  wire                   s_axi_rready
);

endmodule
