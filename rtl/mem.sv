module mem #(
    parameter DATA_WIDTH = 8,
    parameter ADDR_WIDTH = 4 // Param
)(
    input  logic w_clk, // Clk Write
    input  logic w_inc, // Write 
    input  logic w_full, // Write Full
    input  logic [ADDR_WIDTH-1:0] w_addr, // Write Address
    input  logic [DATA_WIDTH-1:0] w_data, // Write Data
    
    input  logic r_clk, // Read Clock 
    input  logic r_inc, // Read Sig
    input  logic r_empty, // Read Empty
    input  logic [ADDR_WIDTH-1:0] r_addr, // Read Address
    output logic [DATA_WIDTH-1:0] r_data // Read Data
);

    localparam DEPTH = 1 << ADDR_WIDTH; // Shift as the width
    logic [DATA_WIDTH-1:0] mem [0:DEPTH-1]; // Create mem

    always_ff @(posedge w_clk) begin
        if (w_inc && !w_full) begin
            mem[w_addr] <= w_data;
        end
    end

    assign r_data = mem[r_addr];  // Assign or Always

endmodule