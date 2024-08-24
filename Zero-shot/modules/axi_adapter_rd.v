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
    parameter FORWARD_ID = 0,        // Forward ID through adapter
    parameter EXPAND = (M_DATA_WIDTH > S_DATA_WIDTH) // Master bus width is wider (EXPAND = 1) or narrower (EXPAND = 0) than the slave bus
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
    output reg                      s_axi_arready,
    output reg  [ID_WIDTH-1:0]      s_axi_rid,
    output reg  [S_DATA_WIDTH-1:0]  s_axi_rdata,
    output reg  [1:0]               s_axi_rresp,
    output reg                      s_axi_rlast,
    output reg  [RUSER_WIDTH-1:0]   s_axi_ruser,
    output reg                      s_axi_rvalid,
    input  wire                     s_axi_rready,

    // AXI Master Interface
    output reg  [ID_WIDTH-1:0]      m_axi_arid,
    output reg  [ADDR_WIDTH-1:0]    m_axi_araddr,
    output reg  [7:0]               m_axi_arlen,
    output reg  [2:0]               m_axi_arsize,
    output reg  [1:0]               m_axi_arburst,
    output reg                      m_axi_arlock,
    output reg  [3:0]               m_axi_arcache,
    output reg  [2:0]               m_axi_arprot,
    output reg  [3:0]               m_axi_arqos,
    output reg  [3:0]               m_axi_arregion,
    output reg  [ARUSER_WIDTH-1:0]  m_axi_aruser,
    output reg                      m_axi_arvalid,
    input  wire                     m_axi_arready,
    input  wire [ID_WIDTH-1:0]      m_axi_rid,
    input  wire [M_DATA_WIDTH-1:0]  m_axi_rdata,
    input  wire [1:0]               m_axi_rresp,
    input  wire                     m_axi_rlast,
    input  wire [RUSER_WIDTH-1:0]   m_axi_ruser,
    input  wire                     m_axi_rvalid,
    output reg                      m_axi_rready
);

    // Internal state variables
    localparam STATE_IDLE        = 3'b001;
    localparam STATE_DATA        = 3'b010;
    localparam STATE_DATA_READ   = 3'b011;
    localparam STATE_DATA_SPLIT  = 3'b100;

    reg [2:0] state, next_state;
    reg [ADDR_WIDTH-1:0] araddr_reg;
    reg [7:0] arlen_reg;
    reg [2:0] arsize_reg;
    reg [1:0] arburst_reg;
    reg [ID_WIDTH-1:0] arid_reg;
    reg [S_DATA_WIDTH-1:0] split_data;

    // State machine
    always @(posedge clk or posedge rst) begin
        if (rst) begin
            state <= STATE_IDLE;
        end else begin
            state <= next_state;
        end
    end

    always @* begin
        next_state = state;
        case (state)
            STATE_IDLE: begin
                if (s_axi_arvalid) begin
                    next_state = (EXPAND) ? STATE_DATA : (CONVERT_NARROW_BURST) ? STATE_DATA_SPLIT : STATE_DATA_READ;
                    araddr_reg = s_axi_araddr;
                    arlen_reg = s_axi_arlen;
                    arsize_reg = s_axi_arsize;
                    arburst_reg = s_axi_arburst;
                    arid_reg = s_axi_arid;
                end
            end
            STATE_DATA: begin
                if (m_axi_rvalid && s_axi_rready) begin
                    next_state = STATE_IDLE;
                end
            end
            STATE_DATA_READ: begin
                if (m_axi_rvalid && s_axi_rready) begin
                    next_state = STATE_IDLE;
                end
            end
            STATE_DATA_SPLIT: begin
                if (m_axi_rvalid && s_axi_rready) begin
                    split_data <= (split_data << S_DATA_WIDTH) | m_axi_rdata;
                    next_state = (s_axi_rlast) ? STATE_IDLE : STATE_DATA_SPLIT;
                end
            end
            default: begin
                next_state = STATE_IDLE;
            end
        endcase
    end

    // AXI protocol handling
    always @* begin
        s_axi_arready = (state == STATE_IDLE);
        s_axi_rvalid = (state == STATE_DATA || state == STATE_DATA_READ || state == STATE_DATA_SPLIT) && m_axi_rvalid;
        s_axi_rdata = (state == STATE_DATA_SPLIT) ? split_data : m_axi_rdata;
        s_axi_rresp = m_axi_rresp;
        s_axi_rlast = m_axi_rlast;
        s_axi_rid = (FORWARD_ID) ? m_axi_rid : arid_reg;

        m_axi_arid = arid_reg;
        m_axi_araddr = araddr_reg;
        m_axi_arlen = arlen_reg;
        m_axi_arsize = (EXPAND) ? arsize_reg + 1 : arsize_reg;
        m_axi_arburst = arburst_reg;
        m_axi_arlock = s_axi_arlock;
        m_axi_arcache = s_axi_arcache;
        m_axi_arprot = s_axi_arprot;
        m_axi_arqos = s_axi_arqos;
        m_axi_arregion = s_axi_arregion;
        m_axi_aruser = s_axi_aruser;
        m_axi_arvalid = (state == STATE_IDLE) && s_axi_arvalid;
        m_axi_rready = (s_axi_rready);
    end

endmodule