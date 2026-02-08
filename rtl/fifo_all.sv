`timescale 1ns/1ps

module async_fifo_top #(
    parameter DATA_WIDTH = 8,
    parameter ADDR_WIDTH = 4
)(
    input  logic                  w_clk, w_rst_n, w_inc,
    input  logic [DATA_WIDTH-1:0] w_data,
    output logic                  w_full,
    
    input  logic                  r_clk, r_rst_n, r_inc,
    output logic [DATA_WIDTH-1:0] r_data,
    output logic                  r_empty
);

    // --- Pointerlar ---
    logic [ADDR_WIDTH:0] w_bin, w_gray, w_bin_next, w_gray_next;
    logic [ADDR_WIDTH:0] r_bin, r_gray, r_bin_next, r_gray_next;
    logic [ADDR_WIDTH:0] w_q2_r_gray, r_q2_w_gray;

    localparam DEPTH = 1 << ADDR_WIDTH;
    logic [DATA_WIDTH-1:0] mem [0:DEPTH-1];

    // 1. Senkronizasyon (CDC)
    logic [ADDR_WIDTH:0] r_ptr_q1;
    always_ff @(posedge w_clk or negedge w_rst_n) begin
        if (!w_rst_n) {w_q2_r_gray, r_ptr_q1} <= '0;
        else          {w_q2_r_gray, r_ptr_q1} <= {r_ptr_q1, r_gray};
    end

    logic [ADDR_WIDTH:0] w_ptr_q1;
    always_ff @(posedge r_clk or negedge r_rst_n) begin
        if (!r_rst_n) {r_q2_w_gray, w_ptr_q1} <= '0;
        else          {r_q2_w_gray, w_ptr_q1} <= {w_ptr_q1, w_gray};
    end

    // 2. Yazma (Write)
    assign w_full = (w_gray == {~w_q2_r_gray[ADDR_WIDTH:ADDR_WIDTH-1], w_q2_r_gray[ADDR_WIDTH-2:0]});
    assign w_bin_next  = w_bin + (w_inc & ~w_full);
    assign w_gray_next = (w_bin_next >> 1) ^ w_bin_next;

    always_ff @(posedge w_clk or negedge w_rst_n) begin
        if (!w_rst_n) {w_bin, w_gray} <= '0;
        else          {w_bin, w_gray} <= {w_bin_next, w_gray_next};
    end

    always_ff @(posedge w_clk) begin
        if (w_inc && !w_full) mem[w_bin[ADDR_WIDTH-1:0]] <= w_data;
    end

    // 3. Okuma (Read)
    assign r_empty = (r_gray == r_q2_w_gray);
    assign r_bin_next  = r_bin + (r_inc & ~r_empty);
    assign r_gray_next = (r_bin_next >> 1) ^ r_bin_next;

    always_ff @(posedge r_clk or negedge r_rst_n) begin
        if (!r_rst_n) {r_bin, r_gray} <= '0;
        else          {r_bin, r_gray} <= {r_bin_next, r_gray_next};
    end

    // 4. Veri Çıkışı (Combinational - FWFT)
    // Veri her zaman "şu anki" pointer'ın gösterdiği adrestedir.
    assign r_data = mem[r_bin[ADDR_WIDTH-1:0]];

    initial begin
        $dumpfile("fifo_dump.vcd");
        $dumpvars(0, async_fifo_top);
    end
endmodule