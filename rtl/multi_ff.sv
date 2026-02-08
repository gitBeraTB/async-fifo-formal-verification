module multi_ff #(
    parameter WIDTH = 4
)(
    input  logic rst_n, // Asynchronous Negative Edge Trigger Reset
    input  logic clk, // CLK

    input  logic [WIDTH-1:0] IN_0, // Input - Output 
    output logic [WIDTH-1:0] OUT_1
);

    logic [WIDTH-1:0] OUT_0; // Input 1 

    // Multi-stage synchronizer (2 Flip-Flops) to prevent metastability [cite: 113]
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            OUT_0   <= '0;
            OUT_1 <= '0; // Reset
        end else begin
            OUT_0 <= IN_0;
            OUT_1 <= OUT_0; // IN0 to OUT0 , OUT0 to OUT1
        end
    end

endmodule