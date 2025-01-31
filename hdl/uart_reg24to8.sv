module uart_reg24to8 (
    input  logic        clk,
    input  logic        rst,
    input  logic        wren,
    input  logic [31:0] din,
    input  logic        rden,
    output logic [ 7:0] dout,
    output logic        valid
);

  logic [23:0] data_r, nxt_data;
  logic [1:0] count_r, nxt_count;
  logic [1:0] num_valid_r, nxt_num_valid;

  always_ff @(posedge clk or posedge rst) begin
    if (rst) begin
      data_r <= 24'd0;
      count_r <= 2'b00;
      num_valid_r <= 2'b00;
    end else begin
      data_r <= nxt_data;
      count_r <= nxt_count;
      num_valid_r <= nxt_num_valid;
    end
  end

  always_comb begin
    nxt_data = data_r;
    nxt_count = count_r;
    nxt_num_valid = num_valid_r;

    valid = (count_r < num_valid_r);

    if (wren) begin
      nxt_data  = din[23:0];
      nxt_count   = 2'b0;
      nxt_num_valid = din[27:26];
    end else if (rden) begin
      nxt_count = count_r + 1;
    end

    // Set dout based on the current accessed register
    unique case (count_r)
      2'd0: dout = data_r[7:0];  //output is dependant on reg_count
      2'd1: dout = data_r[15:8];
      2'd2: dout = data_r[23:16];
      2'd3: dout = '0;
    endcase
  end


endmodule
