package lycan_globals;
  localparam int num_dut_pins = 16;
  localparam int width_dut_pins = $clog2(num_dut_pins);

  localparam int num_peripherals = 2; //for debug
  localparam int inputs_per_peripheral = 3;
  localparam int outputs_per_peripheral = 4;
  localparam int tristates_per_peripheral = 1;

  localparam int usb_packet_width = 32;
  localparam int periph_address_width = 3;//$clog2(num_peripherals); //for debug

  typedef enum logic [2:0] {
    PERIPH_LOOPBACK,
    PERIPH_UART,
    PERIPH_GPIO,
    PERIPH_SPI_M
  } periph_type_t;
endpackage
