module axi_register_rd #
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
    parameter AR_REG_TYPE = 1,  // AR channel register type: 0 to bypass, 1 for simple buffer, 2 for skid buffer
    parameter R_REG_TYPE = 2  // R channel register type: 0 to bypass, 1 for simple buffer, 2 for skid buffer
)
(
    // Ports
    input  wire                     clk,  // Clock signal
    input  wire                     rst,  // Reset signal

    /*
     * AXI slave interface
     */
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

    /*
     * AXI master interface
     */
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

    // Internal signals for AR channel
    reg [ID_WIDTH-1:0] ar_id_reg;
    reg [ADDR_WIDTH-1:0] ar_addr_reg;
    reg [7:0] ar_len_reg;
    reg [2:0] ar_size_reg;
    reg [1:0] ar_burst_reg;
    reg ar_lock_reg;
    reg [3:0] ar_cache_reg;
    reg [2:0] ar_prot_reg;
    reg [3:0] ar_qos_reg;
    reg [3:0] ar_region_reg;
    reg [ARUSER_WIDTH-1:0] ar_user_reg;
    reg ar_valid_reg;
    wire ar_ready_int;

    // Internal signals for R channel
    reg [ID_WIDTH-1:0] r_id_reg;
    reg [DATA_WIDTH-1:0] r_data_reg;
    reg [1:0] r_resp_reg;
    reg r_last_reg;
    reg [RUSER_WIDTH-1:0] r_user_reg;
    reg r_valid_reg;
    wire r_ready_int;

    // AR Channel (Address Read)
    generate
        if (AR_REG_TYPE == 2) begin : gen_ar_skid_buffer
            reg [ID_WIDTH-1:0] ar_id_skid;
            reg [ADDR_WIDTH-1:0] ar_addr_skid;
            reg [7:0] ar_len_skid;
            reg [2:0] ar_size_skid;
            reg [1:0] ar_burst_skid;
            reg ar_lock_skid;
            reg [3:0] ar_cache_skid;
            reg [2:0] ar_prot_skid;
            reg [3:0] ar_qos_skid;
            reg [3:0] ar_region_skid;
            reg [ARUSER_WIDTH-1:0] ar_user_skid;
            reg ar_valid_skid;

            always @(posedge clk) begin
                if (rst) begin
                    ar_valid_skid <= 1'b0;
                end else if (ar_ready_int && s_axi_arvalid) begin
                    ar_id_skid <= s_axi_arid;
                    ar_addr_skid <= s_axi_araddr;
                    ar_len_skid <= s_axi_arlen;
                    ar_size_skid <= s_axi_arsize;
                    ar_burst_skid <= s_axi_arburst;
                    ar_lock_skid <= s_axi_arlock;
                    ar_cache_skid <= s_axi_arcache;
                    ar_prot_skid <= s_axi_arprot;
                    ar_qos_skid <= s_axi_arqos;
                    ar_region_skid <= s_axi_arregion;
                    ar_user_skid <= s_axi_aruser;
                    ar_valid_skid <= s_axi_arvalid;
                end else if (ar_ready_int) begin
                    ar_valid_skid <= 1'b0;
                end
            end

            assign ar_ready_int = ar_valid_skid ? m_axi_arready : 1'b1;
            assign m_axi_arid = ar_id_skid;
            assign m_axi_araddr = ar_addr_skid;
            assign m_axi_arlen = ar_len_skid;
            assign m_axi_arsize = ar_size_skid;
            assign m_axi_arburst = ar_burst_skid;
            assign m_axi_arlock = ar_lock_skid;
            assign m_axi_arcache = ar_cache_skid;
            assign m_axi_arprot = ar_prot_skid;
            assign m_axi_arqos = ar_qos_skid;
            assign m_axi_arregion = ar_region_skid;
            assign m_axi_aruser = ar_user_skid;
            assign m_axi_arvalid = ar_valid_skid;

            assign s_axi_arready = ar_ready_int;
        end else if (AR_REG_TYPE == 1) begin : gen_ar_simple_buffer
            always @(posedge clk) begin
                if (rst) begin
                    ar_valid_reg <= 1'b0;
                end else if (ar_ready_int && s_axi_arvalid) begin
                    ar_id_reg <= s_axi_arid;
                    ar_addr_reg <= s_axi_araddr;
                    ar_len_reg <= s_axi_arlen;
                    ar_size_reg <= s_axi_arsize;
                    ar_burst_reg <= s_axi_arburst;
                    ar_lock_reg <= s_axi_arlock;
                    ar_cache_reg <= s_axi_arcache;
                    ar_prot_reg <= s_axi_arprot;
                    ar_qos_reg <= s_axi_arqos;
                    ar_region_reg <= s_axi_arregion;
                    ar_user_reg <= s_axi_aruser;
                    ar_valid_reg <= s_axi_arvalid;
                end else if (ar_ready_int) begin
                    ar_valid_reg <= 1'b0;
                end
            end

            assign ar_ready_int = ar_valid_reg ? m_axi_arready : 1'b1;
            assign m_axi_arid = ar_id_reg;
            assign m_axi_araddr = ar_addr_reg;
            assign m_axi_arlen = ar_len_reg;
            assign m_axi_arsize = ar_size_reg;
            assign m_axi_arburst = ar_burst_reg;
            assign m_axi_arlock = ar_lock_reg;
            assign m_axi_arcache = ar_cache_reg;
            assign m_axi_arprot = ar_prot_reg;
            assign m_axi_arqos = ar_qos_reg;
            assign m_axi_arregion = ar_region_reg;
            assign m_axi_aruser = ar_user_reg;
            assign m_axi_arvalid = ar_valid_reg;

            assign s_axi_arready = ar_ready_int;
        end else begin : gen_ar_bypass
            assign ar_ready_int = m_axi_arready;
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
            assign m_axi_arvalid = s_axi_arvalid;

            assign s_axi_arready = ar_ready_int;
        end
    endgenerate

    // R Channel (Read Data)
    generate
        if (R_REG_TYPE == 2) begin : gen_r_skid_buffer
            reg [ID_WIDTH-1:0] r_id_skid;
            reg [DATA_WIDTH-1:0] r_data_skid;
            reg [1:0] r_resp_skid;
            reg r_last_skid;
            reg [RUSER_WIDTH-1:0] r_user_skid;
            reg r_valid_skid;

            always @(posedge clk) begin
                if (rst) begin
                    r_valid_skid <= 1'b0;
                end else if (r_ready_int && m_axi_rvalid) begin
                    r_id_skid <= m_axi_rid;
                    r_data_skid <= m_axi_rdata;
                    r_resp_skid <= m_axi_rresp;
                    r_last_skid <= m_axi_rlast;
                    r_user_skid <= m_axi_ruser;
                    r_valid_skid <= m_axi_rvalid;
                end else if (r_ready_int) begin
                    r_valid_skid <= 1'b0;
                end
            end

            assign r_ready_int = r_valid_skid ? s_axi_rready : 1'b1;
            assign s_axi_rid = r_id_skid;
            assign s_axi_rdata = r_data_skid;
            assign s_axi_rresp = r_resp_skid;
            assign s_axi_rlast = r_last_skid;
            assign s_axi_ruser = r_user_skid;
            assign s_axi_rvalid = r_valid_skid;

            assign m_axi_rready = r_ready_int;
        end else if (R_REG_TYPE == 1) begin : gen_r_simple_buffer
            always @(posedge clk) begin
                if (rst) begin
                    r_valid_reg <= 1'b0;
                end else if (r_ready_int && m_axi_rvalid) begin
                    r_id_reg <= m_axi_rid;
                    r_data_reg <= m_axi_rdata;
                    r_resp_reg <= m_axi_rresp;
                    r_last_reg <= m_axi_rlast;
                    r_user_reg <= m_axi_ruser;
                    r_valid_reg <= m_axi_rvalid;
                end else if (r_ready_int) begin
                    r_valid_reg <= 1'b0;
                end
            end

            assign r_ready_int = r_valid_reg ? s_axi_rready : 1'b1;
            assign s_axi_rid = r_id_reg;
            assign s_axi_rdata = r_data_reg;
            assign s_axi_rresp = r_resp_reg;
            assign s_axi_rlast = r_last_reg;
            assign s_axi_ruser = r_user_reg;
            assign s_axi_rvalid = r_valid_reg;

            assign m_axi_rready = r_ready_int;
        end else begin : gen_r_bypass
            assign r_ready_int = s_axi_rready;
            assign s_axi_rid = m_axi_rid;
            assign s_axi_rdata = m_axi_rdata;
            assign s_axi_rresp = m_axi_rresp;
            assign s_axi_rlast = m_axi_rlast;
            assign s_axi_ruser = m_axi_ruser;
            assign s_axi_rvalid = m_axi_rvalid;

            assign m_axi_rready = r_ready_int;
        end
    endgenerate

endmodule