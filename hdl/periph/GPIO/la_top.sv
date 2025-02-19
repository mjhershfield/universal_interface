module la_top #(
    parameter width = 32
)(
    input logic clk, rst,
    input logic [width-1:0] packet_in,
    output logic [width-1:0] packet_out,
    input logic [15:0] pin_vals,
    output logic data_valid
);

    logic go;
    logic [23:0] max_count;
    logic [15:0] reads;
    logic [width-1:0] output_reg;
    logic data_valid_reg;

    assign go = packet_in[28];
    assign packet_out = output_reg;
    assign data_valid = data_valid_reg;


    clk_div #( .width(24) ) clk_div ( 
        .clk(clk), 
        .rst(rst), 
        .div_clk(div_clk),
        .max_count(max_count)
    );

    logic_analyzer #(.width(16)) logic_analyzer(
        .clk(clk),
        .rst(rst),
        .pin_vals(pin_vals),
        .reads(reads)
    );

    always_ff @(posedge clk, posedge rst) begin
        if (rst) begin
            data_valid_reg <= 1'b0;
            max_count <= '0;
            output_reg <= '0;

        end else begin
            max_count <= 24'd8; //hardcoded to 16x  div
            output_reg[31:29] <= 3'b000;
            output_reg[28] <= 1'b0;
            output_reg[27:26] <= 2'b10;
            output_reg[25:24] <= 2'b00;
            output_reg[23:16] <= '0;
            output_reg[15:0] <= reads;
            
            data_valid_reg <= 1'b1;


        end
    end
    
endmodule

/*Name	Bit field	Notes
Peripheral Address	31-29	Ranges from 0-7
Configuration Flag	28	0 = data for tx/rx
Number of valid bytes	27-26	1-3 bytes in data field of this packet
Reserved	25-24	Currently unused
Data for peripheral	23-0	Up to 3 bytes of data*/