package uart_pkg;
  typedef enum logic {
    STOP_BITS_1,
    STOP_BITS_2
  } stop_bits_t;

  typedef enum logic[1:0] {
    PARITY_NONE,
    PARITY_ODD,
    PARITY_EVEN
  } parity_t;
endpackage
