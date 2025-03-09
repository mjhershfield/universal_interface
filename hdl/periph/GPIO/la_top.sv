module la_top #(
    parameter width = 32
)(
    input logic clk, rst,
    input logic [width-1:0] packet_in,
    (* mark_debug = "true" *)output logic [width-periph_address_width-1:0] packet_out,
    input logic [15:0] pin_vals,
    (* mark_debug = "true" *)output logic data_valid
);

    logic go;
    logic [23:0] max_count;
    logic [15:0] reads;
    logic div_clk;
    logic div_clk_rising;

    assign go = packet_in[28];



    clk_div #( .width(24) ) clk_div ( 
        .clk(clk), 
        .rst(rst), 
        .div_clk(div_clk),
        .max_count(max_count)
    );

    logic_analyzer #(.width(16)) logic_analyzer(
        .clk(div_clk),
        .rst(rst),
        .pin_vals(pin_vals),
        .reads(reads)
    );

    edge_detect edge_inst (
        .clk(clk), 
        .rst(rst),
        .signal_in(div_clk),
        .posedge_detected(div_clk_rising)
    );


    always_ff @(posedge clk, posedge rst) begin
        if (rst) begin
            data_valid <= 1'b0;
            max_count <= '0;
            packet_out <= '0;

        end else begin
            max_count <= 24'd1; //approx 1 read every 32sec
            packet_out <= {1'b0, 2'b10, 2'b00, 8'h00, reads};
            // packet_out[28] <= 1'b0;
            // packet_out[27:26] <= 2'b10;
            // packet_out[25:24] <= 2'b00;
            // packet_out[23:16] <= '0;
            // packet_out[15:0] <= reads;
            
            data_valid <= 1'b1 & div_clk_rising;


        end
    end
    
endmodule

/*Name	Bit field	Notes
Peripheral Address	31-29	Ranges from 0-7
Configuration Flag	28	0 = data for tx/rx
Number of valid bytes	27-26	1-3 bytes in data field of this packet
Reserved	25-24	Currently unused
Data for peripheral	23-0	Up to 3 bytes of data*/

// 0000 1000 0000 0000 1111 1111 1111 1111