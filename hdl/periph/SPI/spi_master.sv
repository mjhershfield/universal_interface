//lycan is the master peripheral

module spi_master #(
    parameter WIDTH = 24
)(
    input logic clk,
    input logic rst,
    input logic [7:0] tx_data,
    input logic tx_empty,

    //SPI signals
    output logic CS_L,
    output logic SCLK,
    output logic MOSI,
    input logic MISO,

    //config signals
    input logic [WIDTH-1:0] sclk_div_count,

    //data control for data received and converted from slave
    output logic [7:0] rx_data,
    output logic rx_valid
);

//SPI states
typedef enum logic [1:0] {
    S_IDLE,
    S_START,
    S_TRANSFER,
    S_STOP
} spi_m_state_t;

spi_m_state_t state_r, nxt_state;

//data shift
logic [7:0] shift_tx_r, nxt_shift_tx;
logic [7:0] shift_rx_r, nxt_shift_rx;
logic [3:0] bit_cnt_r, nxt_bit_cnt;

logic clk_pulse;    //clock divider for SCLK


clk_div #(
    .width(WIDTH)
)clk_div_spi(
    .clk(clk),
    .rst(rst),
    .div_clk(clk_pulse),
    .max_count(sclk_div_count)
);

assign SCLK = clk_pulse;

always_ff @(posedge clk_pulse or posedge rst) begin
    if (rst) begin
        state_r <= S_IDLE;
        shift_tx_r <= 8'b0;
        shift_rx_r <= 8'b0;
        bit_cnt_r <= 4'b0;
    end else begin
        state_r <= nxt_state;
        bit_cnt_r <= nxt_bit_cnt;
        shift_rx_r <= nxt_shift_rx;
        shift_tx_r <= nxt_shift_tx;
    end
end

always_comb begin

    nxt_state = state_r;
    nxt_bit_cnt = bit_cnt_r;
    nxt_shift_rx = shift_rx_r;
    nxt_shift_tx = shift_tx_r;

    CS_L = 1'b1;
    MOSI = 1'b0;
    rx_data = 8'b0;
    rx_valid = 1'b0;

    unique case (state_r)
        S_IDLE: begin
            CS_L = 1'b1;
            rx_valid = 1'b0;
            if (tx_empty == 0) begin
                nxt_shift_tx = tx_data;
                nxt_bit_cnt = 4'b0;
                nxt_state = S_START;
            end
        end

        S_START: begin
            CS_L = 1'b0;
            nxt_state = S_TRANSFER;
        end

        //assume SPI norm of sending MSB first
        //assume SPI sends 8 bits at a time
        S_TRANSFER: begin
            if (bit_cnt_r < 8) begin
                CS_L = 1'b0;
                MOSI = shift_tx_r[7]; //send MSB and shift
                nxt_shift_tx = {shift_tx_r[6:0], 1'b0};
                nxt_shift_rx = {shift_rx_r[6:0], MISO}; //read MISO
                nxt_bit_cnt = bit_cnt_r + 1;
            end else begin
                nxt_state = S_STOP;
                CS_L = 1'b0; //keep enabled here to save an extra state (same as S_END)
            end
        end

        S_STOP: begin
            CS_L = 1'b1;
            rx_data = shift_rx_r;
            rx_valid = 1'b1;
            nxt_state = S_IDLE;
        end

        default: begin
        end

    endcase
end

endmodule