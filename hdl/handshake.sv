module handshake (
  input logic clk_wr,
  input logic rst_wr,
  input logic clk_rd,
  input logic rst_rd,
  input logic start,
  output logic read_it,
  output logic done
);

  // BEHAVIOR: put data on write side, pulse start for 1 cycle.
  // When synchronized, read_it will pulse for once cycle on the read domain
  // Finally, done will pulse for one cycle on the write side to indicate
  // we are ready for new data.

  logic p2t_src_r, sync1_src_r, sync2_src_r, t2p_src_r;
  logic p2t_dst_r, sync1_dst_r, sync2_dst_r, t2p_dst_r;

  // WRITE/SRC DOMAIN
  always_ff @(posedge clk_wr or posedge rst_wr) begin
    if (rst_wr) begin
      p2t_src_r <= 1'b0;
      sync1_src_r <= 1'b0;
      sync2_src_r <= 1'b0;
      t2p_src_r <= 1'b0;
    end else begin
      // Pulse to toggle circuit
      p2t_src_r <= start ? ~p2t_src_r : p2t_src_r;
      // Dual flop synchronizer
      sync1_src_r <= p2t_dst_r;
      sync2_src_r <= sync1_src_r;
      // Toggle to pulse circuit
      t2p_src_r <= sync2_src_r;
    end
  end

  assign done = t2p_src_r ^ sync2_src_r;

  // READ/DST DOMAIN
  always_ff @(posedge clk or posedge rst_rd) begin
    if (rst_rd) begin
      p2t_dst_r <= 1'b0;
      sync1_dst_r <= 1'b0;
      sync2_dst_r <= 1'b0;
      t2p_dst_r <= 1'b0;
    end else begin
      // Pulse to toggle circuit
      p2t_dst_r <= read_it ? ~p2t_dst_r : p2t_dst_r;
      // Dual flop synchronizer
      sync1_dst_r <= p2t_src_r;
      sync2_dst_r <= sync2_dst_r;
      // Toggle to pulse circuit
      t2p_dst_r <= sync2_dst_r;
    end
  end

  assign read_it = t2p_dst_r ^ sync2_dst_r;

endmodule
