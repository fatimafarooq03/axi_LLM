// Prompt for axi_dma_rd Module

// Create a Verilog module named axi_dma_rd.

// The module should serve as an AXI to AXI stream DMA engine with parametrizable data and address interface widths.
// It should generate full-width INCR bursts only, with a parametrizable maximum burst length.
// The module must support unaligned transfers, which can be disabled via a parameter to save on resource consumption.
// read engine designed to manage read transactions from an AXI master interface and stream the data out through an AXI stream interface

// Defines various parameters for AXI data and address widths, stream data widths, descriptor lengths, tag widths, and optional features such as scatter/gather and unaligned transfers

// AXI read descriptors are provided via signals, which specify the address, length, tag, and user-specific information 
// Read descriptor status is sent out via signals, indicating the completion and any errors encountered

// Sets up AXI read address transactions by issuing AR (address read) commands using the signals
// Read data is received via signals, which include the data, response, and status information

// compises of AXI state machine 
// operates in states like AXI_STATE_IDLE and AXI_STATE_START
// Handles the flow of data from the AXI read interface to the AXI stream interface, including managing data shifts, cycle counts, and the transmission of signals

// Output FIFO: Used to buffer data between the AXI read data and the AXI stream output, ensuring that data is stored and forwarded correctly even if there is backpressure on the stream interface

// Data read from the AXI master is streamed out via the signals, which include data, keep, last, ID, destination, and user signals
// The module includes logic to detect and report errors

// Develop a Verilog module that includes the following parameters and ports:

module axi_dma_rd #
(
    // Parameters
    parameter AXI_DATA_WIDTH = 32,  // Width of AXI data bus in bits
    parameter AXI_ADDR_WIDTH = 16,  // Width of AXI address bus in bits
    parameter AXI_STRB_WIDTH = (AXI_DATA_WIDTH/8),  // Width of AXI wstrb (width of data bus in words)
    parameter AXI_ID_WIDTH = 8,  // Width of AXI ID signal
    parameter AXI_MAX_BURST_LEN = 16,  // Maximum AXI burst length to generate
    parameter AXIS_DATA_WIDTH = AXI_DATA_WIDTH,  // Width of AXI stream interfaces in bits
    parameter AXIS_KEEP_ENABLE = (AXIS_DATA_WIDTH>8),  // Use AXI stream tkeep signal
    parameter AXIS_KEEP_WIDTH = (AXIS_DATA_WIDTH/8),  // AXI stream tkeep signal width (words per cycle)
    parameter AXIS_LAST_ENABLE = 1,  // Use AXI stream tlast signal
    parameter AXIS_ID_ENABLE = 0,  // Propagate AXI stream tid signal
    parameter AXIS_ID_WIDTH = 8,  // AXI stream tid signal width
    parameter AXIS_DEST_ENABLE = 0,  // Propagate AXI stream tdest signal
    parameter AXIS_DEST_WIDTH = 8,  // AXI stream tdest signal width
    parameter AXIS_USER_ENABLE = 1,  // Propagate AXI stream tuser signal
    parameter AXIS_USER_WIDTH = 1,  // AXI stream tuser signal width
    parameter LEN_WIDTH = 20,  // Width of length field
    parameter TAG_WIDTH = 8,  // Width of tag field
    parameter ENABLE_SG = 0,  // Enable support for scatter/gather DMA (multiple descriptors per AXI stream frame)
    parameter ENABLE_UNALIGNED = 0  // Enable support for unaligned transfers
)
(
    // Ports
    input  wire                       clk,  // Clock signal
    input  wire                       rst,  // Reset signal

    // AXI read descriptor input
    input  wire [AXI_ADDR_WIDTH-1:0]  s_axis_read_desc_addr,
    input  wire [LEN_WIDTH-1:0]       s_axis_read_desc_len,
    input  wire [TAG_WIDTH-1:0]       s_axis_read_desc_tag,
    input  wire [AXIS_ID_WIDTH-1:0]   s_axis_read_desc_id,
    input  wire [AXIS_DEST_WIDTH-1:0] s_axis_read_desc_dest,
    input  wire [AXIS_USER_WIDTH-1:0] s_axis_read_desc_user,
    input  wire                       s_axis_read_desc_valid,
    output wire                       s_axis_read_desc_ready,

    // AXI read descriptor status output
    output wire [TAG_WIDTH-1:0]       m_axis_read_desc_status_tag,
    output wire [3:0]                 m_axis_read_desc_status_error,
    output wire                       m_axis_read_desc_status_valid,

    // AXI stream read data output
    output wire [AXIS_DATA_WIDTH-1:0] m_axis_read_data_tdata,
    output wire [AXIS_KEEP_WIDTH-1:0] m_axis_read_data_tkeep,
    output wire                       m_axis_read_data_tvalid,
    input  wire                       m_axis_read_data_tready,
    output wire                       m_axis_read_data_tlast,
    output wire [AXIS_ID_WIDTH-1:0]   m_axis_read_data_tid,
    output wire [AXIS_DEST_WIDTH-1:0] m_axis_read_data_tdest,
    output wire [AXIS_USER_WIDTH-1:0] m_axis_read_data_tuser,

    // AXI master interface
    output wire [AXI_ID_WIDTH-1:0]    m_axi_arid,
    output wire [AXI_ADDR_WIDTH-1:0]  m_axi_araddr,
    output wire [7:0]                 m_axi_arlen,
    output wire [2:0]                 m_axi_arsize,
    output wire [1:0]                 m_axi_arburst,
    output wire                       m_axi_arlock,
    output wire [3:0]                 m_axi_arcache,
    output wire [2:0]                 m_axi_arprot,
    output wire                       m_axi_arvalid,
    input  wire                       m_axi_arready,
    input  wire [AXI_ID_WIDTH-1:0]    m_axi_rid,
    input  wire [AXI_DATA_WIDTH-1:0]  m_axi_rdata,
    input  wire [1:0]                 m_axi_rresp,
    input  wire                       m_axi_rlast,
    input  wire                       m_axi_rvalid,
    output wire                       m_axi_rready,

    // Configuration
    input  wire                       enable  // Configuration enable signal
);

endmodule
