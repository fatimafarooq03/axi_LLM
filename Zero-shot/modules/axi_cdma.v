module axi_cdma #
(
    parameter AXI_DATA_WIDTH = 32,  
    parameter AXI_ADDR_WIDTH = 16,  
    parameter AXI_STRB_WIDTH = (AXI_DATA_WIDTH/8),  
    parameter AXI_ID_WIDTH = 8,  
    parameter AXI_MAX_BURST_LEN = 16,  
    parameter LEN_WIDTH = 20,  
    parameter TAG_WIDTH = 8,  
    parameter ENABLE_UNALIGNED = 0 
)
(
    input  wire                       clk,  
    input  wire                       rst,  

    input  wire [AXI_ADDR_WIDTH-1:0]  s_axis_desc_read_addr,
    input  wire [AXI_ADDR_WIDTH-1:0]  s_axis_desc_write_addr,
    input  wire [LEN_WIDTH-1:0]       s_axis_desc_len,
    input  wire [TAG_WIDTH-1:0]       s_axis_desc_tag,
    input  wire                       s_axis_desc_valid,
    output reg                        s_axis_desc_ready,

    output reg [TAG_WIDTH-1:0]        m_axis_desc_status_tag,
    output reg [3:0]                 m_axis_desc_status_error,
    output reg                       m_axis_desc_status_valid,

    output reg [AXI_ID_WIDTH-1:0]    m_axi_awid,
    output reg [AXI_ADDR_WIDTH-1:0]  m_axi_awaddr,
    output reg [7:0]                 m_axi_awlen,
    output reg [2:0]                 m_axi_awsize,
    output reg [1:0]                 m_axi_awburst,
    output reg                       m_axi_awlock,
    output reg [3:0]                 m_axi_awcache,
    output reg [2:0]                 m_axi_awprot,
    output reg                       m_axi_awvalid,
    input  wire                       m_axi_awready,
    output reg [AXI_DATA_WIDTH-1:0]  m_axi_wdata,
    output reg [AXI_STRB_WIDTH-1:0]  m_axi_wstrb,
    output reg                       m_axi_wlast,
    output reg                       m_axi_wvalid,
    input  wire                       m_axi_wready,
    input  wire [AXI_ID_WIDTH-1:0]    m_axi_bid,
    input  wire [1:0]                 m_axi_bresp,
    input  wire                       m_axi_bvalid,
    output reg                       m_axi_bready,

    output reg [AXI_ID_WIDTH-1:0]    m_axi_arid,
    output reg [AXI_ADDR_WIDTH-1:0]  m_axi_araddr,
    output reg [7:0]                 m_axi_arlen,
    output reg [2:0]                 m_axi_arsize,
    output reg [1:0]                 m_axi_arburst,
    output reg                       m_axi_arlock,
    output reg [3:0]                 m_axi_arcache,
    output reg [2:0]                 m_axi_arprot,
    output reg                       m_axi_arvalid,
    input  wire                       m_axi_arready,
    input  wire [AXI_ID_WIDTH-1:0]    m_axi_rid,
    input  wire [AXI_DATA_WIDTH-1:0]  m_axi_rdata,
    input  wire [1:0]                 m_axi_rresp,
    input  wire                       m_axi_rlast,
    input  wire                       m_axi_rvalid,
    output reg                       m_axi_rready,

    input  wire                       enable  
);

    // State machine states
    localparam READ_STATE_IDLE = 0, READ_STATE_START = 1, READ_STATE_DATA = 2;
    localparam WRITE_STATE_IDLE = 0, WRITE_STATE_ADDR = 1, WRITE_STATE_DATA = 2, WRITE_STATE_RESP = 3;
    
    reg [1:0] read_state, write_state;

    reg [AXI_ADDR_WIDTH-1:0] read_addr, write_addr;
    reg [LEN_WIDTH-1:0] transfer_len;
    reg [TAG_WIDTH-1:0] current_tag;
    reg [AXI_DATA_WIDTH-1:0] data_buffer;
    reg fifo_empty, fifo_full; // Placeholder for FIFO status signals

    always @(posedge clk) begin
        if (rst) begin
            read_state <= READ_STATE_IDLE;
            write_state <= WRITE_STATE_IDLE;
            s_axis_desc_ready <= 1'b0;
            m_axi_awvalid <= 1'b0;
            m_axi_wvalid <= 1'b0;
            m_axi_bready <= 1'b0;
            m_axi_arvalid <= 1'b0;
            m_axi_rready <= 1'b0;
            m_axis_desc_status_valid <= 1'b0;
        end 
        else if (enable) begin
            case (read_state)
                READ_STATE_IDLE: begin
                    s_axis_desc_ready <= 1'b1;
                    if (s_axis_desc_valid) begin
                        // Capture the descriptor
                        read_addr <= s_axis_desc_read_addr;
                        write_addr <= s_axis_desc_write_addr;
                        transfer_len <= s_axis_desc_len;
                        current_tag <= s_axis_desc_tag;
                        read_state <= READ_STATE_START;
                        s_axis_desc_ready <= 1'b0;
                    end
                end
                READ_STATE_START: begin
                    // Setup initial AXI read
                    m_axi_araddr <= read_addr;
                    m_axi_arlen <= (transfer_len > AXI_MAX_BURST_LEN) ? AXI_MAX_BURST_LEN - 1 : transfer_len - 1;
                    m_axi_arsize <= $clog2(AXI_DATA_WIDTH/8);
                    m_axi_arburst <= 2'b01; // INCR burst
                    m_axi_arvalid <= 1'b1;
                    read_state <= READ_STATE_DATA;
                end
                READ_STATE_DATA: begin
                    if (m_axi_arready) begin
                        m_axi_arvalid <= 1'b0;
                    end
                    if (m_axi_rvalid) begin
                        data_buffer <= m_axi_rdata;
                        if (m_axi_rlast) begin
                            read_addr <= read_addr + AXI_MAX_BURST_LEN * (AXI_DATA_WIDTH/8);
                            transfer_len <= transfer_len - AXI_MAX_BURST_LEN;
                            if (transfer_len == 0) begin
                                read_state <= READ_STATE_IDLE;
                            end else begin
                                read_state <= READ_STATE_START;
                            end
                            m_axi_rready <= 1'b0;
                        end
                        else begin
                            m_axi_rready <= 1'b1;
                        end
                        write_state <= WRITE_STATE_ADDR;
                    end
                end
            endcase

            case (write_state)
                WRITE_STATE_IDLE: begin
                    // Nothing to do
                end
                WRITE_STATE_ADDR: begin
                    if (!fifo_empty) begin
                        m_axi_awaddr <= write_addr;
                        m_axi_awlen <= (transfer_len > AXI_MAX_BURST_LEN) ? AXI_MAX_BURST_LEN - 1 : transfer_len - 1;
                        m_axi_awsize <= $clog2(AXI_DATA_WIDTH/8);
                        m_axi_awburst <= 2'b01; // INCR burst
                        m_axi_awvalid <= 1'b1;
                        write_state <= WRITE_STATE_DATA;
                    end
                end
                WRITE_STATE_DATA: begin
                    if (m_axi_awready) begin
                        m_axi_awvalid <= 1'b0;
                    end
                    if (!fifo_empty && m_axi_wready) begin
                        m_axi_wdata <= data_buffer;
                        m_axi_wstrb <= {AXI_STRB_WIDTH{1'b1}};
                        m_axi_wlast <= 1'b1;
                        m_axi_wvalid <= 1'b1;
                        write_state <= WRITE_STATE_RESP;
                    end
                end
                WRITE_STATE_RESP: begin
                    if (m_axi_bvalid) begin
                        m_axi_bready <= 1'b1;
                        write_addr <= write_addr + AXI_MAX_BURST_LEN * (AXI_DATA_WIDTH/8);
                        if (m_axi_bresp != 2'b00) begin
                            m_axis_desc_status_error <= 4'b1; // Error in response
                        end
                        if (transfer_len == 0) begin
                            m_axis_desc_status_valid <= 1'b1;
                            m_axis_desc_status_tag <= current_tag;
                            write_state <= WRITE_STATE_IDLE;
                        end
                        else begin
                            write_state <= WRITE_STATE_ADDR;
                        end
                    end
                end
            endcase
        end
    end
endmodule