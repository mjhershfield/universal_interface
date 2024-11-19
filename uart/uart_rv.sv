
module uart_rx (
      output   logic       rx_done,
      output   logic       rx_busy,
      output   logic [7:0] rx_data,
      input    logic       rx,      
      input    logic       rx_start,  // enable signal for rx logic
      input    logic [1:0] stop_bits,
      input    string       parity,
      input    logic       clk, 
      input    logic       rst
   );

   localparam IDLE_VAL  = 1'b1;
   localparam START_VAL = 1'b0;

   typedef enum logic [1:0] {
      STATE_IDLE,
      STATE_START,
      STATE_DATA,
      STATE_PARITY,
      STATE_STOP,
      STATE_STOP2
   } t_fsm_state;

   t_fsm_state state, nxt_state;

   logic [7:0] rx_data_nxt;
   logic       parity_bit;
   logic       parity_error,
   logic [2:0] pos, pos_nxt;

   always_ff @ (posedge clk or posedge rst) begin
      if (rst) begin
         state <= STATE_IDLE;
         pos   <= '0;
      end
      else begin
         state <= nxt_state;
         pos   <= pos_nxt;
      end
   end

   always_comb begin  
      parity_bit = (parity = "even") ? ^rx_data : ~^rx_data;
      parity_error = (parity != "none" && parity_bit != rx);
   end 

   // rx_data flop
   always_ff @(posedge clk)
      rx_data <= rx_data_nxt;

   always_comb begin                          //5 or 6 states depending on stop bits IDLE -> START -> DATA -> PARITY -> STOP1&2
      nxt_state   = STATE_IDLE;
      pos_nxt     = '0;
      rx_data_nxt = rx_data;
      case (state)
         STATE_IDLE: begin
            nxt_state = rx_start ? ((rx != IDLE_VAL) ? STATE_START : STATE_IDLE) : STATE_IDLE;
         end

         STATE_START: begin
            nxt_state = STATE_DATA;
            pos_nxt   = pos + 1'b1;
            rx_data_nxt[pos] = rx;    // first bit
         end

         STATE_DATA: begin
            nxt_state         = (pos == data_bits - 1) ? ((parity == "none") ? STATE_STOP : STATE_PARITY) : STATE_DATA;
            pos_nxt           = pos + 1'b1;
            rx_data_nxt[pos]  = rx;
         end

         STATE_PARITY: begin
            nxt_state = STATE_STOP;
         end 
      
         STATE_STOP: begin
            nxt_state = (stop_bits == 2) ? STATE_STOP : STATE_IDLE;
         end

         STATE_STOP2: begin
            nxt_state = STATE_IDLE;
         end

      endcase
   end
   
   assign rx_busy = (state != STATE_IDLE);
   assign rx_done = (state == STATE_STOP);
   
endmodule

