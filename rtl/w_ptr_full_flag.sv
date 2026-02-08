module w_ptr_full_flag #(
    parameter ADDR_WIDTH = 4
)(
    input  logic                  w_clk,
    input  logic                  w_rst_n,
    input  logic                  w_inc,
    input  logic [ADDR_WIDTH:0]   w_q2_r_ptr,
    output logic                  w_full,       // Artık register çıkışı
    output logic [ADDR_WIDTH-1:0] w_addr,
    output logic [ADDR_WIDTH:0]   w_ptr
);

    logic [ADDR_WIDTH:0] w_bin;
    logic [ADDR_WIDTH:0] w_graynext, w_bin_next;
    logic w_full_val; // Gelecek değeri tutan ara sinyal

    always_ff @(posedge w_clk or negedge w_rst_n) begin
        if (!w_rst_n) begin
            w_bin  <= '0;
            w_ptr  <= '0;
            w_full <= 1'b0; // Reset anında FIFO DOLU DEĞİLDİR (0)
        end else begin
            w_bin  <= w_bin_next;
            w_ptr  <= w_graynext;
            w_full <= w_full_val; // Döngüyü kıran kayıt işlemi
        end
    end

    assign w_addr = w_bin[ADDR_WIDTH-1:0];
    
    // Yazma mantığı: Eğer dolu değilse artır
    assign w_bin_next = w_bin + (w_inc & ~w_full);
    
    // Binary -> Gray
    assign w_graynext = (w_bin_next >> 1) ^ w_bin_next;

    // Full mantığı
    assign w_full_val = (w_graynext == {~w_q2_r_ptr[ADDR_WIDTH:ADDR_WIDTH-1], w_q2_r_ptr[ADDR_WIDTH-2:0]});

endmodule