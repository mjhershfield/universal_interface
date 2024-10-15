module mux
#(
    parameter int NUM_INPUTS,
    parameter int WIDTH_INPUTS = 1,
    localparam int WIDTH_SELECT = $clog2(NUM_INPUTS)
)
(
    input logic[NUM_INPUTS-1:0][WIDTH_INPUTS-1:0] in,
    input logic[WIDTH_SELECT-1:0] sel,
    output logic[WIDTH_INPUTS-1:0] out
);

    always_comb begin
        for (int i = 0; i < NUM_INPUTS; i++) begin
            if (sel == i) begin
                out = in[i];
            end
        end
    end

endmodule
