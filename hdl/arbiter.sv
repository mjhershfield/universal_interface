module arbiter
    (
        // Control signals from local peripheral FIFOs
        input logic rx_fifo_empty[7:0],
        input logic rx_fifo_almost_empty[7:0],
        // If FT601 controller has set USB bus to send data to host
        input logic allow_rx, 
        // Number of peripheral that has control of the bus
        output logic grant[2:0],
        // Whether data is currently being sent to the FT601.
        output logic rx_valid
    );
    
endmodule
