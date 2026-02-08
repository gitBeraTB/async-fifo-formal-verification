`timescale 1ns/1ps

module w_ptr_full_flag #(
    parameter ADDR_WIDTH = 4
)(
    input  logic                  w_clk,
    input  logic                  w_rst_n,
    input  logic                  w_inc,
    input  logic [ADDR_WIDTH:0]   w_q2_r_ptr, // Read domain'den gelen senkronize pointer
    
    output logic                  w_full,
    output logic [ADDR_WIDTH-1:0] w_addr,     // Bellek adresi (Binary)
    output logic [ADDR_WIDTH:0]   w_ptr       // Gray kodlu pointer (CDC için)
);

    logic [ADDR_WIDTH:0] w_bin, w_bin_next, w_gray_next;

    // --- Yazma Mantığı ---
    assign w_bin_next  = w_bin + (w_inc & ~w_full);
    assign w_gray_next = (w_bin_next >> 1) ^ w_bin_next;

    // Full Bayrağı (Kombinasyonel - Current State Comparison)
    // MSB farklı, 2. MSB farklı, geri kalanı aynı olmalı
    assign w_full = (w_ptr == {~w_q2_r_ptr[ADDR_WIDTH:ADDR_WIDTH-1], w_q2_r_ptr[ADDR_WIDTH-2:0]});
    
    assign w_addr = w_bin[ADDR_WIDTH-1:0];

    always_ff @(posedge w_clk or negedge w_rst_n) begin
        if (!w_rst_n) begin
            w_bin <= '0;
            w_ptr <= '0;
        end else begin
            w_bin <= w_bin_next;
            w_ptr <= w_gray_next;
        end
    end

endmodule