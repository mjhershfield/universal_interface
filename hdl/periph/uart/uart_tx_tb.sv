`timescale 1 ns / 100 ps

import uart_pkg::*;

module uart_tx_tb;

  logic             clk;
  logic             rst;
  logic             tx;
  logic             tx_busy;
  logic       [7:0] tx_data;
  logic             tx_empty;
  logic             tx_rden;
  logic       [3:0] num_data_bits;
  stop_bits_t       stop_bits;
  parity_t          parity;

  uart_tx DUT (.*);

  initial begin
    clk = 1'b0;
    while (1) #5 clk = ~clk;
  end

  initial begin
    rst = 1'b1;
    parity = PARITY_NONE;
    num_data_bits = 4'd8;
    stop_bits = STOP_BITS_1;
    tx_data = 8'h2B;
    tx_empty = 1'b0;
    for (int i = 0; i < 5; i++) @(posedge clk);
    @(negedge clk);

    rst = 1'b0;

    @(negedge tx_rden);
    // Change configuration for next read
    tx_data = 8'h53;
    stop_bits = STOP_BITS_2;
    // Wait for next TX to start
    @(posedge tx_rden);

    @(negedge tx_rden);
    tx_data = 8'h71;
    parity = PARITY_EVEN;
    @(posedge tx_rden);

    @(negedge tx_rden);
    parity = PARITY_ODD;
    @(posedge tx_rden);

    // Wait for final tx to complete
    @(posedge tx_rden);
    $stop;
  end
endmodule
