module ft601_controller
    (
        input logic clk,
        input logic rst,

        // Control signals coming from the FT601
        input logic usb_txe,
        input logic usb_rxf,

        // Control signals going to FT601
        output logic usb_wren_l,
        output logic usb_rden_l,
        output logic usb_outen_l,
        output logic usb_rst_l,

        //data going to peripheral
        output logic [31:0] data_o,
        output logic [3:0] o_valid, //what bytes of data are valid

        //data coming from peripheral
        input logic [31:0] data_i,
        input logic [3:0] i_valid, //what bytes of data are valid

        //ftdi data bus
        inout logic [31:0] data,
        inout logic [3:0] be //what bytes of data are valid
        //output logic be_ts,
        //output logic data_ts,


        // // 0 = input from data bus, 1 = outputting to data bus
        // output logic ft601_data_bus_dir,
        // // Whether valid data is coming from the arbiter
        // input logic periph_data_available,
        // // Allow peripherals to send data back to USB host
        // output logic read_periph_data
        // Whether valid data is coming from the arbiter
        input logic periph_data_available,
        // Whether we are currently reading data from the arbiter
        output logic read_periph_data
    );

    typedef enum logic[1:0] {
		       init,
		       read,
		       write
		       } state_t;

    state_t state_r, next_state;

    assign data = (!usb_wren_l) ? data_i : 32'bz; //if writing data bus is data in, otherwise tri
    assign be = (!usb_wren_l) ? 4'b1111 : 4'bz; //if writing BE is 1111 (temporary)

    always_ff @(posedge clk, posedge rst) 
     if (rst) state_r <= init;   
     else state_r <= next_state;

    always_comb begin
      
      case (state_r)
        init : begin
        usb_outen_l = 1'b1;
        usb_rden_l = 1'b1;
        usb_wren_l = 1'b1;

        if (!usb_rxf) next_state = read;
        else if (!usb_txe && usb_rxf) next_state = write;

        else next_state = init;	   
        end

        read : begin
        usb_outen_l = 1'b0;
        usb_rden_l = 1'b0;
        usb_wren_l = 1'b1;

        data_o = data;
        o_valid = be;

        if (usb_rxf && usb_txe) next_state = init;
        else if (usb_rxf && !usb_txe) next_state = write;

        else next_state = read;	   
        end

        write : begin
        usb_outen_l = 1'b1;
        usb_rden_l = 1'b1;
        usb_wren_l = 1'b0;

        //data bus taken care of above


        if (usb_rxf && usb_txe) next_state = init;
        else if (!usb_rxf) next_state = read;

        else next_state = write;	   
        end

      endcase      
   end

endmodule
