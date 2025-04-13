module clk_div #(
    parameter width = 24
)

(
    input logic clk,
    input logic rst,

    output logic div_clk,

    input logic [width-1:0] max_count
);

logic [width-1:0] count;

always_ff @( posedge clk, posedge rst ) begin
    if (rst) begin
        div_clk <= 1'b0;
        count <= '0;
    end else begin
        if (count == '0) begin
            div_clk <= ~div_clk;
            count <= max_count - 1;
        end else begin
            div_clk <= div_clk;
            count <= count -1;
        end
    end
    
end

endmodule

