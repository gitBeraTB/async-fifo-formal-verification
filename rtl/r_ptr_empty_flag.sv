`timescale 1ns/1ps

module r_ptr_empty_flag #(
    parameter ADDR_WIDTH = 4
)(
    input  logic                  r_clk,
    input  logic                  r_rst_n,
    input  logic                  r_inc,
    input  logic [ADDR_WIDTH:0]   r_q2_w_ptr, // Write domain'den gelen senkronize pointer
    
    output logic                  r_empty,
    output logic [ADDR_WIDTH-1:0] r_addr,     // Bellek adresi (Binary)
    output logic [ADDR_WIDTH:0]   r_ptr       // Gray kodlu pointer (CDC için)
);

    logic [ADDR_WIDTH:0] r_bin, r_bin_next, r_gray_next;

    // --- Okuma Mantığı ---
    assign r_bin_next  = r_bin + (r_inc & ~r_empty);
    assign r_gray_next = (r_bin_next >> 1) ^ r_bin_next;

    // Empty Bayrağı (Kombinasyonel - Current State Comparison)
    // Pointerlar birebir aynıysa boştur
    assign r_empty = (r_ptr == r_q2_w_ptr);
    
    assign r_addr = r_bin[ADDR_WIDTH-1:0];

    always_ff @(posedge r_clk or negedge r_rst_n) begin
        if (!r_rst_n) begin
            r_bin <= '0;
            r_ptr <= '0;
        end else begin
            r_bin <= r_bin_next;
            r_ptr <= r_gray_next;
        end
    end

endmodule