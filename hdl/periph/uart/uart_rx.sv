import uart_pkg::*;

module uart_rx (
    input  logic             clk,
    input  logic             rst,
    input logic             rx,
    output logic             rx_busy,
    output  logic       [7:0] rx_data,
    input  logic             rx_full,     //unused for now
    output logic             rx_error,    //if the data had no errors
    output logic             rx_done,     //if we are outputting received data
    // Configuration data (for now, just 8N1)
    input  logic [3:0] num_data_bits,
    input  stop_bits_t       stop_bits,
    input  parity_t          parity,

    //to fix out of phase rx and tx clocks
    input logic [3:0] rx_tx_clk_ratio
);


  //then sample every rx_tx_clk_ratio cycles
  typedef enum logic [1:0] {
    S_WAIT,
    S_OFFSET,
    S_REPEAT
  } trig_fsm_state_t;

  trig_fsm_state_t st_r;
  logic trigger_sample_r;
  logic first_edge_r;
  logic [3:0] trigger_cnt_r;


  always @(posedge clk or posedge rst) begin
    if (rst) begin
      st_r <= S_WAIT;
      first_edge_r <= '0;
      trigger_sample_r <= '0;
      trigger_cnt_r <= '0;
    end else begin

      trigger_sample_r <= '0;

      //detect first falling edge of rx line
      if (~rx && first_edge_r == 0) begin
        first_edge_r = '1;
      end
      

      case (st_r)
        S_WAIT: begin
          if (first_edge_r == 1) begin
            st_r <= S_OFFSET;
            trigger_cnt_r <= 0;
          end
        end

        //after rx falls wait until rx_tx_clk_ratio / 2 cycles for first sample
        S_OFFSET: begin
          if (trigger_cnt_r == (rx_tx_clk_ratio /2) - 1) begin
            st_r <= S_REPEAT;
            trigger_sample_r <= '1;
            trigger_cnt_r <= '0;
          end else begin
            trigger_cnt_r <= trigger_cnt_r + 1;
          end
        end

        //keep sampling at the offset created
        S_REPEAT: begin
          if (trigger_cnt_r == rx_tx_clk_ratio - 1) begin
            trigger_cnt_r <= '0;
            trigger_sample_r <= '1;
          end else begin
            trigger_cnt_r <= trigger_cnt_r + 1;
          end
        end

      endcase

    end
  end

  typedef enum logic [2:0] {
    S_WAIT_START,
    S_DATA,
    S_PARITY,
    S_STOP1,
    S_STOP2
  } fsm_state_t;

  fsm_state_t state_r, nxt_state;

  logic [7:0] rx_data_r, nxt_rx_data;     //data collected from rx line
  logic [2:0] data_count_r, nxt_data_count;
  parity_t parity_type_r, nxt_parity_type;
  stop_bits_t stop_bits_r, nxt_stop_bits;
  logic rx_error_r, nxt_rx_error;

  always_ff @(posedge trigger_sample_r or posedge rst) begin
    if (rst) begin
      state_r <= S_WAIT_START;
      rx_data_r <= '0;
      data_count_r   <= '0;
      stop_bits_r <= STOP_BITS_1;
      rx_error_r <= '0;
      parity_type_r <= PARITY_NONE;
    end else begin
      state_r <= nxt_state;
      rx_data_r <= nxt_rx_data;
      data_count_r   <= nxt_data_count;
      stop_bits_r <= nxt_stop_bits;
      rx_error_r <= nxt_rx_error;
      parity_type_r <= nxt_parity_type;
    end
  end

  always_comb begin
    nxt_state = state_r;
    nxt_rx_data = rx_data_r;
    nxt_data_count = data_count_r;
    nxt_stop_bits = stop_bits_r;
    nxt_rx_error = rx_error_r;
    nxt_parity_type = parity_type_r;
    // Default values for combinational signals
    rx_busy = 1'b1;
    rx_done = 1'b0;
    // nxt_rx_data = 8'b0;

    unique case (state_r)
      S_WAIT_START: begin
        rx_busy = 1'b0;
        nxt_rx_error = 1'b0;
        if (~rx)  begin //rx dropping low indicates start detect before data bits
          nxt_data_count = num_data_bits - 1;
          nxt_rx_data = 8'b0;      //reset data collection to 0
          nxt_state = S_DATA;
          //store UART config settings
          nxt_stop_bits = stop_bits;
          nxt_parity_type = parity;
          nxt_rx_error = 1'b0;
        end
      end

      //receives LSB first
      S_DATA: begin
        nxt_rx_data = {rx, rx_data_r[7:1]};
        if (data_count_r == '0) begin
          if (parity_type_r != PARITY_NONE)  nxt_state = S_PARITY;
          else nxt_state = S_STOP1;
        end
        nxt_data_count = data_count_r - 1;
      end

      S_PARITY: begin
         case (parity_type_r)
         PARITY_ODD: begin
           if (0 == ^{rx_data_r, rx}) begin
               nxt_rx_error = 1'b1; //even number of 1s, error occured
           end
         end

         PARITY_EVEN: begin
            if (1 == ^{rx_data_r, rx}) begin
               nxt_rx_error = 1'b1; //odd number of 1s, error occured
           end
         end

         default: begin
         end
       endcase

        nxt_state = S_STOP1;
      end

      S_STOP1: begin
        rx_done = 1'b1;
        if (stop_bits_r == STOP_BITS_2) nxt_state = S_STOP2;
        else begin
          nxt_state = S_WAIT_START;
        end
      end

      S_STOP2: begin
        rx_done = 1'b1;
        nxt_state = S_WAIT_START;
      end

    endcase
  end

  assign rx_error = rx_error_r;
  assign rx_data = rx_data_r;

endmodule