module ft601_controller
    (
        input logic clk,
        input logic rst,

        // Control signals coming from the FT601
        input logic usb_tx_full,
        input logic usb_rx_empty,

        // Control signals going to FT601
        output logic usb_wren_l,
        output logic usb_rden_l,
        output logic usb_outen_l,
        output logic usb_rst_l,

        // 0 = input from data bus, 1 = outputting to data bus
        output logic ft601_data_bus_dir,
        // Whether valid data is coming from the arbiter
        input logic periph_data_available,
        // Allow peripherals to send data back to USB host
        output logic read_periph_data
    );

endmodule
