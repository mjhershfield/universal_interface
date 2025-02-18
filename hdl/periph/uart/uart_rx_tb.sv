`timescale 1 ns / 100 ps

import uart_pkg::*;

module uart_rx_tb;

logic             clk;
logic             rst;
logic             rx;
logic             rx_busy;
logic       [7:0] rx_data;
logic             rx_full;
logic             rx_error;
logic             rx_done;
logic [3:0] num_data_bits;
stop_bits_t       stop_bits;
parity_t          parity;

  uart_rx DUT (.*);

  initial begin
    clk = 1'b0;
    while (1) #5 clk = ~clk;
  end

  initial begin
    rst = 1'b1;
    parity = PARITY_EVEN;
    num_data_bits = 4'd8;
    stop_bits = STOP_BITS_1;
    rx = 1'b1;
    for (int i = 0; i < 3; i++) @(posedge clk);
    @(negedge clk);

    rst = 1'b0;

    @(posedge clk);

    //going to transmit 177 aka B1 - 1011 0001

    //LSB to MSB 1000 1101

    //rx started high
    
    //drop low to indicate start
    @(negedge clk);
    rx <= 1'b0;
    @(posedge clk);

    //LSB to MSB transmission
    @(negedge clk);
    rx <= 1'b1;
    @(posedge clk);

    @(negedge clk);
    rx <= 1'b0;
    @(posedge clk);

    @(negedge clk);
    rx <= 1'b0;
    @(posedge clk);

    @(negedge clk);
    rx <= 1'b0;
    @(posedge clk);

    @(negedge clk);
    rx <= 1'b1;
    @(posedge clk);

    @(negedge clk);
    rx <= 1'b1;
    @(posedge clk);

    @(negedge clk);
    rx <= 1'b0;
    @(posedge clk);

    @(negedge clk);
    rx <= 1'b1;
    @(posedge clk);

    //even parity - checking bad
    @(negedge clk);
    rx <= 1'b1;
    @(posedge clk);

    //one stop bit
    @(negedge clk);
    rx <= 1'b0;
    @(posedge clk);

    //keep high for 5 cycles
    rx <= 1'b1;
    for (int i = 0; i < 2; i++) @(posedge clk);
    @(negedge clk);

    $stop;
  end
endmodule
