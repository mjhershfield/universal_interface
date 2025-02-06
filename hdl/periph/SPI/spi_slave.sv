//lycan is the slave peripheral, DUT is master

module spi_slave #(
    parameter WIDTH = 8
)(
    input logic clk,
    input logic rst,

    //SPI
    input logic CS_L,
    input logic SCLK,
    input logic MOSI,
    output logic MISO,

    //data control
    input logic [WIDTH-1:0] tx_data,
    output logic [WIDTH-1:0] rx_data,
    output logic rx_valid,
    output logic tx_busy    //not sure if needed
);

    // SPI States
    typedef enum logic [1:0] {
        S_IDLE,
        S_TRANSFER,
        S_DONE
    } spi_s_state_t;

    spi_s_state_t state_r, nxt_state;

    //data shift
    logic [WIDTH-1:0] shift_rx_r, nxt_shift_rx;
    logic [WIDTH-1:0] shift_tx_r, nxt_shift_tx;
    logic [3:0] bit_cnt_r, nxt_bit_cnt;

    always_ff @(posedge SCLK or posedge rst) begin
        if (rst) begin
            state_r <= S_IDLE;
            bit_cnt_r <= 4'b0;
            //MISO <= 1'b0;
            shift_rx_r <= 8'b0;
            shift_tx_r <= 8'b0;
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

        rx_valid = 1'b0;
        tx_busy = 1'b0;
        MISO = 1'b0;

        unique case (state_r)
            S_IDLE: begin
                rx_valid = 1'b0;
                tx_busy = 1'b0;
                nxt_bit_cnt = 3'b0;

                if (CS_L == 0) begin
                    nxt_shift_tx = tx_data;
                    tx_busy = 1'b1;
                    nxt_state = S_TRANSFER;
                end
            end

            S_TRANSFER: begin
                if (CS_L == 1) begin  //sudden disable failsafe
                    nxt_state = S_IDLE;
                end else if (bit_cnt_r < WIDTH) begin
                    MISO = shift_tx_r[WIDTH-1];   // Send MSB first
                    nxt_shift_tx = {shift_tx_r[WIDTH-2:0], 1'b0}; // Shift left
                    nxt_shift_rx = {shift_rx_r[WIDTH-2:0], MOSI}; // Read MOSI
                    nxt_bit_cnt = bit_cnt_r + 1;
                end else begin
                    nxt_state = S_DONE;
                end
            end

            S_DONE: begin
                rx_data = shift_rx_r;  // Store received data
                rx_valid = 1'b1;     // Signal data is ready
                tx_busy = 1'b0;     // Ready for new tx_data
                nxt_state = S_IDLE;
            end

            default: begin
            end

        endcase
    end

endmodule
