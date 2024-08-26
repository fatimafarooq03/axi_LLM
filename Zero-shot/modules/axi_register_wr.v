module axi_register_wr #
(
    // Parameters
    parameter DATA_WIDTH = 32,  // Width of data bus in bits
    parameter ADDR_WIDTH = 32,  // Width of address bus in bits
    parameter STRB_WIDTH = (DATA_WIDTH/8),  // Width of wstrb (width of data bus in words)
    parameter ID_WIDTH = 8,  // Width of ID signal
    parameter AWUSER_ENABLE = 0,  // Propagate awuser signal
    parameter AWUSER_WIDTH = 1,  // Width of awuser signal
    parameter WUSER_ENABLE = 0,  // Propagate wuser signal
    parameter WUSER_WIDTH = 1,  // Width of wuser signal
    parameter BUSER_ENABLE = 0,  // Propagate buser signal
    parameter BUSER_WIDTH = 1,  // Width of buser signal
    parameter AW_REG_TYPE = 1,  // AW channel register type: 0 to bypass, 1 for simple buffer, 2 for skid buffer
    parameter W_REG_TYPE = 2,  // W channel register type: 0 to bypass, 1 for simple buffer, 2 for skid buffer
    parameter B_REG_TYPE = 1  // B channel register type: 0 to bypass, 1 for simple buffer, 2 for skid buffer
)
(
    // Ports
    input  wire                     clk,  // Clock signal
    input  wire                     rst,  // Reset signal

    /*
     * AXI slave interface
     */
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
    input  wire [DATA_WIDTH-1:0]    s_axi_wdata,
    input  wire [STRB_WIDTH-1:0]    s_axi_wstrb,
    input  wire                     s_axi_wlast,
    input  wire [WUSER_WIDTH-1:0]   s_axi_wuser,
    input  wire                     s_axi_wvalid,
    output wire                     s_axi_wready,
    output wire [ID_WIDTH-1:0]      s_axi_bid,
    output wire [1:0]               s_axi_bresp,
    output wire [BUSER_WIDTH-1:0]   s_axi_buser,
    output wire                     s_axi_bvalid,
    input  wire                     s_axi_bready,

    /*
     * AXI master interface
     */
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
    output wire [DATA_WIDTH-1:0]    m_axi_wdata,
    output wire [STRB_WIDTH-1:0]    m_axi_wstrb,
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

// Write address (AW) channel

reg [ID_WIDTH-1:0] awid_reg;
reg [ADDR_WIDTH-1:0] awaddr_reg;
reg [7:0] awlen_reg;
reg [2:0] awsize_reg;
reg [1:0] awburst_reg;
reg        awlock_reg;
reg [3:0] awcache_reg;
reg [2:0] awprot_reg;
reg [3:0] awqos_reg;
reg [3:0] awregion_reg;
reg [AWUSER_WIDTH-1:0] awuser_reg;
reg        awvalid_reg;

wire aw_fifo_full;
reg aw_fifo_full_reg;
assign s_axi_awready = ~aw_fifo_full_reg;

always @(posedge clk or posedge rst) begin
    if (rst) begin
        aw_fifo_full_reg <= 1'b0;
    end else begin
        if (s_axi_awvalid & ~aw_fifo_full_reg) begin
            awid_reg <= s_axi_awid;
            awaddr_reg <= s_axi_awaddr;
            awlen_reg <= s_axi_awlen;
            awsize_reg <= s_axi_awsize;
            awburst_reg <= s_axi_awburst;
            awlock_reg <= s_axi_awlock;
            awcache_reg <= s_axi_awcache;
            awprot_reg <= s_axi_awprot;
            awqos_reg <= s_axi_awqos;
            awregion_reg <= s_axi_awregion;
            awuser_reg <= s_axi_awuser;
        end
        if (s_axi_awvalid & m_axi_awready & ~aw_fifo_full_reg) begin
            aw_fifo_full_reg <= 1'b0;
        end else if (s_axi_awvalid & ~m_axi_awready & ~aw_fifo_full_reg) begin
            aw_fifo_full_reg <= 1'b1;
        end else if (~s_axi_awvalid & m_axi_awready & aw_fifo_full_reg) begin
            aw_fifo_full_reg <= 1'b0;
        end
    end
end

assign m_axi_awid = awid_reg;
assign m_axi_awaddr = awaddr_reg;
assign m_axi_awlen = awlen_reg;
assign m_axi_awsize = awsize_reg;
assign m_axi_awburst = awburst_reg;
assign m_axi_awlock = awlock_reg;
assign m_axi_awcache = awcache_reg;
assign m_axi_awprot = awprot_reg;
assign m_axi_awqos = awqos_reg;
assign m_axi_awregion = awregion_reg;
assign m_axi_awuser = awuser_reg;
assign m_axi_awvalid = s_axi_awvalid | aw_fifo_full_reg;

// Write data (W) channel

reg [DATA_WIDTH-1:0] wdata_reg;
reg [STRB_WIDTH-1:0] wstrb_reg;
reg wlast_reg;
reg [WUSER_WIDTH-1:0] wuser_reg;
reg wvalid_reg;

wire w_fifo_full;
reg w_fifo_full_reg;
assign s_axi_wready = ~w_fifo_full_reg;

always @(posedge clk or posedge rst) begin
    if (rst) begin
        w_fifo_full_reg <= 1'b0;
    end else begin
        if (s_axi_wvalid & ~w_fifo_full_reg) begin
            wdata_reg <= s_axi_wdata;
            wstrb_reg <= s_axi_wstrb;
            wlast_reg <= s_axi_wlast;
            wuser_reg <= s_axi_wuser;
        end
        if (s_axi_wvalid & m_axi_wready & ~w_fifo_full_reg) begin
            w_fifo_full_reg <= 1'b0;
        end else if (s_axi_wvalid & ~m_axi_wready & ~w_fifo_full_reg) begin
            w_fifo_full_reg <= 1'b1;
        end else if (~s_axi_wvalid & m_axi_wready & w_fifo_full_reg) begin
            w_fifo_full_reg <= 1'b0;
        end
    end
end

assign m_axi_wdata = wdata_reg;
assign m_axi_wstrb = wstrb_reg;
assign m_axi_wlast = wlast_reg;
assign m_axi_wuser = wuser_reg;
assign m_axi_wvalid = s_axi_wvalid | w_fifo_full_reg;

// Write response (B) channel

reg [ID_WIDTH-1:0] bid_reg;
reg [1:0] bresp_reg;
reg [BUSER_WIDTH-1:0] buser_reg;
reg bvalid_reg;

wire b_fifo_full;
reg b_fifo_full_reg;
assign s_axi_bvalid = bvalid_reg | b_fifo_full_reg;
assign s_axi_bid = b_fifo_full_reg ? bid_reg : m_axi_bid;
assign s_axi_bresp = b_fifo_full_reg ? bresp_reg : m_axi_bresp;
assign s_axi_buser = b_fifo_full_reg ? buser_reg : m_axi_buser;

always @(posedge clk or posedge rst) begin
    if (rst) begin
        b_fifo_full_reg <= 1'b0;
        bvalid_reg <= 1'b0;
    end else begin
        if (m_axi_bvalid & ~b_fifo_full_reg) begin
            bid_reg <= m_axi_bid;
            bresp_reg <= m_axi_bresp;
            buser_reg <= m_axi_buser;
            bvalid_reg <= 1'b1;
        end
        if (m_axi_bvalid & s_axi_bready & ~b_fifo_full_reg) begin
            b_fifo_full_reg <= 1'b0;
            bvalid_reg <= 1'b0;
        end else if (m_axi_bvalid & ~s_axi_bready & ~b_fifo_full_reg) begin
            b_fifo_full_reg <= 1'b1;
        end else if (~m_axi_bvalid & s_axi_bready & b_fifo_full_reg) begin
            b_fifo_full_reg <= 1'b0;
        end
    end
end

assign m_axi_bready = s_axi_bready | b_fifo_full_reg;

endmodule