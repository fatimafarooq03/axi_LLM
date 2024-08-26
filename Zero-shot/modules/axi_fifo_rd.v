module axi_fifo_rd #
(
    // Parameters
    parameter DATA_WIDTH = 32,  // Width of data bus in bits
    parameter ADDR_WIDTH = 32,  // Width of address bus in bits
    parameter STRB_WIDTH = (DATA_WIDTH/8),  // Width of wstrb (width of data bus in words)
    parameter ID_WIDTH = 8,  // Width of ID signal
    parameter ARUSER_ENABLE = 0,  // Propagate aruser signal
    parameter ARUSER_WIDTH = 1,  // Width of aruser signal
    parameter RUSER_ENABLE = 0,  // Propagate ruser signal
    parameter RUSER_WIDTH = 1,  // Width of ruser signal
    parameter FIFO_DEPTH = 32,  // Read data FIFO depth (cycles)
    parameter FIFO_DELAY = 0  // Hold read address until space available in FIFO for data, if possible
)
(
    // Ports
    input  wire                     clk,  // Clock signal
    input  wire                     rst,  // Reset signal

    // AXI slave interface
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
    output wire                     s_axi_arready,
    output wire [ID_WIDTH-1:0]      s_axi_rid,
    output wire [DATA_WIDTH-1:0]    s_axi_rdata,
    output wire [1:0]               s_axi_rresp,
    output wire                     s_axi_rlast,
    output wire [RUSER_WIDTH-1:0]   s_axi_ruser,
    output wire                     s_axi_rvalid,
    input  wire                     s_axi_rready,

    // AXI master interface
    output wire [ID_WIDTH-1:0]      m_axi_arid,
    output wire [ADDR_WIDTH-1:0]    m_axi_araddr,
    output wire [7:0]               m_axi_arlen,
    output wire [2:0]               m_axi_arsize,
    output wire [1:0]               m_axi_arburst,
    output wire                     m_axi_arlock,
    output wire [3:0]               m_axi_arcache,
    output wire [2:0]               m_axi_arprot,
    output wire [3:0]               m_axi_arqos,
    output wire [3:0]               m_axi_arregion,
    output wire [ARUSER_WIDTH-1:0]  m_axi_aruser,
    output wire                     m_axi_arvalid,
    input  wire                     m_axi_arready,
    input  wire [ID_WIDTH-1:0]      m_axi_rid,
    input  wire [DATA_WIDTH-1:0]    m_axi_rdata,
    input  wire [1:0]               m_axi_rresp,
    input  wire                     m_axi_rlast,
    input  wire [RUSER_WIDTH-1:0]   m_axi_ruser,
    input  wire                     m_axi_rvalid,
    output wire                     m_axi_rready
);

// Internal signals for FIFO
reg [DATA_WIDTH-1:0] fifo_data [0:FIFO_DEPTH-1];
reg [ID_WIDTH-1:0]   fifo_id [0:FIFO_DEPTH-1];
reg [1:0]            fifo_resp [0:FIFO_DEPTH-1];
reg                  fifo_last [0:FIFO_DEPTH-1];
reg [RUSER_WIDTH-1:0] fifo_user [0:FIFO_DEPTH-1];
reg [FIFO_DEPTH:0]   wr_ptr, rd_ptr;
wire fifo_full, fifo_empty;
reg ar_ready;
reg [2:0] fsm_state;

// Write control logic
always @(posedge clk or posedge rst) begin
    if (rst) begin
        wr_ptr <= 0;
    end else if (m_axi_rvalid && m_axi_rready) begin
        if (!fifo_full) begin
            fifo_data[wr_ptr[FIFO_DEPTH-1:0]] <= m_axi_rdata;
            fifo_id[wr_ptr[FIFO_DEPTH-1:0]] <= m_axi_rid;
            fifo_resp[wr_ptr[FIFO_DEPTH-1:0]] <= m_axi_rresp;
            fifo_last[wr_ptr[FIFO_DEPTH-1:0]] <= m_axi_rlast;
            if (RUSER_ENABLE) fifo_user[wr_ptr[FIFO_DEPTH-1:0]] <= m_axi_ruser;
            wr_ptr <= wr_ptr + 1;
        end
    end
end

// Read control logic
always @(posedge clk or posedge rst) begin
    if (rst) begin
        rd_ptr <= 0;
    end else if (s_axi_rvalid && s_axi_rready) begin
        if (!fifo_empty) begin
            rd_ptr <= rd_ptr + 1;
        end
    end
end

// FIFO status
assign fifo_full = (wr_ptr - rd_ptr) == FIFO_DEPTH;
assign fifo_empty = (wr_ptr == rd_ptr);

// Output register logic
assign s_axi_rid = fifo_id[rd_ptr[FIFO_DEPTH-1:0]];
assign s_axi_rdata = fifo_data[rd_ptr[FIFO_DEPTH-1:0]];
assign s_axi_rresp = fifo_resp[rd_ptr[FIFO_DEPTH-1:0]];
assign s_axi_rlast = fifo_last[rd_ptr[FIFO_DEPTH-1:0]];
assign s_axi_ruser = fifo_user[rd_ptr[FIFO_DEPTH-1:0]];

assign s_axi_rvalid = !fifo_empty;
assign m_axi_rready = !fifo_full;

generate
    if (FIFO_DELAY) begin
        always @(posedge clk or posedge rst) begin
            if (rst) begin
                fsm_state <= 0;
                ar_ready <= 0;
            end else begin
                case (fsm_state)
                    0: begin
                        if (s_axi_arvalid && ((wr_ptr - rd_ptr) <= (FIFO_DEPTH - s_axi_arlen))) begin
                            fsm_state <= 1;
                            ar_ready <= 1;
                        end else begin
                            ar_ready <= 0;
                        end
                    end
                    1: begin
                        if (m_axi_arready) begin
                            fsm_state <= 0;
                            ar_ready <= 0;
                        end
                    end
                endcase
            end
        end
        
        assign s_axi_arready = ar_ready;
        assign m_axi_arvalid = ar_ready;
    end else begin
        assign s_axi_arready = m_axi_arready;
        assign m_axi_arvalid = s_axi_arvalid;
    end
endgenerate

assign m_axi_arid = s_axi_arid;
assign m_axi_araddr = s_axi_araddr;
assign m_axi_arlen = s_axi_arlen;
assign m_axi_arsize = s_axi_arsize;
assign m_axi_arburst = s_axi_arburst;
assign m_axi_arlock = s_axi_arlock;
assign m_axi_arcache = s_axi_arcache;
assign m_axi_arprot = s_axi_arprot;
assign m_axi_arqos = s_axi_arqos;
assign m_axi_arregion = s_axi_arregion;
assign m_axi_aruser = s_axi_aruser;

endmodule