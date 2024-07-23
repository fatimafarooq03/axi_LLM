// Create a Verilog module named axi_adapter_wr.

// The module should serve as an AXI width adapter for write transactions with parametrizable data and address interface widths.
// It must support INCR burst types and narrow bursts. This module is essential for designing an efficient
// and flexible data transfer system within an AXI-based design.

// handles different data bus widths between the slave and master interfaces
// can merge or split write transactions based on the width difference
// EXPAND Parameter: Determines whether the master bus is wider (EXPAND = 1) or narrower (EXPAND = 0) than the slave bus

// The module uses a state machine with states STATE_IDLE, STATE_DATA, STATE_DATA_2, and STATE_RESP to manage write transactions
// The module compromises of internal paramters, state registers, data registers, and control signals
// IDLE State: Waits for a new write burst. When a valid write address is received (s_axi_awvalid), it captures the address and burst parameters and transitions to the appropriate state based on the bus widths and conversion parameters.
// DATA State: Transfers write data directly if the master bus width is the same as the slave bus width. If the master bus is wider, it merges the write data. If the master bus is narrower, it splits write data into multiple transactions.
// DATA_2 State: Handles additional data transfers required when the master bus is wider and multiple segments are needed for a single burst.
// RESP State: Transfers write response signals from the master to the slave interface, signaling the completion of the write transaction.

// CONVERT_BURST and CONVERT_NARROW_BURST control how bursts are handled when adapting between different bus widths
// Allows repacking of bursts to optimize data transfer, either by merging smaller bursts into larger ones or splitting larger bursts into smaller ones


// Develop a Verilog module that includes the following parameters and ports:

module axi_adapter_wr #
(
    // Parameters
    parameter ADDR_WIDTH = 32,       // Width of address bus in bits
    parameter S_DATA_WIDTH = 32,     // Width of input (slave) interface data bus in bits
    parameter S_STRB_WIDTH = (S_DATA_WIDTH/8),  // Width of input (slave) interface wstrb
    parameter M_DATA_WIDTH = 32,     // Width of output (master) interface data bus in bits
    parameter M_STRB_WIDTH = (M_DATA_WIDTH/8),  // Width of output (master) interface wstrb
    parameter ID_WIDTH = 8,          // Width of ID signal
    parameter AWUSER_ENABLE = 0,     // Propagate awuser signal
    parameter AWUSER_WIDTH = 1,      // Width of awuser signal
    parameter WUSER_ENABLE = 0,      // Propagate wuser signal
    parameter WUSER_WIDTH = 1,       // Width of wuser signal
    parameter BUSER_ENABLE = 0,      // Propagate buser signal
    parameter BUSER_WIDTH = 1,       // Width of buser signal
    parameter CONVERT_BURST = 1,     // Re-pack full-width burst when adapting to a wider bus
    parameter CONVERT_NARROW_BURST = 0,  // Re-pack all bursts when adapting to a wider bus
    parameter FORWARD_ID = 0         // Forward ID through adapter
)
(
    // Ports
    input  wire                     clk,     // Clock signal
    input  wire                     rst,     // Reset signal

    // AXI Slave Interface
    input  wire [ID_WIDTH-1:0]      s_axi_awid,
    input  wire [ADDR_WIDTH-1:0]    s_axi_awaddr,
    input  wire [7:0]               s_axi_awlen,
    input  wire [2:0]               s_axi_awsize,
    input  wire [1:0]               s_axi_awburst,
    input  wire                     s_axi_awlock,
    input  wire [3:0]               s_axi_awcache,
    input  wire [2:0]               s_axi_awprot,
    input  wire [3:0]               s_axi_awqos,
    input  wire [3:0]               s_axi_awregion,
    input  wire [AWUSER_WIDTH-1:0]  s_axi_awuser,
    input  wire                     s_axi_awvalid,
    output wire                     s_axi_awready,
    input  wire [S_DATA_WIDTH-1:0]  s_axi_wdata,
    input  wire [S_STRB_WIDTH-1:0]  s_axi_wstrb,
    input  wire                     s_axi_wlast,
    input  wire [WUSER_WIDTH-1:0]   s_axi_wuser,
    input  wire                     s_axi_wvalid,
    output wire                     s_axi_wready,
    output wire [ID_WIDTH-1:0]      s_axi_bid,
    output wire [1:0]               s_axi_bresp,
    output wire [BUSER_WIDTH-1:0]   s_axi_buser,
    output wire                     s_axi_bvalid,
    input  wire                     s_axi_bready,

    // AXI Master Interface
    output wire [ID_WIDTH-1:0]      m_axi_awid,
    output wire [ADDR_WIDTH-1:0]    m_axi_awaddr,
    output wire [7:0]               m_axi_awlen,
    output wire [2:0]               m_axi_awsize,
    output wire [1:0]               m_axi_awburst,
    output wire                     m_axi_awlock,
    output wire [3:0]               m_axi_awcache,
    output wire [2:0]               m_axi_awprot,
    output wire [3:0]               m_axi_awqos,
    output wire [3:0]               m_axi_awregion,
    output wire [AWUSER_WIDTH-1:0]  m_axi_awuser,
    output wire                     m_axi_awvalid,
    input  wire                     m_axi_awready,
    output wire [M_DATA_WIDTH-1:0]  m_axi_wdata,
    output wire [M_STRB_WIDTH-1:0]  m_axi_wstrb,
    output wire                     m_axi_wlast,
    output wire [WUSER_WIDTH-1:0]   m_axi_wuser,
    output wire                     m_axi_wvalid,
    input  wire                     m_axi_wready,
    input  wire [ID_WIDTH-1:0]      m_axi_bid,
    input  wire [1:0]               m_axi_bresp,
    input  wire [BUSER_WIDTH-1:0]   m_axi_buser,
    input  wire                     m_axi_bvalid,
    output wire                     m_axi_bready
);

endmodule
