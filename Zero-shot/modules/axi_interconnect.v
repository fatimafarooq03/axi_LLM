module axi_interconnect #
(
    // Parameters
    parameter S_COUNT = 4,  // Number of AXI inputs (slave interfaces)
    parameter M_COUNT = 4,  // Number of AXI outputs (master interfaces)
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
    parameter ARUSER_ENABLE = 0,  // Propagate aruser signal
    parameter ARUSER_WIDTH = 1,  // Width of aruser signal
    parameter RUSER_ENABLE = 0,  // Propagate ruser signal
    parameter RUSER_WIDTH = 1,  // Width of ruser signal
    parameter FORWARD_ID = 0,  // Propagate ID field
    parameter M_REGIONS = 1,  // Number of regions per master interface
    parameter M_BASE_ADDR = 0,  // Master interface base addresses
    parameter M_ADDR_WIDTH = {M_COUNT{{M_REGIONS{32'd24}}}},  // Master interface address widths
    parameter M_CONNECT_READ = {M_COUNT{{S_COUNT{1'b1}}}},  // Read connections between interfaces
    parameter M_CONNECT_WRITE = {M_COUNT{{S_COUNT{1'b1}}}},  // Write connections between interfaces
    parameter M_SECURE = {M_COUNT{1'b0}}  // Secure master (fail operations based on awprot/arprot)
)
(
    // Ports
    input  wire                            clk,  // Clock signal
    input  wire                            rst,  // Reset signal

    // AXI slave interfaces
    input  wire [S_COUNT*ID_WIDTH-1:0]     s_axi_awid,
    input  wire [S_COUNT*ADDR_WIDTH-1:0]   s_axi_awaddr,
    input  wire [S_COUNT*8-1:0]            s_axi_awlen,
    input  wire [S_COUNT*3-1:0]            s_axi_awsize,
    input  wire [S_COUNT*2-1:0]            s_axi_awburst,
    input  wire [S_COUNT-1:0]              s_axi_awlock,
    input  wire [S_COUNT*4-1:0]            s_axi_awcache,
    input  wire [S_COUNT*3-1:0]            s_axi_awprot,
    input  wire [S_COUNT*4-1:0]            s_axi_awqos,
    input  wire [S_COUNT*AWUSER_WIDTH-1:0] s_axi_awuser,
    input  wire [S_COUNT-1:0]              s_axi_awvalid,
    output wire [S_COUNT-1:0]              s_axi_awready,
    input  wire [S_COUNT*DATA_WIDTH-1:0]   s_axi_wdata,
    input  wire [S_COUNT*STRB_WIDTH-1:0]   s_axi_wstrb,
    input  wire [S_COUNT-1:0]              s_axi_wlast,
    input  wire [S_COUNT*WUSER_WIDTH-1:0]  s_axi_wuser,
    input  wire [S_COUNT-1:0]              s_axi_wvalid,
    output wire [S_COUNT-1:0]              s_axi_wready,
    output wire [S_COUNT*ID_WIDTH-1:0]     s_axi_bid,
    output wire [S_COUNT*2-1:0]            s_axi_bresp,
    output wire [S_COUNT*BUSER_WIDTH-1:0]  s_axi_buser,
    output wire [S_COUNT-1:0]              s_axi_bvalid,
    input  wire [S_COUNT-1:0]              s_axi_bready,
    input  wire [S_COUNT*ID_WIDTH-1:0]     s_axi_arid,
    input  wire [S_COUNT*ADDR_WIDTH-1:0]   s_axi_araddr,
    input  wire [S_COUNT*8-1:0]            s_axi_arlen,
    input  wire [S_COUNT*3-1:0]            s_axi_arsize,
    input  wire [S_COUNT*2-1:0]            s_axi_arburst,
    input  wire [S_COUNT-1:0]              s_axi_arlock,
    input  wire [S_COUNT*4-1:0]            s_axi_arcache,
    input  wire [S_COUNT*3-1:0]            s_axi_arprot,
    input  wire [S_COUNT*4-1:0]            s_axi_arqos,
    input  wire [S_COUNT*ARUSER_WIDTH-1:0] s_axi_aruser,
    input  wire [S_COUNT-1:0]              s_axi_arvalid,
    output wire [S_COUNT-1:0]              s_axi_arready,
    output wire [S_COUNT*ID_WIDTH-1:0]     s_axi_rid,
    output wire [S_COUNT*DATA_WIDTH-1:0]   s_axi_rdata,
    output wire [S_COUNT*2-1:0]            s_axi_rresp,
    output wire [S_COUNT-1:0]              s_axi_rlast,
    output wire [S_COUNT*RUSER_WIDTH-1:0]  s_axi_ruser,
    output wire [S_COUNT-1:0]              s_axi_rvalid,
    input  wire [S_COUNT-1:0]              s_axi_rready,

    // AXI master interfaces
    output wire [M_COUNT*ID_WIDTH-1:0]     m_axi_awid,
    output wire [M_COUNT*ADDR_WIDTH-1:0]   m_axi_awaddr,
    output wire [M_COUNT*8-1:0]            m_axi_awlen,
    output wire [M_COUNT*3-1:0]            m_axi_awsize,
    output wire [M_COUNT*2-1:0]            m_axi_awburst,
    output wire [M_COUNT-1:0]              m_axi_awlock,
    output wire [M_COUNT*4-1:0]            m_axi_awcache,
    output wire [M_COUNT*3-1:0]            m_axi_awprot,
    output wire [M_COUNT*4-1:0]            m_axi_awqos,
    output wire [M_COUNT*4-1:0]            m_axi_awregion,
    output wire [M_COUNT*AWUSER_WIDTH-1:0] m_axi_awuser,
    output wire [M_COUNT-1:0]              m_axi_awvalid,
    input  wire [M_COUNT-1:0]              m_axi_awready,
    output wire [M_COUNT*DATA_WIDTH-1:0]   m_axi_wdata,
    output wire [M_COUNT*STRB_WIDTH-1:0]   m_axi_wstrb,
    output wire [M_COUNT-1:0]              m_axi_wlast,
    output wire [M_COUNT*WUSER_WIDTH-1:0]  m_axi_wuser,
    output wire [M_COUNT-1:0]              m_axi_wvalid,
    input  wire [M_COUNT-1:0]              m_axi_wready,
    input  wire [M_COUNT*ID_WIDTH-1:0]     m_axi_bid,
    input  wire [M_COUNT*2-1:0]            m_axi_bresp,
    input  wire [M_COUNT*BUSER_WIDTH-1:0]  m_axi_buser,
    input  wire [M_COUNT-1:0]              m_axi_bvalid,
    output wire [M_COUNT-1:0]              m_axi_bready,
    output wire [M_COUNT*ID_WIDTH-1:0]     m_axi_arid,
    output wire [M_COUNT*ADDR_WIDTH-1:0]   m_axi_araddr,
    output wire [M_COUNT*8-1:0]            m_axi_arlen,
    output wire [M_COUNT*3-1:0]            m_axi_arsize,
    output wire [M_COUNT*2-1:0]            m_axi_arburst,
    output wire [M_COUNT-1:0]              m_axi_arlock,
    output wire [M_COUNT*4-1:0]            m_axi_arcache,
    output wire [M_COUNT*3-1:0]            m_axi_arprot,
    output wire [M_COUNT*4-1:0]            m_axi_arqos,
    output wire [M_COUNT*4-1:0]            m_axi_arregion,
    output wire [M_COUNT*ARUSER_WIDTH-1:0] m_axi_aruser,
    output wire [M_COUNT-1:0]              m_axi_arvalid,
    input  wire [M_COUNT-1:0]              m_axi_arready,
    input  wire [M_COUNT*ID_WIDTH-1:0]     m_axi_rid,
    input  wire [M_COUNT*DATA_WIDTH-1:0]   m_axi_rdata,
    input  wire [M_COUNT*2-1:0]            m_axi_rresp,
    input  wire [M_COUNT-1:0]              m_axi_rlast,
    input  wire [M_COUNT*RUSER_WIDTH-1:0]  m_axi_ruser,
    input  wire [M_COUNT-1:0]              m_axi_rvalid,
    output wire [M_COUNT-1:0]              m_axi_rready
);

// Internal signals and FSM states
localparam [2:0] 
    STATE_IDLE       = 3'd0,
    STATE_DECODE     = 3'd1,
    STATE_WRITE      = 3'd2,
    STATE_WRITE_RESP = 3'd3,
    STATE_WRITE_DROP = 3'd4,
    STATE_READ       = 3'd5,
    STATE_READ_DROP  = 3'd6,
    STATE_WAIT_IDLE  = 3'd7;

reg [2:0] state_reg, state_next;

// Signal declarations for arbitration, decoding and data transfer
wire [M_COUNT-1:0] aw_arb_grant, ar_arb_grant;
reg [ADDR_WIDTH-1:0] awaddr_mux, araddr_mux;
reg [DATA_WIDTH-1:0] wdata_mux, rdata_buf;
reg wvalid_mux, rready_buf;

axi_arbiter #(
    .PORTS(S_COUNT),
    .TYPE("ROUND_ROBIN")
) aw_arbiter_inst (
    .clk(clk),
    .rst(rst),
    .request(s_axi_awvalid),
    .grant(aw_arb_grant)
);

axi_arbiter #(
    .PORTS(S_COUNT),
    .TYPE("ROUND_ROBIN")
) ar_arbiter_inst (
    .clk(clk),
    .rst(rst),
    .request(s_axi_arvalid),
    .grant(ar_arb_grant)
);

always @(*) begin
    state_next = state_reg;
    case (state_reg)
        STATE_IDLE: begin
            if (|s_axi_awvalid | |s_axi_arvalid) 
                state_next = STATE_DECODE;
        end
        STATE_DECODE: begin
            if (|s_axi_awvalid) 
                state_next = STATE_WRITE;
            else if(|s_axi_arvalid) 
                state_next = STATE_READ;
        end
        STATE_WRITE: begin
            if (&s_axi_wvalid)
                state_next = STATE_WRITE_RESP;
            else if (!|s_axi_awvalid)
                state_next = STATE_WRITE_DROP;
        end
        STATE_WRITE_RESP: begin
            if (|m_axi_bvalid) 
                state_next = STATE_IDLE;
        end
        STATE_WRITE_DROP: begin
            state_next = STATE_IDLE;
        end
        STATE_READ: begin
            if (|m_axi_rvalid)
                state_next = STATE_IDLE;
            else if (!|s_axi_arvalid)
                state_next = STATE_READ_DROP;
        end
        STATE_READ_DROP: begin
            state_next = STATE_IDLE;
        end
        default: state_next = STATE_IDLE;
    endcase
end

always @(posedge clk) begin
    if (rst) begin
        state_reg <= STATE_IDLE;
    end else begin
        state_reg <= state_next;
    end
end

// Decode the addresses and manage data transfer based on current state
always @(*) begin
    m_axi_awid    = s_axi_awid;
    m_axi_awaddr  = s_axi_awaddr;
    m_axi_awlen   = s_axi_awlen;
    m_axi_awsize  = s_axi_awsize;
    m_axi_awburst = s_axi_awburst;
    m_axi_awlock  = s_axi_awlock;
    m_axi_awcache = s_axi_awcache;
    m_axi_awprot  = s_axi_awprot;
    m_axi_awqos   = s_axi_awqos;
    m_axi_awuser  = s_axi_awuser;
    m_axi_awvalid = s_axi_awvalid & aw_arb_grant;

    m_axi_wdata  = s_axi_wdata;
    m_axi_wstrb  = s_axi_wstrb;
    m_axi_wlast  = s_axi_wlast;
    m_axi_wuser  = s_axi_wuser;
    m_axi_wvalid = s_axi_wvalid & aw_arb_grant;

    s_axi_awready = m_axi_awready;
    s_axi_wready  = m_axi_wready;
    s_axi_bid     = m_axi_bid;
    s_axi_bresp   = m_axi_bresp;
    s_axi_buser   = m_axi_buser;
    s_axi_bvalid  = m_axi_bvalid;
    
    m_axi_arid    = s_axi_arid;
    m_axi_araddr  = s_axi_araddr;
    m_axi_arlen   = s_axi_arlen;
    m_axi_arsize  = s_axi_arsize;
    m_axi_arburst = s_axi_arburst;
    m_axi_arlock  = s_axi_arlock;
    m_axi_arcache = s_axi_arcache;
    m_axi_arprot  = s_axi_arprot;
    m_axi_arqos   = s_axi_arqos;
    m_axi_aruser  = s_axi_aruser;
    m_axi_arvalid = s_axi_arvalid & ar_arb_grant;

    s_axi_arready = m_axi_arready;
    s_axi_rid     = m_axi_rid;
    s_axi_rdata   = m_axi_rdata;
    s_axi_rresp   = m_axi_rresp;
    s_axi_rlast   = m_axi_rlast;
    s_axi_ruser   = m_axi_ruser;
    s_axi_rvalid  = m_axi_rvalid;
end

endmodule