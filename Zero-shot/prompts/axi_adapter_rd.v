// Create a Verilog module named axi_adapter_rd.

// The module should serve as an AXI width adapter for read transactions with parametrizable data and address interface widths.
// It must support INCR burst types and narrow bursts. This module is essential for designing an efficient
// and flexible data transfer system within an AXI-based design.

// Handles different data bus widths between the slave and master interfaces
// can split or merge read transactions based on the width difference
// EXPAND Parameter: Determines whether the master bus is wider (EXPAND = 1) or narrower (EXPAND = 0) than the slave bus

// The module uses a state machine with states STATE_IDLE, STATE_DATA, STATE_DATA_READ, and STATE_DATA_SPLIT to manage read transactions
// The module compromises of internal paramters, state registers, data registers, and control signals
// IDLE State: Waits for a new read burst. When a valid read address is received (s_axi_arvalid), it captures the address and burst parameters and transitions to the appropriate state based on the bus widths and conversion parameters.
// DATA State: Transfers read data directly if the master bus width is the same as the slave bus width. If the master bus is wider, it splits the read data. If the master bus is narrower, it merges read data from multiple transactions.
// DATA_READ State: Handles splitting of reads for wider master bus widths. It calculates the correct segment of data to transfer based on the address and burst parameters.
// DATA_SPLIT State: Manages the transfer of split data segments back to the slave interface.

// CONVERT_BURST and CONVERT_NARROW_BURST control how bursts are handled when adapting between different bus widths
// Allows repacking of bursts to optimize data transfer, either by splitting larger bursts into smaller ones or merging smaller bursts into larger ones

// Develop a Verilog module that includes the following parameters and ports:

module axi_adapter_rd #
(
    // Parameters
    parameter ADDR_WIDTH = 32,       // Width of address bus in bits
    parameter S_DATA_WIDTH = 32,     // Width of input (slave) interface data bus in bits
    parameter S_STRB_WIDTH = (S_DATA_WIDTH/8),  // Width of input (slave) interface wstrb
    parameter M_DATA_WIDTH = 32,     // Width of output (master) interface data bus in bits
    parameter M_STRB_WIDTH = (M_DATA_WIDTH/8),  // Width of output (master) interface wstrb
    parameter ID_WIDTH = 8,          // Width of ID signal
    parameter ARUSER_ENABLE = 0,     // Propagate aruser signal
    parameter ARUSER_WIDTH = 1,      // Width of aruser signal
    parameter RUSER_ENABLE = 0,      // Propagate ruser signal
    parameter RUSER_WIDTH = 1,       // Width of ruser signal
    parameter CONVERT_BURST = 1,     // Re-pack full-width burst when adapting to a wider bus
    parameter CONVERT_NARROW_BURST = 0,  // Re-pack all bursts when adapting to a wider bus
    parameter FORWARD_ID = 0         // Forward ID through adapter
)
(
    // Ports
    input  wire                     clk,     // Clock signal
    input  wire                     rst,     // Reset signal

    // AXI Slave Interface
    input  wire [ID_WIDTH-1:0]      s_axi_arid,
    input  wire [ADDR_WIDTH-1:0]    s_axi_araddr,
    input  wire [7:0]               s_axi_arlen,
    input  wire [2:0]               s_axi_arsize,
    input  wire [1:0]               s_axi_arburst,
    input  wire                     s_axi_arlock,
    input  wire [3:0]               s_axi_arcache,
    input  wire [2:0]               s_axi_arprot,
    input  wire [3:0]               s_axi_arqos,
    input  wire [3:0]               s_axi_arregion,
    input  wire [ARUSER_WIDTH-1:0]  s_axi_aruser,
    input  wire                     s_axi_arvalid,
    output wire                     s_axi_arready,
    output wire [ID_WIDTH-1:0]      s_axi_rid,
    output wire [S_DATA_WIDTH-1:0]  s_axi_rdata,
    output wire [1:0]               s_axi_rresp,
    output wire                     s_axi_rlast,
    output wire [RUSER_WIDTH-1:0]   s_axi_ruser,
    output wire                     s_axi_rvalid,
    input  wire                     s_axi_rready,

    // AXI Master Interface
    output wire [ID_WIDTH-1:0]      m_axi_arid,
    output wire [ADDR_WIDTH-1:0]    m_axi_araddr,
    output wire [7:0]               m_axi_arlen,
    output wire [2:0]               m_axi_arsize,
    output wire [1:0]               m_axi_arburst,
    output wire                     m_axi_arlock,
    output wire [3:0]               m_axi_arcache,
    output wire [2:0]               m_axi_arprot,
    output wire [3:0]               m_axi_arqos,
    output wire [3:0]               m_axi_arregion,
    output wire [ARUSER_WIDTH-1:0]  m_axi_aruser,
    output wire                     m_axi_arvalid,
    input  wire                     m_axi_arready,
    input  wire [ID_WIDTH-1:0]      m_axi_rid,
    input  wire [M_DATA_WIDTH-1:0]  m_axi_rdata,
    input  wire [1:0]               m_axi_rresp,
    input  wire                     m_axi_rlast,
    input  wire [RUSER_WIDTH-1:0]   m_axi_ruser,
    input  wire                     m_axi_rvalid,
    output wire                     m_axi_rready
);

endmodule
