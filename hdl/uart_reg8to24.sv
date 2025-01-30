module uart_reg24to8 (
    input logic         clk,
    input logic         rst,
    input logic         wren,
    input logic     [7:0] dIn,
    input logic         rden,
    output logic    [23:0] dOut,
    output logic        valid
);

logic [23:0] register;

always_ff @(posedge clk or posedge rst) begin
    if (rst) begin
        register <= 24'd0;      //place zeros into registers
        dOut <= 24'd0;
        valid <= 1'b0;
    end else begin
        if (wren) begin      
            register <= {register[15:0], dIn};  //shift in 8 bits when wren is true
            valid <= 1'b1;                      //we have valid bits now
        end
        if (rden && valid) begin
            dOut <= register;               //output bits when rden is true
            valid <= 1'b0'
        end
        
    end
end




