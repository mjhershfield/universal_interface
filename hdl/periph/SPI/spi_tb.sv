`timescale 1ns/1ps

module spi_tb;

    parameter WIDTH = 8;  //8-bit SPI transfer

    logic clk;
    logic rst;
    logic [WIDTH-1:0] master_tx_data;
    logic master_tx_empty;
    logic [WIDTH-1:0] slave_tx_data;
    logic [WIDTH-1:0] master_rx_data;
    logic [WIDTH-1:0] slave_rx_data;
    logic master_rx_valid;
    logic slave_rx_valid;
    logic master_tx_busy;

    //SPI signals
    logic CS_L;
    logic SCLK;
    logic MOSI;
    logic MISO;

    //clock divider count for master SCLK generation
    logic [7:0] sclk_div_count = 8'd4;

    // Instantiate SPI Master
    spi_master #(
        .WIDTH(WIDTH)
    ) master (
        .clk(clk),
        .rst(rst),
        .tx_data(master_tx_data),
        .tx_empty(master_tx_empty),
        .CS_L(CS_L),
        .SCLK(SCLK),
        .MOSI(MOSI),
        .MISO(MISO),
        .sclk_div_count(sclk_div_count),
        .rx_data(master_rx_data),
        .rx_valid(master_rx_valid)
    );

    // Instantiate SPI Slave
    spi_slave #(
        .WIDTH(WIDTH)
    ) slave (
        .clk(clk),
        .rst(rst),
        .CS_L(CS_L),
        .SCLK(SCLK),
        .MOSI(MOSI),
        .MISO(MISO),
        .tx_data(slave_tx_data),
        .rx_data(slave_rx_data),
        .rx_valid(slave_rx_valid),
        .tx_busy(master_tx_busy)
    );

    //clk gen
    always #5 clk = ~clk;

    initial begin
        clk = 0;
        rst = 1;
        master_tx_empty = 1;
        master_tx_data = 8'hA5;  //master sends 0xA5
        slave_tx_data = 8'h3C;   //slave sends 0x3C

        #20 rst = 0;

        $display("Initializing data transfer.");

        //master starts transfer
        @(negedge SCLK);
        master_tx_empty = 0;
        @(posedge SCLK);
        @(negedge SCLK);
        #10 master_tx_empty = 1;
        @(posedge SCLK);

        //wait for transfer to finish
        wait(master_rx_valid);
        if (slave_rx_data == master_tx_data) begin
            $display("TEST PASSED: Slave received correct data from Master: %h", slave_rx_data);
        end else begin
            $display("TEST FAILED: Slave received incorrect data: %h", slave_rx_data);
        end


        wait(slave_rx_valid);

        //check data
        if (master_rx_data == slave_tx_data) begin
            $display("TEST PASSED: Master received correct data from Slave: %h", master_rx_data);
        end else begin
            $display("TEST FAILED: Master received incorrect data: %h", master_rx_data);
        end


        $finish;
    end

endmodule
