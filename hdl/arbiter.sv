module arbiter(
        // Control signals from local peripheral FIFOs
        input logic [7:0] rx_fifo_empty, //same as fifo not empty
        input logic [7:0] rx_fifo_almost_full,
        // If FT601 controller has set USB bus to send data to host, sent from Gilon controller

        input logic rst,
        input logic clk,

        //transmission occuring signal to allow for grant to change
        input logic read_periph_data,

        // Number of peripheral that has control of the bus, goes to demux
        output logic [2:0] grant
        // Whether data is currently being sent to the FT601.
    );

    logic [2:0] curr_grant = 3'b000;
    logic [7:0] barrel_sh_out;
    logic [2:0] next_grant;

    logic [7:0] rx_request = ~rx_fifo_empty; //make active high request

    //logic to modify request signal if any fifos are almost full
    always_comb begin
        if (rx_fifo_almost_full > 0)
            assign rx_request = rx_fifo_almost_full;
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

    //Structural
    barrel_shifter BAR_SH_1 (.in(rx_request), .sh_amt(curr_grant), .out(barrel_sh_out));
    priority_encoder PRI_EN_1 (.data(barrel_sh_out), .y(next_grant));

    assign grant = next_grant;
    
endmodule