module uart_peripheral #(
    parameter baud_rate = 9600,
    parameter clock_freq = 10000000,
    parameter parity = "none",  // Options: "none", "even", "odd"
    parameter data_bits = 8,
    parameter stop_bits = 1
) (
    // 
    input logic clk,
    input logic rst,

    // UART signals
    input  logic rx,  // UART RX input from external device
    output logic tx,  // UART TX output to external device

    // FIFO interfaces
    input logic [usb_packet_width-1:0] tx_data,
    input logic tx_empty,
    output logic tx_rden,
    output logic tx_busy,

    output logic [usb_packet_width-1:0] rx_data,
    input logic rx_full,
    output logic rx_wren
);


  baudrategen baudgen (
      .baud_out(baud_out),
      .clkin   (clkin),
      .rst     (rst),
      .baud_sel(baud_sel)
  );


  uart_tx transmitter (
      .clk     (baud_out),
      .rst     (rst),
      .tx      (tx),
      .tx_busy (tx_busy),
      .tx_data (tx_data),
      .tx_empty(tx_empty),
      .tx_rden (tx_rden)
  );

  uart_rx receiver (
      .rx      (rx),
      .rx_done (rx_done),
      .rx_busy (rx_busy),
      .rx_data (rx_data),
      .rx_start(rx_start),
      .clk     (baud_out),
      .rst     (rst)
  );


  //we still need to add the FIFO stuff somewhere here
endmodule




