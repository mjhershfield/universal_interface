module priority_encoder (
    input  logic [7:0] data,
    output reg   [2:0] y
);

  always_comb begin
    if (data[7] == 1) y = 7;
    else if (data[6] == 1) y = 6;
    else if (data[5] == 1) y = 5;
    else if (data[4] == 1) y = 4;
    else if (data[3] == 1) y = 3;
    else if (data[2] == 1) y = 2;
    else if (data[1] == 1) y = 1;
    else y = 0;
  end
endmodule
