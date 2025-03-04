import uart_pkg::*;

module uart_rx #(
    parameter int RX_TX_CLK_RATIO = 8
) (
    input  logic             clk,
    input  logic             rst,
    input  logic             rx,
    output logic             rx_busy,
    output logic       [7:0] rx_data,
    input  logic             rx_full,        //unused for now
    output logic             rx_error,       //if the data had no errors
    output logic             rx_done,        //if we are outputting received data
    // Configuration data (for now, just 8N1)
    input  logic       [3:0] num_data_bits,
    input  stop_bits_t       stop_bits,
    input  parity_t          parity
);

  typedef enum logic [2:0] {
    S_WAIT_START,
    S_START,
    S_DATA,
    S_PARITY,
    S_STOP1,
    S_STOP2
  } fsm_state_t;

  fsm_state_t state_r, nxt_state;

  logic [7:0] rx_data_r, nxt_rx_data;  //data collected from rx line
  logic [2:0] data_count_r, nxt_data_count;
  parity_t parity_type_r, nxt_parity_type;
  stop_bits_t stop_bits_r, nxt_stop_bits;
  logic rx_error_r, nxt_rx_error;

  logic [$clog2(RX_TX_CLK_RATIO)-1:0] oversample_count_r, nxt_oversample_count;
  logic done_r, nxt_done;

  always_ff @(posedge clk or posedge rst) begin
    if (rst) begin
      state_r <= S_WAIT_START;
      rx_data_r <= '0;
      data_count_r <= '0;
      stop_bits_r <= STOP_BITS_1;
      rx_error_r <= '0;
      parity_type_r <= PARITY_NONE;
      oversample_count_r <= '0;
      done_r <= 1'b0;
    end else begin
      state_r <= nxt_state;
      rx_data_r <= nxt_rx_data;
      data_count_r <= nxt_data_count;
      stop_bits_r <= nxt_stop_bits;
      rx_error_r <= nxt_rx_error;
      parity_type_r <= nxt_parity_type;
      oversample_count_r <= nxt_oversample_count;
      done_r <= nxt_done;
    end
  end

  always_comb begin
    nxt_state = state_r;
    nxt_rx_data = rx_data_r;
    nxt_data_count = data_count_r;
    nxt_stop_bits = stop_bits_r;
    nxt_rx_error = rx_error_r;
    nxt_parity_type = parity_type_r;
    nxt_oversample_count = oversample_count_r;
    // Default values for combinational signals
    rx_busy = 1'b1;
    nxt_done = 1'b0;
    // nxt_rx_data = 8'b0;

    unique case (state_r)
      S_WAIT_START: begin
        rx_busy = 1'b0;
        nxt_rx_error = 1'b0;
        if (~rx) begin  //rx dropping low indicates start detect before data bits
          nxt_data_count  = num_data_bits - 1;
          nxt_rx_data     = 8'b0;  //reset data collection to 0
          nxt_state       = S_START;
          //store UART config settings
          nxt_stop_bits   = stop_bits;
          nxt_parity_type = parity;
          nxt_rx_error    = 1'b0;
        end
      end

      S_START: begin
        nxt_oversample_count = oversample_count_r + 1;
        if (oversample_count_r == '1) nxt_state = S_DATA;
      end

      //receives LSB first
      S_DATA: begin
        nxt_oversample_count = oversample_count_r + 1;
        if (oversample_count_r == RX_TX_CLK_RATIO / 2) begin
          nxt_rx_data = {rx, rx_data_r[7:1]};
        end

        if (oversample_count_r == '1) begin
          nxt_data_count = data_count_r - 1;
        end

        if (oversample_count_r == '1 && data_count_r == '0) begin
          if (parity_type_r != PARITY_NONE) nxt_state = S_PARITY;
          else begin
            nxt_state = S_STOP1;
            nxt_done  = 1'b1;
          end
        end
      end

      S_PARITY: begin
        nxt_oversample_count = oversample_count_r + 1;
        if (oversample_count_r == RX_TX_CLK_RATIO / 2) begin
          case (parity_type_r)
            PARITY_ODD:
            if (0 == ^{rx_data_r, rx}) begin
              nxt_rx_error = 1'b1;  //even number of 1s, error occured
            end

            PARITY_EVEN:
            if (1 == ^{rx_data_r, rx}) begin
              nxt_rx_error = 1'b1;  //odd number of 1s, error occured
              nxt_done = 1'b1;
            end


            default: begin
            end
          endcase
        end

        if (oversample_count_r == '1) begin
          nxt_state = S_STOP1;
          nxt_done  = 1'b1;
        end
      end

      S_STOP1: begin
        nxt_oversample_count = oversample_count_r + 1;
        if (oversample_count_r == '1 && stop_bits_r == STOP_BITS_2) nxt_state = S_STOP2;
        else if (oversample_count_r == '1) begin
          if (~rx) nxt_state = S_START;
          else nxt_state = S_WAIT_START;
        end
      end

      S_STOP2: begin
        nxt_oversample_count = oversample_count_r + 1;
        if (oversample_count_r == '1) begin
          if (~rx) nxt_state = S_START;
          else nxt_state = S_WAIT_START;
        end
      end

    endcase
  end

  assign rx_error = rx_error_r;
  assign rx_data  = rx_data_r;
  assign rx_done  = done_r;
endmodule
