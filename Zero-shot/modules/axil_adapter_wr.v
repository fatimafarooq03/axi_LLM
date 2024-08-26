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
    output reg                      s_axil_awready,
    input  wire [S_DATA_WIDTH-1:0]  s_axil_wdata,
    input  wire [S_STRB_WIDTH-1:0]  s_axil_wstrb,
    input  wire                     s_axil_wvalid,
    output reg                      s_axil_wready,
    output reg  [1:0]               s_axil_bresp,
    output reg                      s_axil_bvalid,
    input  wire                     s_axil_bready,

    /*
     * AXI lite master interface
     */
    output reg  [ADDR_WIDTH-1:0]    m_axil_awaddr,
    output reg  [2:0]               m_axil_awprot,
    output reg                      m_axil_awvalid,
    input  wire                     m_axil_awready,
    output reg  [M_DATA_WIDTH-1:0]  m_axil_wdata,
    output reg  [M_STRB_WIDTH-1:0]  m_axil_wstrb,
    output reg                      m_axil_wvalid,
    input  wire                     m_axil_wready,
    input  wire [1:0]               m_axil_bresp,
    input  wire                     m_axil_bvalid,
    output reg                      m_axil_bready
);

localparam STATE_IDLE = 2'd0;
localparam STATE_DATA = 2'd1;
localparam STATE_RESP = 2'd2;

reg [1:0] state_reg = STATE_IDLE, state_next;

reg [ADDR_WIDTH-1:0] awaddr_reg, awaddr_next;
reg [2:0] awprot_reg, awprot_next;
reg [S_DATA_WIDTH-1:0] wdata_reg, wdata_next;
reg [S_STRB_WIDTH-1:0] wstrb_reg, wstrb_next;

wire expand = M_DATA_WIDTH > S_DATA_WIDTH;

always @* begin
    state_next = state_reg;
    s_axil_awready = 1'b0;
    s_axil_wready = 1'b0;
    s_axil_bresp = 2'b00;
    s_axil_bvalid = 1'b0;
    m_axil_awaddr = awaddr_reg;
    m_axil_awprot = awprot_reg;
    m_axil_awvalid = 1'b0;
    m_axil_wdata = wdata_reg;
    m_axil_wstrb = wstrb_reg;
    m_axil_wvalid = 1'b0;
    m_axil_bready = 1'b0;

    case (state_reg)
        STATE_IDLE: begin
            s_axil_awready = 1'b1;
            if (s_axil_awvalid) begin
                awaddr_next = s_axil_awaddr;
                awprot_next = s_axil_awprot;
                state_next = STATE_DATA;
            end
        end
        STATE_DATA: begin
            s_axil_wready = 1'b1;
            if (s_axil_wvalid) begin
                wdata_next = s_axil_wdata;
                wstrb_next = s_axil_wstrb;
                state_next = STATE_RESP;
            end
        end
        STATE_RESP: begin
            m_axil_awvalid = 1'b1;
            if (m_axil_awready) begin
                m_axil_wvalid = 1'b1;
                if (expand) begin
                    m_axil_wdata = {{(M_DATA_WIDTH-S_DATA_WIDTH){1'b0}}, wdata_reg};
                    m_axil_wstrb = {{(M_STRB_WIDTH-S_STRB_WIDTH){1'b0}}, wstrb_reg};
                end else begin
                    m_axil_wdata = wdata_reg[S_DATA_WIDTH-1:0];
                    m_axil_wstrb = wstrb_reg[S_STRB_WIDTH-1:0];
                end
                if (m_axil_wready) begin
                    m_axil_bready = 1'b1;
                    if (m_axil_bvalid && m_axil_bready) begin
                        s_axil_bresp = m_axil_bresp;
                        s_axil_bvalid = 1'b1;
                        if (s_axil_bready && s_axil_bvalid) begin
                            state_next = STATE_IDLE;
                        end
                    end
                end
            end
        end
    endcase
end

always @(posedge clk or posedge rst) begin
    if (rst) begin
        state_reg <= STATE_IDLE;
        awaddr_reg <= {ADDR_WIDTH{1'b0}};
        awprot_reg <= 3'b000;
        wdata_reg <= {S_DATA_WIDTH{1'b0}};
        wstrb_reg <= {S_STRB_WIDTH{1'b0}};
    end else begin
        state_reg <= state_next;
        awaddr_reg <= awaddr_next;
        awprot_reg <= awprot_next;
        wdata_reg <= wdata_next;
        wstrb_reg <= wstrb_next;
    end
end

endmodule