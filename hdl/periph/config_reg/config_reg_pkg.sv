package config_reg_pkg;
  typedef enum logic [2:0] {
    WHO_AM_I,
    NUM_DATA_BITS,
    STOP_BITS,
    PARITY,
    CLK_DIV_MAX
  } uart_config_t;
endpackage
