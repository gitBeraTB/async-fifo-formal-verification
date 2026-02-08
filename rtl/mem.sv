`timescale 1ns/1ps

module mem #(
    parameter DATA_WIDTH = 8,
    parameter ADDR_WIDTH = 4
)(
    input  logic                  w_clk,
    input  logic                  w_inc,
    input  logic                  w_full,
    input  logic [ADDR_WIDTH-1:0] w_addr,
    input  logic [DATA_WIDTH-1:0] w_data,
    
    input  logic                  r_clk,
    input  logic                  r_rst_n,
    input  logic                  r_inc,
    input  logic                  r_empty,
    input  logic [ADDR_WIDTH-1:0] r_addr,
    output logic [DATA_WIDTH-1:0] r_data
);

    localparam DEPTH = 1 << ADDR_WIDTH;
    logic [DATA_WIDTH-1:0] mem [0:DEPTH-1];

    // Yazma İşlemi (Senkron)
    always_ff @(posedge w_clk) begin
        if (w_inc && !w_full) 
            mem[w_addr] <= w_data;
    end

    // --- DÜZELTME BURADA ---
    // Okuma İşlemi (Kombinasyonel - FWFT)
    // Register yerine 'assign' kullanıyoruz.
    // Böylece r_addr değiştiği an veri çıkışta hazır olur.
    // Testbench FallingEdge'de okuduğunda doğru veriyi görür.
    assign r_data = mem[r_addr];

endmodule