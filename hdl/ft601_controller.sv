module ft601_controller (
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

    //data going to peripheral
    output logic [31:0] data_o,
    output logic [ 3:0] o_valid, //what bytes of data are valid

    //data coming from peripheral
    input logic [31:0] data_i,
    input logic [ 3:0] i_valid, //what bytes of data are valid

    //ftdi data bus
    inout logic [31:0] data,
    inout logic [ 3:0] be,    //what bytes of data are valid
    //output logic be_ts,
    //output logic data_ts,

    // Whether valid data is coming from the arbiter
    input  logic periph_data_available,
    // Whether peripheral FIFOs have been initialized
    input  logic periph_ready,
    // Whether we are currently reading data from the arbiter
    output logic read_periph_data
);

  typedef enum logic [1:0] {
    init,
    read,
    write
  } state_t;

  state_t state_r, next_state;

  always_ff @(posedge clk, posedge rst) begin
    if (rst) state_r <= init;
    else state_r <= next_state;
  end

  always_comb begin

    read_periph_data = '0;
    usb_outen_l = 1;
    usb_rden_l = 1;
    usb_wren_l = 1;
    next_state = state_r;
    data_o = '0;
    o_valid = 0;
    read_periph_data = '0;

    unique case (state_r)
      init: begin
        if (!usb_rx_empty) next_state = read;
        else if (!usb_tx_full && usb_rx_empty) next_state = write;
      end

      read: begin
        usb_outen_l = 1'b0;
        usb_rden_l = 1'b0;

        data_o = data;
        o_valid = be;

        if (usb_rx_empty && usb_tx_full) next_state = init;
        else if (usb_rx_empty && !usb_tx_full) next_state = write;
      end

      write: begin
        usb_wren_l = ~periph_data_available;

        // TODO: Poor assumption?
        read_periph_data = periph_data_available;

        if (usb_rx_empty && usb_tx_full) next_state = init;
        else if (!usb_rx_empty) next_state = read;
      end
    endcase

    if (!periph_ready) next_state = init;
  end

  assign data = (!usb_wren_l) ? data_i : {32{1'bz}};  //if writing data bus is data in, otherwise tri
  assign be = (!usb_wren_l) ? 4'b1111 : 4'bzzzz;  //if writing BE is 1111 (temporary)
  assign usb_rst_l = ~rst;

endmodule
