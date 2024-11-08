module barrel_shifter(
    input logic [7:0] in,
    input logic [2:0] sh_amt,
    output logic [7:0] out
);

    always_comb begin
        case (sh_amt)
            0: out = in;
            1: out = {in[0], in[7:1]};//right sh 1
            2: out = {in[1:0], in[7:2]};//rs 2
            3: out = {in[2:0], in[7:3]};//rs 3
            4: out = {in[3:0], in[7:4]};//rs 4
            5: out = {in[4:0], in[7:5]};//rs 5
            6: out = {in[5:0], in[7:6]};// rs 6
            default out = {in[6:0], in[7]}; //ls 1
        endcase
    end
endmodule