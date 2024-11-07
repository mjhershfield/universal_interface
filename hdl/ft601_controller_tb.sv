`timescale 1 ns/100 ps

module ft601_controller_tb;

        logic clk = 1'b1;
        logic rst;

        // Control signals coming from the FT601
        logic usb_txe;
        logic usb_rxf;

        // Control signals going to FT601
        logic usb_wren_l;
        logic usb_rden_l;
        logic usb_outen_l;
        logic usb_rst_l;

        //data going to peripheral
        logic [31:0] data_o;
        logic [3:0] o_valid; //what bytes of data are valid

        //data coming from peripheral
        logic [31:0] data_i;
        logic [3:0] i_valid; //what bytes of data are valid

        //ftdi data bus
        wire [31:0] data;
        wire [3:0] be; //what bytes of data are valid
        //logic be_ts;
        //logic data_ts;


        // // 0 = from data bus; 1 = outputting to data bus
        // logic ft601_data_bus_dir;
        // // Whether valid data is coming from the arbiter
        // logic periph_data_available;
        // // Allow peripherals to send data back to USB host
        // logic read_periph_data
        // Whether valid data is coming from the arbiter
        logic periph_data_available;
        // Whether we are currently reading data from the arbiter
        logic read_periph_data;

        localparam period = 20;

            always begin : generate_clock
                #5 clk = ~clk;
            end

    ft601_controller DUT (
        .clk(clk),
        .rst(rst),
        .usb_txe(usb_txe),
        .usb_rxf(usb_rxf),
        .usb_wren_l(usb_wren_l),
        .usb_rden_l(usb_rden_l),
        .usb_outen_l(usb_outen_l),
        .usb_rst_l(usb_rst_l),
        .data_o(data_o),
        .o_valid(o_valid),
        .data_i(data_i),
        .i_valid(i_valid),
        .data(data),
        .be(be),
        .periph_data_available(periph_data_available),
        .read_periph_data(read_periph_data)
    );

        initial begin : drive_inputs
            $timeformat(-9, 0, " ns");

                rst <= 1'b1;
                usb_txe <= 1'b1;
                usb_rxf <= 1'b1;
                data_i <= 8'hFF00FF00;
                i_valid <= 4'b1111;



                for (int i = 0; i < 5; i++) 
                    @(posedge clk);

                @(negedge clk);
                rst <= 1'b0;
                @(posedge clk);

                usb_txe <= 1'b0;

                for (int i = 0; i < 5; i++) 
                    @(posedge clk);

                


	disable generate_clock;
        end

	
endmodule