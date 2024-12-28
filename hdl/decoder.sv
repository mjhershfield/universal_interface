module decoder #(
    parameter int WIDTH
) (
    input logic [$clog2(WIDTH)-1:0] in,
    input logic valid,
    output logic[WIDTH-1:0] out
);

always_comb begin
    for (int i = 0; i < WIDTH; i++) begin
        if (in == i && valid == 1) begin
            out[i] = 1'b1;
        end else begin
            out [i] = 1'b0;
        end
    end
end

endmodule
