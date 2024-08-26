module axi_crossbar_wr #
(
    // Parameters
    parameter S_COUNT = 4,
    parameter M_COUNT = 4,
    parameter DATA_WIDTH = 32,
    parameter ADDR_WIDTH = 32,
    parameter STRB_WIDTH = (DATA_WIDTH/8),
    parameter S_ID_WIDTH = 8,
    parameter M_ID_WIDTH = S_ID_WIDTH+$clog2(S_COUNT),
    parameter AWUSER_ENABLE = 0,
    parameter AWUSER_WIDTH = 1,
    parameter WUSER_ENABLE = 0,
    parameter WUSER_WIDTH = 1,
    parameter BUSER_ENABLE = 0,
    parameter BUSER_WIDTH = 1,
    parameter S_THREADS = {S_COUNT{32'd2}},
    parameter S_ACCEPT = {S_COUNT{32'd16}},
    parameter M_REGIONS = 1,
    parameter M_BASE_ADDR = 0,
    parameter M_ADDR_WIDTH = {M_COUNT{{M_REGIONS{32'd24}}}},
    parameter M_CONNECT = {M_COUNT{{S_COUNT{1'b1}}}},
    parameter M_ISSUE = {M_COUNT{32'd4}},
    parameter M_SECURE = {M_COUNT{1'b0}},
    parameter S_AW_REG_TYPE = {S_COUNT{2'd0}},
    parameter S_W_REG_TYPE = {S_COUNT{2'd0}},
    parameter S_B_REG_TYPE = {S_COUNT{2'd1}},
    parameter M_AW_REG_TYPE = {M_COUNT{2'd1}},
    parameter M_W_REG_TYPE = {M_COUNT{2'd2}},
    parameter M_B_REG_TYPE = {M_COUNT{2'd0}}
)
(
    input  wire                             clk,
    input  wire                             rst,

    // AXI Slave Interfaces
    input  wire [S_COUNT*S_ID_WIDTH-1:0]    s_axi_awid,
    input  wire [S_COUNT*ADDR_WIDTH-1:0]    s_axi_awaddr,
    input  wire [S_COUNT*8-1:0]             s_axi_awlen,
    input  wire [S_COUNT*3-1:0]             s_axi_awsize,
    input  wire [S_COUNT*2-1:0]             s_axi_awburst,
    input  wire [S_COUNT-1:0]               s_axi_awlock,
    input  wire [S_COUNT*4-1:0]             s_axi_awcache,
    input  wire [S_COUNT*3-1:0]             s_axi_awprot,
    input  wire [S_COUNT*4-1:0]             s_axi_awqos,
    input  wire [S_COUNT*AWUSER_WIDTH-1:0]  s_axi_awuser,
    input  wire [S_COUNT-1:0]               s_axi_awvalid,
    output wire [S_COUNT-1:0]               s_axi_awready,
    input  wire [S_COUNT*DATA_WIDTH-1:0]    s_axi_wdata,
    input  wire [S_COUNT*STRB_WIDTH-1:0]    s_axi_wstrb,
    input  wire [S_COUNT-1:0]               s_axi_wlast,
    input  wire [S_COUNT*WUSER_WIDTH-1:0]   s_axi_wuser,
    input  wire [S_COUNT-1:0]               s_axi_wvalid,
    output wire [S_COUNT-1:0]               s_axi_wready,
    output wire [S_COUNT*S_ID_WIDTH-1:0]    s_axi_bid,
    output wire [S_COUNT*2-1:0]             s_axi_bresp,
    output wire [S_COUNT*BUSER_WIDTH-1:0]   s_axi_buser,
    output wire [S_COUNT-1:0]               s_axi_bvalid,
    input  wire [S_COUNT-1:0]               s_axi_bready,

    // AXI Master Interfaces
    output wire [M_COUNT*M_ID_WIDTH-1:0]    m_axi_awid,
    output wire [M_COUNT*ADDR_WIDTH-1:0]    m_axi_awaddr,
    output wire [M_COUNT*8-1:0]             m_axi_awlen,
    output wire [M_COUNT*3-1:0]             m_axi_awsize,
    output wire [M_COUNT*2-1:0]             m_axi_awburst,
    output wire [M_COUNT-1:0]               m_axi_awlock,
    output wire [M_COUNT*4-1:0]             m_axi_awcache,
    output wire [M_COUNT*3-1:0]             m_axi_awprot,
    output wire [M_COUNT*4-1:0]             m_axi_awqos,
    output wire [M_COUNT*4-1:0]             m_axi_awregion,
    output wire [M_COUNT*AWUSER_WIDTH-1:0]  m_axi_awuser,
    output wire [M_COUNT-1:0]               m_axi_awvalid,
    input  wire [M_COUNT-1:0]               m_axi_awready,
    output wire [M_COUNT*DATA_WIDTH-1:0]    m_axi_wdata,
    output wire [M_COUNT*STRB_WIDTH-1:0]    m_axi_wstrb,
    output wire [M_COUNT-1:0]               m_axi_wlast,
    output wire [M_COUNT*WUSER_WIDTH-1:0]   m_axi_wuser,
    output wire [M_COUNT-1:0]               m_axi_wvalid,
    input  wire [M_COUNT-1:0]               m_axi_wready,
    input  wire [M_COUNT*M_ID_WIDTH-1:0]    m_axi_bid,
    input  wire [M_COUNT*2-1:0]             m_axi_bresp,
    input  wire [M_COUNT*BUSER_WIDTH-1:0]   m_axi_buser,
    input  wire [M_COUNT-1:0]               m_axi_bvalid,
    output wire [M_COUNT-1:0]               m_axi_bready
);

// Internal registers
reg [S_COUNT*S_ID_WIDTH-1:0] selected_master;

// Address decode submodules
genvar i;
generate
    for (i = 0; i < S_COUNT; i = i + 1) begin : address_decode
        // Instantiate axi_crossbar_addr submodule (assume it exists)
        axi_crossbar_addr #
        (
            .ADDR_WIDTH(ADDR_WIDTH),
            .M_COUNT(M_COUNT),
            .M_BASE_ADDR(M_BASE_ADDR),
            .M_ADDR_WIDTH(M_ADDR_WIDTH)
        )
        axi_crossbar_addr_inst
        (
            .clk(clk),
            .rst(rst),
            .s_awaddr(s_axi_awaddr[i*ADDR_WIDTH +: ADDR_WIDTH]),
            .m_select(selected_master[i*S_ID_WIDTH +: S_ID_WIDTH])
        );
    end
endgenerate

// Write data routing logic
always @(posedge clk or posedge rst) begin
    if (rst) begin
        selected_master <= {S_COUNT*S_ID_WIDTH{1'b0}};
    end else begin
        for (i = 0; i < S_COUNT; i = i + 1) begin
            if (s_axi_awvalid[i] && s_axi_awready[i]) begin
                selected_master[i*S_ID_WIDTH +: S_ID_WIDTH] <= axi_crossbar_addr_inst[i].m_select;
            end
        end
    end
end

// Generate output signals for write data and write response channels
endmodule