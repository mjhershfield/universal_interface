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
    output logic rd_data_valid,

    // USB DATA BUS
    // TODO: change data_i/o, i/o_valid to use usb_data_* outside of this module.
    // input logic [31:0] usb_data_in,
    // output logic [31:0] usb_data_out,
    output logic usb_data_tri,

    input logic [3:0] be_in,
    output logic [3:0] be_out,
    output logic be_tri,

    input logic lycan_in_full,
    input logic lycan_out_empty,
    // Whether peripheral FIFOs have been initialized
    input  logic periph_ready,

    output logic [1:0] state_r_out
);

  typedef enum logic [1:0] {
    init = 2'b00,
    init_read = 2'b01,
    read = 2'b10,
    write = 2'b11
  } state_t;

  state_t state_r;
  state_t next_state;

  always_ff @(posedge clk, posedge rst) begin
    if (rst) begin
      state_r <= init;
    end else  begin
      state_r <= next_state;
    end
  end

  always_comb begin

    usb_outen_l = 1'b1;
    usb_rden_l = 1'b1;
    usb_wren_l = 1'b1;
    next_state = state_r;
    data_o = '0;
    rd_data_valid = '0;

    unique case (state_r)
      init: begin
        if (!periph_ready) next_state = init;
        else if (!usb_rx_empty) next_state = init_read;
        else if (lycan_out_empty) next_state = init; //avoids being in write when there is no data to write
        else if (!usb_tx_full && usb_rx_empty) next_state = write;
      end

      init_read: begin
        next_state = read;
        usb_outen_l = 1'b0;
      end

      read: begin
        usb_outen_l = lycan_in_full; //avoids reading when ftdi to lycan fifo is full
        usb_rden_l = !(!lycan_in_full & !usb_rx_empty); //should go high one cycle after rx_empty goes high
        rd_data_valid = &be_in;

        // data_o = usb_data_in;
        // o_valid = usb_rx_empty ? 4'b0 : be_in;

        if (!periph_ready) next_state = init;
        else if (usb_rx_empty && usb_tx_full) next_state = init;
        else if (lycan_out_empty) next_state = init; //avoids being in write when there is no data to write
        else if (usb_rx_empty && !usb_tx_full) next_state = write;
      end

      write: begin
        usb_wren_l = lycan_out_empty;
        
        if (!periph_ready) next_state = init;
        else if (usb_rx_empty && usb_tx_full) next_state = init;
        else if (!usb_rx_empty) next_state = init_read;
        else if (lycan_out_empty) next_state = init; //avoids being in write when there is no data to write

      end
    endcase

    //if (!periph_ready) next_state = init;
  end

  assign usb_data_tri = ~usb_outen_l; //if writing, do not tristate, otherise tristate
  assign be_tri = ~usb_outen_l;  //if writing do not tri, otherwise tri
  assign be_out = ~usb_wren_l ? '1 : '0; //temporary, all data is valid

  assign usb_rst_l = ~rst;

  assign state_r_out = state_r; //test for debug

endmodule
