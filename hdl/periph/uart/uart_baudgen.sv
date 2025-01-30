

module baudrategen (
    output logic       baud_out,  // output of baud gen
    input  logic       clkin,     // input  clock of baud gen (100MHz)
    input  logic       rst,       // reset
    input  logic [1:0] baud_sel   // 00-19200, 01-38400, 10-57600, 11 - 115200
);

  localparam LOAD_VAL_BAUD_19200 = 13'd2604;
  localparam LOAD_VAL_BAUD_38400 = 13'd1302;
  localparam LOAD_VAL_BAUD_57600 = 13'd868;
  localparam LOAD_VAL_BAUD_115200 = 13'd434;

  logic [12:0] load_val;
  logic [12:0] cnt_r, cnt_nxt, cnt_m1;

  logic baud_out_r, nxt_baud_out;

  // decode baud_sel to obtain buad generator load value
  always_comb begin
    unique case (baud_sel)
      2'b00: load_val = LOAD_VAL_BAUD_19200;
      2'b01: load_val = LOAD_VAL_BAUD_38400;
      2'b10: load_val = LOAD_VAL_BAUD_57600;
      2'b11: load_val = LOAD_VAL_BAUD_115200;
    endcase
  end

  // counter logic
  assign cnt_m1   = cnt_r - 1'b1;
  assign cnt_nxt  = (cnt_r == '0) ? load_val : cnt_m1;  // reload counter with load value
  assign nxt_baud_out = (cnt_r == '0) ? ~baud_out_r : baud_out_r;
  assign baud_out = baud_out_r;

  always_ff @(posedge clkin or posedge rst) begin
    if (rst) begin
      cnt_r <= '0;
      baud_out_r <= 1'b0;
    end else begin
      cnt_r <= cnt_nxt;
      baud_out_r <= nxt_baud_out;
    end
  end

endmodule
