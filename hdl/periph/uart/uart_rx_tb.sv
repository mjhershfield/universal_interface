`timescale 1 ns / 100 ps

import uart_pkg::*;

module uart_rx_tb;

logic             clk;    //this is the faster rx clock
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
logic [3:0] rx_tx_clk_ratio;

logic tx_clk;   //this is the slow clock


  uart_rx DUT (.*);

  initial begin
    clk = 1'b0;
    while (1) #5 clk = ~clk;
  end

  initial begin
    tx_clk = 1'b0;
    while (1) #40 tx_clk = ~tx_clk; //40 = 5*8 edges difference
  end

  initial begin
    rst = 1'b1;
    parity = PARITY_EVEN;
    num_data_bits = 4'd8;
    stop_bits = STOP_BITS_1;
    rx = 1'b1;
    rx_tx_clk_ratio = 4'd8;
    for (int i = 0; i < 3; i++) @(posedge tx_clk);
    @(negedge tx_clk);

    rst = 1'b0;

    @(posedge tx_clk);

    //going to transmit 177 aka B1 - 1011 0001

    //LSB to MSB 1000 1101

    //rx started high
    
    //drop low to indicate start
    @(negedge tx_clk);
    rx <= 1'b0;
    @(posedge tx_clk);

    //LSB to MSB transmission
    @(negedge tx_clk);
    rx <= 1'b1;
    @(posedge tx_clk);

    @(negedge tx_clk);
    rx <= 1'b0;
    @(posedge tx_clk);

    @(negedge tx_clk);
    rx <= 1'b0;
    @(posedge tx_clk);

    @(negedge tx_clk);
    rx <= 1'b0;
    @(posedge tx_clk);

    @(negedge tx_clk);
    rx <= 1'b1;
    @(posedge tx_clk);

    @(negedge tx_clk);
    rx <= 1'b1;
    @(posedge tx_clk);

    @(negedge tx_clk);
    rx <= 1'b0;
    @(posedge tx_clk);

    @(negedge tx_clk);
    rx <= 1'b1;
    @(posedge tx_clk);

    //even parity - checking bad
    @(negedge tx_clk);
    rx <= 1'b1;
    @(posedge tx_clk);

    //one stop bit
    @(negedge tx_clk);
    rx <= 1'b0;
    @(posedge tx_clk);

    //keep high for 5 cycles
    rx <= 1'b1;
    for (int i = 0; i < 2; i++) @(posedge tx_clk);
    @(negedge tx_clk);

    $stop;
  end
endmodule
