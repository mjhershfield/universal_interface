module uart_reg8to24 (
    input  logic        clk,
    input  logic        rst,
    input  logic        wren,
    input  logic [ 7:0] din,
    input  logic        rden,
    output logic [31:0] dout,
    output logic [1:0] valid_bytes
);

  logic [23:0] data_r, nxt_data;
  logic [1:0] valid_bytes_r, nxt_valid_bytes;

  always_ff @(posedge clk or posedge rst) begin
    if (rst) begin
      data_r <= 24'd0;
      valid_bytes_r <= 2'b00;
    end else begin
      data_r <= nxt_data;
      valid_bytes_r <= nxt_valid_bytes;
    end
  end

  always_comb begin
    nxt_data = data_r;
    nxt_valid_bytes = valid_bytes_r;

    // if write, set 8 bits defined by count to din
    // if read, reset count to 0
    if (rden) begin
      nxt_valid_bytes = '0;
      nxt_data = '0;
    end 
    if (wren) begin
      unique0 case (valid_bytes_r)
        2'd0: nxt_data[7:0] = din;
        2'd1: nxt_data[15:8] = din;
        2'd2: nxt_data[23:16] = din;
      endcase;
      if (valid_bytes_r != 2'd3)
        nxt_valid_bytes = valid_bytes_r + 1;
    end

    dout = data_r;
    valid_bytes = valid_bytes_r;
  end


endmodule
