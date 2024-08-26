module axil_adapter #
(
    // Parameters
    parameter ADDR_WIDTH = 32,        // Width of address bus in bits
    parameter S_DATA_WIDTH = 32,      // Width of input (slave) interface data bus in bits
    parameter S_STRB_WIDTH = (S_DATA_WIDTH/8),  // Width of input (slave) interface wstrb (width of data bus in words)
    parameter M_DATA_WIDTH = 32,      // Width of output (master) interface data bus in bits
    parameter M_STRB_WIDTH = (M_DATA_WIDTH/8)   // Width of output (master) interface wstrb (width of data bus in words)
)
(
    // Ports
    input  wire                     clk,    // Clock signal
    input  wire                     rst,    // Reset signal

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
    output wire                     m_axil_bready,
    output wire [ADDR_WIDTH-1:0]    m_axil_araddr,
    output wire [2:0]               m_axil_arprot,
    output wire                     m_axil_arvalid,
    input  wire                     m_axil_arready,
    input  wire [M_DATA_WIDTH-1:0]  m_axil_rdata,
    input  wire [1:0]               m_axil_rresp,
    input  wire                     m_axil_rvalid,
    output wire                     m_axil_rready
);

// Wires to connect subprocesses
wire [ADDR_WIDTH-1:0] awaddr_int;
wire [2:0] awprot_int;
wire awvalid_int;
wire awready_int;
wire [S_DATA_WIDTH-1:0] wdata_int;
wire [S_STRB_WIDTH-1:0] wstrb_int;
wire wvalid_int;
wire wready_int;
wire [1:0] bresp_int;
wire bvalid_int;
wire bready_int;
wire [ADDR_WIDTH-1:0] araddr_int;
wire [2:0] arprot_int;
wire arvalid_int;
wire arready_int;
wire [S_DATA_WIDTH-1:0] rdata_int;
wire [1:0] rresp_int;
wire rvalid_int;
wire rready_int;

// Write Adapter submodule
axil_adapter_wr #(
    .ADDR_WIDTH(ADDR_WIDTH),
    .S_DATA_WIDTH(S_DATA_WIDTH),
    .S_STRB_WIDTH(S_STRB_WIDTH),
    .M_DATA_WIDTH(M_DATA_WIDTH),
    .M_STRB_WIDTH(M_STRB_WIDTH)
) axil_adapter_wr_i (
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
    .m_axil_awaddr(awaddr_int),
    .m_axil_awprot(awprot_int),
    .m_axil_awvalid(awvalid_int),
    .m_axil_awready(awready_int),
    .m_axil_wdata(wdata_int),
    .m_axil_wstrb(wstrb_int),
    .m_axil_wvalid(wvalid_int),
    .m_axil_wready(wready_int),
    .m_axil_bresp(bresp_int),
    .m_axil_bvalid(bvalid_int),
    .m_axil_bready(bready_int)
);

// Read Adapter submodule
axil_adapter_rd #(
    .ADDR_WIDTH(ADDR_WIDTH),
    .S_DATA_WIDTH(S_DATA_WIDTH),
    .M_DATA_WIDTH(M_DATA_WIDTH)
) axil_adapter_rd_i (
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
    .m_axil_araddr(araddr_int),
    .m_axil_arprot(arprot_int),
    .m_axil_arvalid(arvalid_int),
    .m_axil_arready(arready_int),
    .m_axil_rdata(rdata_int),
    .m_axil_rresp(rresp_int),
    .m_axil_rvalid(rvalid_int),
    .m_axil_rready(rready_int)
);

// Connect internal signals to output AXI Lite master interface
assign m_axil_awaddr = awaddr_int;
assign m_axil_awprot = awprot_int;
assign m_axil_awvalid = awvalid_int;
assign awready_int = m_axil_awready;
assign m_axil_wdata = wdata_int;
assign m_axil_wstrb = wstrb_int;
assign m_axil_wvalid = wvalid_int;
assign wready_int = m_axil_wready;
assign bresp_int = m_axil_bresp;
assign bvalid_int = m_axil_bvalid;
assign m_axil_bready = bready_int;
assign m_axil_araddr = araddr_int;
assign m_axil_arprot = arprot_int;
assign m_axil_arvalid = arvalid_int;
assign arready_int = m_axil_arready;
assign rdata_int = m_axil_rdata;
assign rresp_int = m_axil_rresp;
assign rvalid_int = m_axil_rvalid;
assign m_axil_rready = rready_int;

endmodule