module axi_dma_desc_mux #
(
    // Parameters
    parameter PORTS = 2,  // Number of ports
    parameter AXI_ADDR_WIDTH = 16,  // AXI address width
    parameter AXIS_ID_ENABLE = 0,  // Propagate AXI stream tid signal
    parameter AXIS_ID_WIDTH = 8,  // AXI stream tid signal width
    parameter AXIS_DEST_ENABLE = 0,  // Propagate AXI stream tdest signal
    parameter AXIS_DEST_WIDTH = 8,  // AXI stream tdest signal width
    parameter AXIS_USER_ENABLE = 1,  // Propagate AXI stream tuser signal
    parameter AXIS_USER_WIDTH = 1,  // AXI stream tuser signal width
    parameter LEN_WIDTH = 20,  // Length field width
    parameter S_TAG_WIDTH = 8,  // Input tag field width
    parameter M_TAG_WIDTH = S_TAG_WIDTH+$clog2(PORTS),  // Output tag field width (towards DMA module)
                                                       // Additional bits required for response routing
    parameter ARB_TYPE_ROUND_ROBIN = 1,  // Select round robin arbitration
    parameter ARB_LSB_HIGH_PRIORITY = 1  // LSB priority selection
)
(
    // Ports
    input  wire                             clk,  // Clock signal
    input  wire                             rst,  // Reset signal

    // Descriptor output (to AXI DMA core)
    output reg [AXI_ADDR_WIDTH-1:0]         m_axis_desc_addr,
    output reg [LEN_WIDTH-1:0]              m_axis_desc_len,
    output reg [M_TAG_WIDTH-1:0]            m_axis_desc_tag,
    output reg [AXIS_ID_WIDTH-1:0]          m_axis_desc_id,
    output reg [AXIS_DEST_WIDTH-1:0]        m_axis_desc_dest,
    output reg [AXIS_USER_WIDTH-1:0]        m_axis_desc_user,
    output reg                              m_axis_desc_valid,
    input  wire                             m_axis_desc_ready,

    // Descriptor status input (from AXI DMA core)
    input  wire [LEN_WIDTH-1:0]             s_axis_desc_status_len,
    input  wire [M_TAG_WIDTH-1:0]           s_axis_desc_status_tag,
    input  wire [AXIS_ID_WIDTH-1:0]         s_axis_desc_status_id,
    input  wire [AXIS_DEST_WIDTH-1:0]       s_axis_desc_status_dest,
    input  wire [AXIS_USER_WIDTH-1:0]       s_axis_desc_status_user,
    input  wire [3:0]                       s_axis_desc_status_error,
    input  wire                                s_axis_desc_status_valid,

    // Descriptor input
    input  wire [PORTS*AXI_ADDR_WIDTH-1:0]  s_axis_desc_addr,
    input  wire [PORTS*LEN_WIDTH-1:0]       s_axis_desc_len,
    input  wire [PORTS*S_TAG_WIDTH-1:0]     s_axis_desc_tag,
    input  wire [PORTS*AXIS_ID_WIDTH-1:0]   s_axis_desc_id,
    input  wire [PORTS*AXIS_DEST_WIDTH-1:0] s_axis_desc_dest,
    input  wire [PORTS*AXIS_USER_WIDTH-1:0] s_axis_desc_user,
    input  wire [PORTS-1:0]                 s_axis_desc_valid,
    output reg [PORTS-1:0]                  s_axis_desc_ready,

    // Descriptor status output
    output reg [PORTS*LEN_WIDTH-1:0]        m_axis_desc_status_len,
    output reg [PORTS*S_TAG_WIDTH-1:0]      m_axis_desc_status_tag,
    output reg [PORTS*AXIS_ID_WIDTH-1:0]    m_axis_desc_status_id,
    output reg [PORTS*AXIS_DEST_WIDTH-1:0]  m_axis_desc_status_dest,
    output reg [PORTS*AXIS_USER_WIDTH-1:0]  m_axis_desc_status_user,
    output reg [PORTS*4-1:0]                m_axis_desc_status_error,
    output reg [PORTS-1:0]                  m_axis_desc_status_valid
);

// Internal variables
reg [$clog2(PORTS)-1:0] arb_counter;
reg [$clog2(PORTS)-1:0] selected_port;

always @(posedge clk or posedge rst) begin
    if (rst) begin
        arb_counter <= 0;
        m_axis_desc_valid <= 0;
        m_axis_desc_addr <= 0;
        m_axis_desc_len <= 0;
        m_axis_desc_tag <= 0;
        m_axis_desc_id <= 0;
        m_axis_desc_dest <= 0;
        m_axis_desc_user <= 0;
        s_axis_desc_ready <= 0;
        m_axis_desc_status_len <= 0;
        m_axis_desc_status_tag <= 0;
        m_axis_desc_status_id <= 0;
        m_axis_desc_status_dest <= 0;
        m_axis_desc_status_user <= 0;
        m_axis_desc_status_error <= 0;
        m_axis_desc_status_valid <= 0;
    end else begin
        // Round-robin arbitration logic
        if (m_axis_desc_ready && m_axis_desc_valid) begin
            if (arb_counter == PORTS-1) begin
                arb_counter <= 0;
            end else begin
                arb_counter <= arb_counter + 1;
            end
        end

        selected_port <= arb_counter;

        // Set m_axis signals based on selected port
        m_axis_desc_addr <= s_axis_desc_addr[(selected_port+1)*AXI_ADDR_WIDTH-1 -: AXI_ADDR_WIDTH];
        m_axis_desc_len <= s_axis_desc_len[(selected_port+1)*LEN_WIDTH-1 -: LEN_WIDTH];
        m_axis_desc_tag <= {selected_port, s_axis_desc_tag[(selected_port+1)*S_TAG_WIDTH-1 -: S_TAG_WIDTH]};
        m_axis_desc_id <= s_axis_desc_id[(selected_port+1)*AXIS_ID_WIDTH-1 -: AXIS_ID_WIDTH];
        m_axis_desc_dest <= s_axis_desc_dest[(selected_port+1)*AXIS_DEST_WIDTH-1 -: AXIS_DEST_WIDTH];
        m_axis_desc_user <= s_axis_desc_user[(selected_port+1)*AXIS_USER_WIDTH-1 -: AXIS_USER_WIDTH];
        m_axis_desc_valid <= s_axis_desc_valid[selected_port];
        
        s_axis_desc_ready <= 0;
        s_axis_desc_ready[selected_port] <= m_axis_desc_ready;

        // Handle sync of status back to input ports based on tag
        if (s_axis_desc_status_valid) begin
            // extract port from tag
            m_axis_desc_status_len[(s_axis_desc_status_tag[$clog2(PORTS)-1:0]+1)*LEN_WIDTH-1 -: LEN_WIDTH] <= s_axis_desc_status_len;
            m_axis_desc_status_tag[(s_axis_desc_status_tag[$clog2(PORTS)-1:0]+1)*S_TAG_WIDTH-1 -: S_TAG_WIDTH] <= s_axis_desc_status_tag[M_TAG_WIDTH-1:$clog2(PORTS)];
            m_axis_desc_status_id[(s_axis_desc_status_tag[$clog2(PORTS)-1:0]+1)*AXIS_ID_WIDTH-1 -: AXIS_ID_WIDTH] <= s_axis_desc_status_id;
            m_axis_desc_status_dest[(s_axis_desc_status_tag[$clog2(PORTS)-1:0]+1)*AXIS_DEST_WIDTH-1 -: AXIS_DEST_WIDTH] <= s_axis_desc_status_dest;
            m_axis_desc_status_user[(s_axis_desc_status_tag[$clog2(PORTS)-1:0]+1)*AXIS_USER_WIDTH-1 -: AXIS_USER_WIDTH] <= s_axis_desc_status_user;
            m_axis_desc_status_error[(s_axis_desc_status_tag[$clog2(PORTS)-1:0]+1)*4-1 -: 4] <= s_axis_desc_status_error;
            m_axis_desc_status_valid[s_axis_desc_status_tag[$clog2(PORTS)-1:0]] <= s_axis_desc_status_valid;
        end
    end
end

endmodule