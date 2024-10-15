module ft601_controller
    (
        // Control signals coming from the FT601
        input logic tx_full,
        input logic rx_empty,
        // Whether valid data is coming from the arbiter
        input logic tx_valid,
        // Control signals going to FT601
        output logic wren,
        output logic rden,
        output logic outen,
        output logic rst,
        // 0 = input from data bus, 1 = outputting to data bus
        output logic data_bus_dir,
        // Allow peripherals to send data back to USB host
        output logic allow_tx
    );

endmodule
