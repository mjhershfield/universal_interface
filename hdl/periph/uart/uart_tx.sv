import uart_pkg::*;

module uart_tx (
    input  logic             clk,
    input  logic             rst,
    output logic             tx,
    output logic             tx_busy,
    input  logic       [7:0] tx_data,
    input  logic             tx_empty,
    output logic             tx_rden,
    // Configuration data (for now, just 8N1)
    input  logic [3:0] num_data_bits,
    input  stop_bits_t       stop_bits,
    input  parity_t          parity
);

  typedef enum logic [2:0] {
    S_IDLE,
    S_START,
    S_DATA,
    S_PARITY,
    S_STOP1,
    S_STOP2
  } fsm_state_t;

  fsm_state_t state_r, nxt_state;

  logic [7:0] tx_data_r, nxt_tx_data;
  logic [2:0] data_count_r, nxt_data_count;
  logic parity_bit_r, nxt_parity;
  logic parity_type_r, nxt_parity_type;
  stop_bits_t stop_bits_r, nxt_stop_bits;

  always_ff @(posedge clk or posedge rst) begin
    if (rst) begin
      state_r <= S_IDLE;
      tx_data_r <= '0;
      data_count_r   <= '0;
      parity_bit_r <= 1'b0;
      stop_bits_r <= STOP_BITS_1;
      parity_type_r <= PARITY_NONE;
    end else begin
      state_r <= nxt_state;
      tx_data_r <= nxt_tx_data;
      data_count_r   <= nxt_data_count;
      parity_bit_r <= nxt_parity;
      stop_bits_r <= nxt_stop_bits;
      parity_type_r <= nxt_parity_type;
    end
  end

  always_comb begin
    nxt_state = state_r;
    nxt_tx_data = tx_data_r;
    nxt_data_count = data_count_r;
    nxt_parity = parity_bit_r;
    nxt_stop_bits = stop_bits_r;
    nxt_parity_type = parity_type_r;
    // Default values for combinational signals
    tx_busy = 1'b1;
    tx = 1'b1;
    tx_rden = 1'b0;

    unique case (state_r)
      S_IDLE: begin
        tx_busy = 1'b0;
        if (~tx_empty)
          nxt_state = S_START;
      end

      S_START: begin
        nxt_data_count = num_data_bits - 1;
        tx = 1'b0;
        // Reading TX data into local register
        tx_rden = 1'b1;
        nxt_tx_data = tx_data;
        nxt_stop_bits = stop_bits;
        nxt_parity_type = parity;
        case (parity_type_r)
          PARITY_ODD: begin
            nxt_parity = ~^tx_data;
          end

          PARITY_EVEN: begin
            nxt_parity = ^tx_data;
          end

          default: begin
            nxt_parity = 1'b0;
          end
        endcase
        nxt_state = S_DATA;
      end

      S_DATA: begin
        tx = tx_data_r[0];
        nxt_tx_data = tx_data_r >> 1;
        if (data_count_r == '0) begin
          if (parity != PARITY_NONE)  nxt_state = S_PARITY;
          else nxt_state = S_STOP1;
        end
        nxt_data_count = data_count_r - 1;
      end

      S_PARITY: begin
        tx = parity_bit_r;
        nxt_state = S_STOP1;
      end

      S_STOP1: begin
        tx = 1'b1;
        if (stop_bits_r == STOP_BITS_2) nxt_state = S_STOP2;
        else begin
          if (~tx_empty) nxt_state = S_START;
          else nxt_state = S_IDLE;
        end
      end

      S_STOP2: begin
        tx = 1'b1;
        if (~tx_empty) nxt_state = S_START;
        else nxt_state = S_IDLE;
      end

    endcase
  end

endmodule
