// Wrapper for reconfigurable peripherals.
// All reconfigurable peripherals must share this interface.
// Make a copy of this file to create a new peripheral.

import lycan_globals::*;

module GPIO (
    input logic clk,
    input logic rst,

    (* mark_debug = "true" *) input logic [16-1:0] in,
    output logic [outputs_per_peripheral-1:0] out,
    // For now, only need to tristate a subset of all outputs
    output logic [tristates_per_peripheral-1:0] tristate,

    // peripheral address is not stored in the local FIFOs.
    (* mark_debug = "true" *) input logic [usb_packet_width-periph_address_width-1:0] tx_data,
    (* mark_debug = "true" *) input logic tx_empty,
    (* mark_debug = "true" *) output logic tx_rden,

    (* mark_debug = "true" *) output logic [usb_packet_width-periph_address_width-1:0] rx_data,
    (* mark_debug = "true" *) output logic rx_wren,
    input logic rx_full,

    output logic idle
);

  logic [usb_packet_width-periph_address_width-1:0] gpio_out_data;
  logic gpio_out_valid;

  // assign gpio_out_data = '1;
  // assign gpio_out_valid = 1'b0;

  la_top #( .width(32) )logic_analyzer
  (
    .clk(clk),
    .rst(rst),
    .packet_in(tx_data),
    .packet_out(gpio_out_data),
    .pin_vals(in),
    .data_valid(gpio_out_valid),
    .en(all_gpio_cfg_regs[GPIO_CONFIG_ENABLE][0]),
    .max_count(all_gpio_cfg_regs[GPIO_CONFIG_SAMPLE_RATE][23:0])
);

(* mark_debug = "true" *) logic [28:0] gpio_cfg_read_data;
(* mark_debug = "true" *) logic gpio_cfg_valid;
logic [23:0] all_gpio_cfg_regs [8];

(* mark_debug = "true" *) logic cfg_read_en, cfg_write_en;

generic_config_regs #(
    .reset_vals({PERIPH_GPIO, 1'b0, 24'd6250000, 1'b0, 1'b0, 1'b0, 1'b0, 1'b0})
  )
  uart_config_regs (
      .clk(clk),
      .rst(rst),
      .packet(tx_data),
      .cfg_read_en(cfg_read_en),
      .cfg_write_en(cfg_write_en),
      .read_data(gpio_cfg_read_data),
      .valid(gpio_cfg_valid),
      .all_regs(all_gpio_cfg_regs)
  );

  always_comb begin
    tx_rden = (tx_data[28] && ~tx_empty);
    rx_wren = gpio_out_valid || gpio_cfg_valid;
    cfg_read_en = ((tx_data[28] == 1) && (tx_data[27] == 0) && tx_rden);
    cfg_write_en = ((tx_data[28] == 1) && (tx_data[27] == 1) && tx_rden);
  
    if (gpio_out_valid && ~gpio_cfg_valid) rx_data = gpio_out_data;
    else rx_data = gpio_cfg_read_data;
  
  end

endmodule
