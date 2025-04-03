package config_reg_pkg;
  typedef enum logic [2:0] {
    WHO_A_I,
    NUM_DATA_BITS,
    STOP_BITS,
    PARITY,
    RX_TX_RATIO
  } uart_config_t;
endpackage
