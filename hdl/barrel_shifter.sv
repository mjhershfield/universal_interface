module barrel_shifter(
    input logic [7:0]in,
    input logic [2:0]sh_amt,
    output logic [7:0]out
);

    always_comb begin
        case (sh_amt)
            000: out = in;
            001: out = {in[0], in[7:1]};
            010: out = {in[1:0], in[7:2]};
            011: out = {in[2:0], in[7:3]};
            100: out = {in[3:0], in[7:4]};
            101: out = {in[4:0], in[7:5]};
            110: out = {in[5:0], in[7:6]};
            default out = {in[6:0], in[7];}
        endcase
    end
endmodule