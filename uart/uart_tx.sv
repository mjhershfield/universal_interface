module uart_tx (
      output   logic       tx,
      output   logic       tx_done,
      output   logic       tx_busy,      
      input    logic [7:0] tx_data,
      input    logic       tx_start,
      input    logic [1:0] stop_bits,
      input    string      parity,
      input    logic       clk, 
      input    logic       rst
   );

   // i think it kinda works dont hate on the ternary operators
   localparam IDLE_VAL  = 1'b1;
   localparam START_VAL = 1'b0;
   localparam STOP_VAL  = 1'b1;

   typedef enum logic [1:0] {
      STATE_IDLE,
      STATE_START,
      STATE_DATA,
      STATE_PARITY,
      STATE_STOP,
      STATE_STOP2
   } t_fsm_state;

   t_fsm_state state, nxt_state;

   logic [2:0] pos, pos_nxt;
   logic       parity_bit;
   logic       tx_nxt;

   always_comb begin
    if (parity == "even")
        parity_bit = ^tx_data;
    else if (parity == "odd")
        parity_bit = ~^tx_data;
    else
        parity_bit = 1'b0;
   end

   always_ff @ (posedge clk or posedge rst) begin
      if (rst) begin
         state <= STATE_IDLE;
         tx    <= IDLE_VAL;
         pos   <= '0;
      end
      else begin
         state <= nxt_state;
         tx    <= tx_nxt;
         pos   <= pos_nxt;
      end
   end

   always_comb begin  //5 or 6 states depending on stop bits IDLE -> START -> DATA -> PARITY -> STOP1&2
      nxt_state = STATE_IDLE;
      pos_nxt   = '0;      
      tx_nxt    = IDLE_VAL;
      case (state)
         STATE_IDLE: begin
            nxt_state = tx_start ? STATE_START : STATE_IDLE;
            tx_nxt    = tx_start ? START_VAL   : IDLE_VAL;
         end

         STATE_START: begin
            nxt_state = STATE_DATA;
            tx_nxt    = tx_data[pos];
            pos_nxt   = pos + 1'b1;
         end
        
         STATE_DATA: begin
            if (pos == data_bits - 1) begin 
                nxt_state = (parity == "none") ? STATE_STOP : STATE_PARITY;
            end
            else begin
                nxt_state = STATE_DATA;
                pos_nxt   = pos + 1'b1;
            end
            tx_nxt    = tx_data[pos];
        end

        STATE_PARITY: begin
            nxt_state = STATE_STOP;
            tx_nxt = parity_bit;
        end
      
         STATE_STOP: begin
            nxt_state = (stop_bits == 2) ? STATE_STOP2 : STATE_IDLE;
            tx_nxt    = STOP_VAL;
         end

         STATE_STOP2: begin 
            nxt_state = STATE_IDLE;
            tx_next = STOP_VAL;
         end

      endcase
   end

   assign tx_busy = (state != STATE_IDLE);
   assign tx_done = (state == STATE_STOP);

endmodule
