//we do not care about the type of the variable here, can just store raw 24 bits per reg
//type conversion handled outside of this
module generic_config_regs #(
    parameter WIDTH = 32,
    parameter logic[23:0] reset_vals[0:7]
)(
    input logic clk,
    input logic rst,

    input logic [WIDTH-1:0] packet,
    input logic cfg_read_en, cfg_write_en,
    output logic [WIDTH-4:0] read_data,
    output logic valid,
    output logic [WIDTH-9:0] all_regs [8]
);

    //0-7 registers
    logic [WIDTH-9:0] zero_r;
    logic [WIDTH-9:0] one_r;
    logic [WIDTH-9:0] two_r;
    logic [WIDTH-9:0] three_r;
    logic [WIDTH-9:0] four_r;
    logic [WIDTH-9:0] five_r;
    logic [WIDTH-9:0] six_r;
    logic [WIDTH-9:0] seven_r;

    assign all_regs = '{zero_r, one_r, two_r, three_r, four_r, five_r, six_r, seven_r};

    always_ff @(posedge clk or posedge rst) begin
        if (rst) begin
          zero_r <= reset_vals[0];
          one_r <= reset_vals[1];
          two_r <= reset_vals[2];
          three_r <= reset_vals[3];
          four_r <= reset_vals[4];
          five_r <= reset_vals[5];
          six_r <= reset_vals[6];
          seven_r <= reset_vals[7];
        end else begin

            if (cfg_write_en) begin
                //we are writing
                unique case (packet[26:24])
                    3'b000: zero_r <= packet[23:0];
                    3'b001: one_r <= packet[23:0];
                    3'b010: two_r <= packet[23:0];
                    3'b011: three_r <= packet[23:0];
                    3'b100: four_r <= packet[23:0];
                    3'b101: five_r <= packet[23:0];
                    3'b110: six_r <= packet[23:0];
                    3'b111: seven_r <= packet[23:0];
                endcase

            end
        end
      end

    //make read_data comb so that it updates instantly
    always_comb begin

        valid = 1'b0;
        read_data = '0;

        if (cfg_read_en) begin
            unique case (packet[26:24])
                    3'b000: read_data = {2'b10, packet[26:24], zero_r};
                    3'b001: read_data = {2'b10, packet[26:24], one_r};
                    3'b010: read_data = {2'b10, packet[26:24], two_r};
                    3'b011: read_data = {2'b10, packet[26:24], three_r};
                    3'b100: read_data = {2'b10, packet[26:24], four_r};
                    3'b101: read_data = {2'b10, packet[26:24], five_r};
                    3'b110: read_data = {2'b10, packet[26:24], six_r};
                    3'b111: read_data = {2'b10, packet[26:24], seven_r};
                endcase

            valid = 1'b1;

        end

        if (rst == 1) begin
            valid = 1'b0;
        end

    end

endmodule