//checks if data is a config packet and if so forwards to uart config_reg
//if not sends on to tx_splitter
import lycan_globals::*;

module cfg_packet_check #(
    parameter WIDTH = 32
)(
    input logic [usb_packet_width-periph_address_width-1:0] tx_data,
    output logic [WIDTH-1:0] tx_splitter_data,
    output logic [WIDTH-1:0] uart_config_data
);

    always_comb begin

        tx_splitter_data = '0;
        uart_config_data = '0;

        if (tx_data[28] == 0) begin
            //data for tx/rx
            tx_splitter_data = tx_data;
        end else begin
            uart_config_data = tx_data;
        end

    end


endmodule