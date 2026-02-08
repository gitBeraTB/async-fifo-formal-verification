`timescale 1ns/1ps

module multi_ff #(
    parameter WIDTH = 4
)(
    input  logic             clk,
    input  logic             rst_n,
    input  logic [WIDTH-1:0] din,
    output logic [WIDTH-1:0] dout
);

    logic [WIDTH-1:0] stage1;

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            stage1 <= '0;
            dout   <= '0;
        end else begin
            stage1 <= din;
            dout   <= stage1;
        end
    end

endmodule