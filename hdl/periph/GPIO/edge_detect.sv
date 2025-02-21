module edge_detect (
    input logic clk,       // System clock
    input logic rst,       // Reset signal
    input logic signal_in, // Input signal to detect edge on
    output logic posedge_detected // High for one cycle on rising edge
);

    logic signal_prev;

    always_ff @(posedge clk, posedge rst) begin
        if (rst) begin
            signal_prev <= 1'b0;
            posedge_detected <= 1'b0;
        end else begin
            posedge_detected <= (~signal_prev & signal_in); // Detect rising edge
            signal_prev <= signal_in; // Store previous state
        end
    end

endmodule
