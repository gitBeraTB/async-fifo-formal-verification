`timescale 1ns/1ps

module asynch_fifo_top #(
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

    // Ara Bağlantı Sinyalleri
    logic [ADDR_WIDTH-1:0] w_addr, r_addr;
    logic [ADDR_WIDTH:0]   w_ptr, r_ptr;
    logic [ADDR_WIDTH:0]   w_q2_r_ptr, r_q2_w_ptr;

    // 1. Senkronizasyon (Read Ptr -> Write Domain)
    multi_ff #(.WIDTH(ADDR_WIDTH+1)) sync_r2w (
        .clk(w_clk), .rst_n(w_rst_n), 
        .din(r_ptr), .dout(w_q2_r_ptr)
    );

    // 2. Senkronizasyon (Write Ptr -> Read Domain)
    multi_ff #(.WIDTH(ADDR_WIDTH+1)) sync_w2r (
        .clk(r_clk), .rst_n(r_rst_n), 
        .din(w_ptr), .dout(r_q2_w_ptr)
    );

    // 3. Yazma Kontrol
    w_ptr_full_flag #(.ADDR_WIDTH(ADDR_WIDTH)) w_logic (
        .w_clk(w_clk), .w_rst_n(w_rst_n), .w_inc(w_inc),
        .w_q2_r_ptr(w_q2_r_ptr), 
        .w_full(w_full), .w_addr(w_addr), .w_ptr(w_ptr)
    );

    // 4. Okuma Kontrol
    r_ptr_empty_flag #(.ADDR_WIDTH(ADDR_WIDTH)) r_logic (
        .r_clk(r_clk), .r_rst_n(r_rst_n), .r_inc(r_inc),
        .r_q2_w_ptr(r_q2_w_ptr),
        .r_empty(r_empty), .r_addr(r_addr), .r_ptr(r_ptr)
    );

    // 5. Bellek
    mem #(.DATA_WIDTH(DATA_WIDTH), .ADDR_WIDTH(ADDR_WIDTH)) memory (
        .w_clk(w_clk), .w_inc(w_inc), .w_full(w_full), .w_addr(w_addr), .w_data(w_data),
        .r_clk(r_clk), .r_rst_n(r_rst_n), .r_inc(r_inc), .r_empty(r_empty), .r_addr(r_addr), .r_data(r_data)
    );

    // Waveform Dump
    initial begin
        $dumpfile("fifo_dump.vcd");
        $dumpvars(0, asynch_fifo_top);
    end

endmodule