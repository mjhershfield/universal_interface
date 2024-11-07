module arbiter
    (
        input logic clk,
        input logic rst,

        // Control signals from local peripheral FIFOs
        input logic rx_fifo_empty[7:0],
        input logic rx_fifo_almost_full[7:0],

        // If data is being currently read from the peripheral into the FT601
        input logic read_periph_data, 

        // Number of peripheral that has control of the bus
        output logic grant[2:0],
    );

    logic [2:0] curr_grant = 3'b000;
    logic [7:0] barrel_sh_out;
    logic [2:0] next_grant;

    logic [7:0] rx_request = ~rx_fifo_empty; // make active high request

    // Logic to modify request signal if any FIFOs are almost full
    always_comb begin
        if (rx_fifo_almost_full > 0)
            assign rx_request = rx_fifo_almost_full;
        else
            rx_request = ~rx_fifo_empty;
    end

    always_ff @(posedge clk) begin
        if (rst)
            curr_grant <= 3'b000;
        else
            if (read_periph_data)
                curr_grant <= next_grant;
            else
                curr_grant <= curr_grant;
    end

    // Structural
    barrel_shifter BAR_SH_1 (.in(rx_request), .sh_amt(curr_grant), .out(barrel_sh_out));
    priority_encoder PRI_EN_1 (.data(barrel_sh_out), .y(next_grant));

    assign grant = next_grant;

endmodule