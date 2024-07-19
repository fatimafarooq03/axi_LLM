// Create a Verilog module named axil_adapter_rd.

// The module should serve as an AXI lite width adapter module with parametrizable data and address interface widths.

// Develop a Verilog module that includes the following parameters and ports:

module axil_adapter_rd #
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
    input  wire [ADDR_WIDTH-1:0]    s_axil_araddr,
    input  wire [2:0]               s_axil_arprot,
    input  wire                     s_axil_arvalid,
    output wire                     s_axil_arready,
    output wire [S_DATA_WIDTH-1:0]  s_axil_rdata,
    output wire [1:0]               s_axil_rresp,
    output wire                     s_axil_rvalid,
    input  wire                     s_axil_rready,

    /*
     * AXI lite master interface
     */
    output wire [ADDR_WIDTH-1:0]    m_axil_araddr,
    output wire [2:0]               m_axil_arprot,
    output wire                     m_axil_arvalid,
    input  wire                     m_axil_arready,
    input  wire [M_DATA_WIDTH-1:0]  m_axil_rdata,
    input  wire [1:0]               m_axil_rresp,
    input  wire                     m_axil_rvalid,
    output wire                     m_axil_rready
);

// The final output should be a complete Verilog code snippet with the module definition, input/output declaration, and the logic to handle the AXI lite width adaptation functionality.

endmodule
