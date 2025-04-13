`timescale 1 ns / 100 ps

module generic_config_regs_tb;

    parameter WIDTH = 32;

    logic clk;
    logic rst;
    logic [WIDTH-1:0] packet;
    logic [WIDTH-9:0] read_data;
    logic valid;
    logic [WIDTH-9:0] all_regs [8];

    generic_config_regs #(.WIDTH(WIDTH)) dut (
        .clk(clk),
        .rst(rst),
        .packet(packet),
        .read_data(read_data),
        .valid(valid),
        .all_regs(all_regs)
    );

    initial begin
        clk = 1'b0;
        while (1) #5 clk = ~clk;
    end

    initial begin
        rst = 1'b1;
        packet = 0;

        for (int i = 0; i < 3; i++) @(posedge clk);
        @(negedge clk);

        rst = 1'b0;

        @(posedge clk);

        //write values to all registers
        for (int i = 0; i < 8; i++) begin
            packet <= {5'b00011, i[2:0], 16'hDDD0, i[7:0]}; //write to all packets with unique data
            @(posedge clk);
        end

        //read back and check data
        for (int i = 0; i < 8; i++) begin
            packet <= {5'b00010, i[2:0], 24'h000000}; //read
            @(posedge clk);
            if (read_data != (24'hDDD000 + i)) begin
                $display("ERROR: Register %0d read mismatch. Expected %h, Got %h", i, 24'hDDD000 + i, read_data);
            end else begin
                $display("PASS: Register %0d read correctly: %h", i, read_data);
            end
        end

        //check all_regs external exposure
        $display("Checking all_regs output:");
        for (int i = 0; i < 8; i++) begin
            if (all_regs[i] != (24'hDDD000 + i)) begin
                $display("ERROR: all_regs[%0d] mismatch. Expected %h, Got %h", i, 24'hDDD000 + i, all_regs[i]);
            end else begin
                $display("PASS: all_regs[%0d] = %h", i, all_regs[i]);
            end
        end

        $display("Testbench finished.");
        $finish;
    end

endmodule
