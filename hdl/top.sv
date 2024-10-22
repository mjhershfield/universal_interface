import lycan::*;

module top
    (
        input logic clk, // CLK provided by FT601
        input logic rst,

        // FTDI FT601 control signals
        inout logic[31:0] usb_data,
        output logic[3:0] usb_be,
        input logic usb_tx_full, // 0 = space available, 1 = full
        input logic usb_rx_empty, // 0 = data available, 1 = empty
        input logic usb_siwu, // TODO: constant pullup. can this be done in constraints?
        output logic usb_wren_l,
        output logic usb_rden_l,
        output logic usb_outen_l,
        output logic usb_rst_l,
        input logic usb_wakeup, // bidirectional. as input, 0 = USB active, 1 = usb suspended. Drive low to send remote wakeup
        input logic[1:0] usb_gpio, // TWO CONFIGURABLE GPIO. WHAT DO THEY DO?

        inout logic[width_dut_pins-1:0] dut_pins         // DUT pins
    );

    // TODO: HOW TO TRISTATE PINS THAT WE ARE NOT OUTPUTTING ON?

    // MUX all peripheral outputs out to every DUT I/O pin
    // Array to store all peripheral outputs
    localparam int num_periph_outputs = num_peripherals*outputs_per_peripheral;
    logic[num_periph_outputs-1:0] peripheral_outputs;
    // TODO: Registers to store the select value for each DUT pin.
    logic[num_dut_pins-1:0][$clog2(num_periph_outputs)-1:0] peripheral_output_selects;

    for (genvar i = 0; i < num_dut_pins; i++) begin : peripheral_output_muxes
        mux #(.NUM_INPUTS(num_periph_outputs)) periph_output_mux
            (.in(peripheral_outputs), .sel(peripheral_output_selects[i]), .out(dut_pins[i]));
    end

    // MUX all DUT pins to every peripheral input
    localparam num_periph_inputs = num_peripherals*inputs_per_peripheral;
    logic[num_periph_inputs-1:0] peripheral_inputs;
    logic[num_periph_inputs-1:0] peripheral_input_selects;

    for (genvar i = 0; i < num_periph_inputs; i++) begin : peripheral_input_muxes
        mux #(.NUM_INPUTS(num_dut_pins)) periph_input_mux
            (.in(dut_pins), .sel(peripheral_input_selects[i]), .out(peripheral_inputs[i]));
    end

endmodule
