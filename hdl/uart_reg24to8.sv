module uart_reg24to8 (
    input logic         clk,
    input logic         rst,
    input logic         wren,
    input logic     [23:0] dIn,
    input logic         rden,
    output logic    [7:0] dOut,
    output logic        valid    //error
);

logic [23:0] register
logic [1:0] reg_count;

always_ff @(posedge clk or posedge rst) begin
    if (rst) begin
        register <= 24'd0;      //place zeros into registers
        dOut <= 8'd0;
        reg_count <= 2'd0;
        valid <= 1'b0;
    end else begin      //write the 24 bits into the registers and set valid to true as there is data to be read
        if (wren) begin
            register <= dIn;
            valid <= 1'b1;             //since we have data to read it is valid
            reg_count <= 2'd0;
        end
        if (rden && valid) begin
            case (reg_count)
                2'd0: dOut <= register[7:0];    //output is dependant on reg_count
                2'd1: dOut <= register[15:8];
                2'd2: dOut <= register[23:16];
            endcase

            if(reg_count == 2'd2) begin          //after 3 clock cycles we reset the reg_count and make data invalid
                reg_count <= 2'd0;
                valid <= 1'b0;
            end else begin
                reg_count <= reg_count + 1;     
            end
        end
    end
end






