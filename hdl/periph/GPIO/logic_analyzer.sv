module logic_analyzer #(parameter width = 16)
(
    input logic clk,
    input logic rst,
    input logic [width-1:0] pin_vals,
    
    output logic [width-1:0] reads
);

always_ff @(posedge clk, posedge rst) begin

    if (rst) begin
        reads <= '0;
    end else begin
        reads <= pin_vals;
    end

end
endmodule