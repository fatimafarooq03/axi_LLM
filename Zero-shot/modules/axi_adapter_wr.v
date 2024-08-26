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

// Internal parameters and state declarations
localparam STATE_IDLE   = 2'd0;
localparam STATE_DATA   = 2'd1;
localparam STATE_DATA_2 = 2'd2;
localparam STATE_RESP   = 2'd3;

reg [1:0] state_reg, state_next;
reg [ID_WIDTH-1:0] axi_awid_reg;
reg [ADDR_WIDTH-1:0] axi_awaddr_reg;
reg [7:0] axi_awlen_reg;
reg [2:0] axi_awsize_reg;
reg [1:0] axi_awburst_reg;
reg axi_awlock_reg;
reg [3:0] axi_awcache_reg;
reg [2:0] axi_awprot_reg;
reg [3:0] axi_awqos_reg;
reg [3:0] axi_awregion_reg;
reg [AWUSER_WIDTH-1:0] axi_awuser_reg;

reg [S_DATA_WIDTH-1:0] s_wdata_reg;
reg [S_STRB_WIDTH-1:0] s_wstrb_reg;

reg s_wvalid_reg, s_wready_reg;
reg m_wvalid_reg, m_wready_reg;

reg [ID_WIDTH-1:0] s_bid_reg;
reg [1:0] s_bresp_reg;
reg s_bvalid_reg, s_bready_reg;

wire idle_cond;
wire data_cond;
wire data_2_cond;
wire resp_cond;

// Signals for address and control channel
assign s_axi_awready = (state_reg == STATE_IDLE);
assign m_axi_awid = axi_awid_reg;
assign m_axi_awaddr = axi_awaddr_reg;
assign m_axi_awlen = axi_awlen_reg;
assign m_axi_awsize = axi_awsize_reg;
assign m_axi_awburst = axi_awburst_reg;
assign m_axi_awlock = axi_awlock_reg;
assign m_axi_awcache = axi_awcache_reg;
assign m_axi_awprot = axi_awprot_reg;
assign m_axi_awqos = axi_awqos_reg;
assign m_axi_awregion = axi_awregion_reg;
assign m_axi_awuser = axs_awuser_reg;
assign m_axi_awvalid = (state_reg == STATE_IDLE) && s_axi_awvalid;

// Signals for write channel
assign s_axi_wready = (state_reg == STATE_DATA) && m_axi_wready;
assign m_axi_wdata = s_wdata_reg;
assign m_axi_wstrb = s_wisolation_reg;
assign m_axi_wvalid = (state_reg == STATE_DATA) && s_axi_wvalid;
assign m_axi_wlast = s_axi_wlast;

// Signals for response channel
assign s_axi_bid = s_bid_reg;
assign s_axi_bresp = s_bresp_reg;
assign s_axi_bvalid = (state_reg == STATE_RESP) && m_axi_bvalid;
assign m_axi_bready = s_bready_reg;

// State Machine for AXI write transactions
always@(posedge clk or posedge rst) begin
    if(rst) begin
        state_reg <= STATE_IDLE;
    end else begin
        state_reg <= state_next;
    end
end

always@* begin
    state_next = state_reg;
    case(state_reg) 
        // IDLE State
        STATE_IDLE: begin
            if(s_axi_awvalid) begin
                axi_awid_reg = s_axi_awid;
                axi_awaddr_reg = s_axi_awaddr;
                axi_awlen_reg = s_axi_awlen;
                axi_awsize_reg = s_axi_awsize;
                axi_awburst_reg = s_axi_awburst;
                axi_awlock_reg = s_axi_awlock;
                axi_awcache_reg = s_axi_awcache;
                axi_awprot_reg = s_axi_awprot;
                axi_awqos_reg = s_axi_awqos;
                axi_awregion_reg = s_axi_awregion;
                axi_awuser_reg = s_axi_awuser;
                state_next = (M_DATA_WIDTH > S_DATA_WIDTH )? STATE_DATA : STATE_DATA_2;
            end
        end
        // DATA State
        STATE_DATA: begin
            if(s_axi_wvalid && m_axi_wready) begin
                s_wdata_reg = s_axi_wdata;
                s_wstrb_reg = s_axi_wstrb;
                s_wvalid_reg = s_axi_wvalid;
                m_wvalid_reg = (M_DATA_WIDTH == S_DATA_WIDTH || M_DATA_WIDTH > S_DATA_WIDTH );
                if(s_axi_wlast) begin
                    state_next = STATE_RESP;
                end else if(M_DATA_WIDTH > S_DATA_WIDTH ) begin
                    state_next = STATE_DATA_2;
                end
            end
        end
        // DATA_2 State
        STATE_DATA_2: begin
            if(s_wvalid_reg && m_axi_wready) begin
                m_wvalid_reg = 1'b0;
                state_next = STATE_DATA;
                s_wvalid_reg = 1'b0;
            end
            else begin
                s_wvalid_reg = 1'b1;
                state_next = state_reg;
            end
        end
        // RESP State
        STATE_RESP: begin
            if(m_axi_bvalid) begin
                s_bresp_reg = m_axi_bresp;
                s_Bid_reg = m_axi_bid;
                s_bvalid_reg = 1'b1;
                if(s_axi_bready && m_axi_bvalid){
                    state_note = STATE_IDLE;
                end
            end
            else begin
                s_bvalid_reg = 1'b0;                             
                state_next = state_reg;
            end
        end 
    endcase
end

endmodule