package config_reg_pkg;
  typedef enum logic [2:0] {
    WHO_AM_I = 0,
    NUM_DATA_BITS = 1,
    STOP_BITS = 2,
    PARITY = 3,
    CLK_DIV_MAX = 4
  } uart_config_t;

  typedef enum logic[2:0] {
    GPIO_CONFIG_WHOAMI = 0,
    GPIO_CONFIG_ENABLE = 1,
    GPIO_CONFIG_SAMPLE_RATE = 2
  } gpio_config_t;
endpackage