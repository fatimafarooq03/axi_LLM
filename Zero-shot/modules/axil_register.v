module axil_register #
(
    // Parameters
    parameter DATA_WIDTH = 32,  // Width of data bus in bits
    parameter ADDR_WIDTH = 32,  // Width of address bus in bits
    parameter STRB_WIDTH = (DATA_WIDTH/8),  // Width of wstrb (width of data bus in words)
    parameter AW_REG_TYPE = 1,  // AW channel register type: 0 to bypass, 1 for simple buffer
    parameter W_REG_TYPE = 1,  // W channel register type: 0 to bypass, 1 for simple buffer
    parameter B_REG_TYPE = 1,  // B channel register type: 0 to bypass, 1 for simple buffer
    parameter AR_REG_TYPE = 1,  // AR channel register type: 0 to bypass, 1 for simple buffer
    parameter R_REG_TYPE = 1  // R channel register type: 0 to bypass, 1 for simple buffer
)
(
    // Ports
    input  wire                     clk,  // Clock signal
    input  wire                     rst,  // Reset signal

    /*
     * AXI lite slave interface
     */
    input  wire [ADDR_WIDTH-1:0]    s_axil_awaddr,  // Write address
    input  wire [2:0]               s_axil_awprot,  // Write protection type
    input  wire                     s_axil_awvalid,  // Write address valid
    output wire                     s_axil_awready,  // Write address ready
    input  wire [DATA_WIDTH-1:0]    s_axil_wdata,  // Write data
    input  wire [STRB_WIDTH-1:0]    s_axil_wstrb,  // Write strobes
    input  wire                     s_axil_wvalid,  // Write valid
    output wire                     s_axil_wready,  // Write ready
    output wire [1:0]               s_axil_bresp,  // Write response
    output wire                     s_axil_bvalid,  // Write response valid
    input  wire                     s_axil_bready,  // Write response ready
    input  wire [ADDR_WIDTH-1:0]    s_axil_araddr,  // Read address
    input  wire [2:0]               s_axil_arprot,  // Read protection type
    input  wire                     s_axil_arvalid,  // Read address valid
    output wire                     s_axil_arready,  // Read address ready
    output wire [DATA_WIDTH-1:0]    s_axil_rdata,  // Read data
    output wire [1:0]               s_axil_rresp,  // Read response
    output wire                     s_axil_rvalid,  // Read response valid
    input  wire                     s_axil_rready,  // Read response ready

    /*
     * AXI lite master interface
     */
    output wire [ADDR_WIDTH-1:0]    m_axil_awaddr,  // Master write address
    output wire [2:0]               m_axil_awprot,  // Master write protection type
    output wire                     m_axil_awvalid,  // Master write address valid
    input  wire                     m_axil_awready,  // Master write address ready
    output wire [DATA_WIDTH-1:0]    m_axil_wdata,  // Master write data
    output wire [STRB_WIDTH-1:0]    m_axil_wstrb,  // Master write strobes
    output wire                     m_axil_wvalid,  // Master write valid
    input  wire                     m_axil_wready,  // Master write ready
    input  wire [1:0]               m_axil_bresp,  // Master write response
    input  wire                     m_axil_bvalid,  // Master write response valid
    output wire                     m_axil_bready,  // Master write response ready
    output wire [ADDR_WIDTH-1:0]    m_axil_araddr,  // Master read address
    output wire [2:0]               m_axil_arprot,  // Master read protection type
    output wire                     m_axil_arvalid,  // Master read address valid
    input  wire                     m_axil_arready,  // Master read address ready
    input  wire [DATA_WIDTH-1:0]    m_axil_rdata,  // Master read data
    input  wire [1:0]               m_axil_rresp,  // Master read response
    input  wire                     m_axil_rvalid,  // Master read response valid
    output wire                     m_axil_rready  // Master read response ready
);

// Internal signal declarations
wire aw_ready, aw_valid;
wire w_ready, w_valid;
wire b_ready, b_valid;
wire ar_ready, ar_valid;
wire r_ready, r_valid;

// Write channel instantiation
axil_register_wr #(
    .DATA_WIDTH(DATA_WIDTH),
    .ADDR_WIDTH(ADDR_WIDTH),
    .STRB_WIDTH(STRB_WIDTH),
    .AW_REG_TYPE(AW_REG_TYPE),
    .W_REG_TYPE(W_REG_TYPE),
    .B_REG_TYPE(B_REG_TYPE)
)
axil_register_wr_inst (
    .clk(clk),
    .rst(rst),
    .s_axil_awaddr(s_axil_awaddr),
    .s_axil_awprot(s_axil_awprot),
    .s_axil_awvalid(s_axil_awvalid),
    .s_axil_awready(s_axil_awready),
    .s_axil_wdata(s_axil_wdata),
    .s_axil_wstrb(s_axil_wstrb),
    .s_axil_wvalid(s_axil_wvalid),
    .s_axil_wready(s_axil_wready),
    .s_axil_bresp(s_axil_bresp),
    .s_axil_bvalid(s_axil_bvalid),
    .s_axil_bready(s_axil_bready),
    .m_axil_awaddr(m_axil_awaddr),
    .m_axil_awprot(m_axil_awprot),
    .m_axil_awvalid(aw_valid),
    .m_axil_awready(aw_ready),
    .m_axil_wdata(m_axil_wdata),
    .m_axil_wstrb(m_axil_wstrb),
    .m_axil_wvalid(w_valid),
    .m_axil_wready(w_ready),
    .m_axil_bresp(m_axil_bresp),
    .m_axil_bvalid(b_valid),
    .m_axil_bready(b_ready)
);

// Read channel instantiation
axil_register_rd #(
    .DATA_WIDTH(DATA_WIDTH),
    .ADDR_WIDTH(ADDR_WIDTH),
    .AR_REG_TYPE(AR_REG_TYPE),
    .R_REG_TYPE(R_REG_TYPE)
)
axil_register_rd_inst (
    .clk(clk),
    .rst(rst),
    .s_axil_araddr(s_axil_araddr),
    .s_axil_arprot(s_axil_arprot),
    .s_axil_arvalid(s_axil_arvalid),
    .s_axil_arready(s_axil_arready),
    .s_axil_rdata(s_axil_rdata),
    .s_axil_rresp(s_axil_rresp),
    .s_axil_rvalid(s_axil_rvalid),
    .s_axil_rready(s_axil_rready),
    .m_axil_araddr(m_axil_araddr),
    .m_axil_arprot(m_axil_arprot),
    .m_axil_arvalid(ar_valid),
    .m_axil_arready(ar_ready),
    .m_axil_rdata(m_axil_rdata),
    .m_axil_rresp(m_axil_rresp),
    .m_axil_rvalid(r_valid),
    .m_axil_rready(r_ready)
);

// Assign intermediate signals to output
assign m_axil_awvalid = aw_valid;
assign m_axil_wvalid = w_valid;
assign m_axil_bready = b_ready;
assign m_axil_arvalid = ar_valid;
assign m_axil_rready = r_ready;

endmodule