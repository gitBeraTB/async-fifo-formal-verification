module r_ptr_empty_flag #(
    parameter ADDR_WIDTH = 4
)(
    input  logic                  r_clk,
    input  logic                  r_rst_n,
    input  logic                  r_inc,
    input  logic [ADDR_WIDTH:0]   r_q2_w_ptr,
    output logic                  r_empty,      // Artık register çıkışı
    output logic [ADDR_WIDTH-1:0] r_addr,
    output logic [ADDR_WIDTH:0]   r_ptr
);

    logic [ADDR_WIDTH:0] r_bin;
    logic [ADDR_WIDTH:0] r_graynext, r_binnext;
    logic r_empty_val; // Gelecek değeri tutan ara sinyal

    always_ff @(posedge r_clk or negedge r_rst_n) begin
        if (!r_rst_n) begin
            r_bin   <= '0;
            r_ptr   <= '0;
            r_empty <= 1'b1; // Reset anında FIFO BOŞTUR (1)
        end else begin
            r_bin   <= r_binnext;
            r_ptr   <= r_graynext;
            r_empty <= r_empty_val; // Döngüyü kıran kayıt işlemi
        end
    end

    assign r_addr = r_bin[ADDR_WIDTH-1:0];
    
    // Okuma mantığı: Eğer boş değilse artır
    assign r_binnext = r_bin + (r_inc & ~r_empty);
    
    // Binary -> Gray
    assign r_graynext = (r_binnext >> 1) ^ r_binnext;

    // Empty mantığı: Bir sonraki Gray kodu, yazma pointer'ına eşit mi?
    assign r_empty_val = (r_graynext == r_q2_w_ptr);

endmodule