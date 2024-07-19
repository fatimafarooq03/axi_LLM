// Create a Verilog module named axil_adapter_wr.

// The module should serve as an AXI lite width adapter module with parametrizable data and address interface widths.

// Develop a Verilog module that includes the following parameters and ports:

module axil_adapter_wr #
(
    // Parameters
    parameter ADDR_WIDTH = 32,  // Width of address bus in bits
    parameter S_DATA_WIDTH = 32,  // Width of input (slave) interface data bus in bits
    parameter S_STRB_WIDTH = (S_DATA_WIDTH/8),  // Width of input (slave) interface wstrb (width of data bus in words)
    parameter M_DATA_WIDTH = 32,  // Width of output (master) interface data bus in bits
    parameter M_STRB_WIDTH = (M_DATA_WIDTH/8)  // Width of output (master) interface wstrb (width of data bus in words)
)
(
    // Ports
    input  wire                     clk,  // Clock signal
    input  wire                     rst,  // Reset signal

    /*
     * AXI lite slave interface
     */
    input  wire [ADDR_WIDTH-1:0]    s_axil_awaddr,
    input  wire [2:0]               s_axil_awprot,
    input  wire                     s_axil_awvalid,
    output wire                     s_axil_awready,
    input  wire [S_DATA_WIDTH-1:0]  s_axil_wdata,
    input  wire [S_STRB_WIDTH-1:0]  s_axil_wstrb,
    input  wire                     s_axil_wvalid,
    output wire                     s_axil_wready,
    output wire [1:0]               s_axil_bresp,
    output wire                     s_axil_bvalid,
    input  wire                     s_axil_bready,

    /*
     * AXI lite master interface
     */
    output wire [ADDR_WIDTH-1:0]    m_axil_awaddr,
    output wire [2:0]               m_axil_awprot,
    output wire                     m_axil_awvalid,
    input  wire                     m_axil_awready,
    output wire [M_DATA_WIDTH-1:0]  m_axil_wdata,
    output wire [M_STRB_WIDTH-1:0]  m_axil_wstrb,
    output wire                     m_axil_wvalid,
    input  wire                     m_axil_wready,
    input  wire [1:0]               m_axil_bresp,
    input  wire                     m_axil_bvalid,
    output wire                     m_axil_bready
);

// The final output should be a complete Verilog code snippet with the module definition, input/output declaration, and the logic to handle the AXI lite width adaptation functionality.

endmodule
