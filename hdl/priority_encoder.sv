module priority_encoder(
    input logic [7:0]data;
    output reg [2:0]y;
);
  
    always_comb begin
        if(data[7]==1) y=3'b111;
        else if(i[6]==1) y=3'b110;
        else if(i[5]==1) y=3'b101;
        else if(i[4]==1) y=3'b100;
        else if(i[3]==1) y=3'b011;
        else if(i[2]==1) y=3'b010;
        else if(i[1]==1) y=3'b001;
        else y=3'b000;
    end
endmodule