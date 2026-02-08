# --- Cocotb Makefile for Async FIFO Verification ---

# Simulator selection (Vivado's xsim)
SIM ?= xsim
TOPLEVEL_LANG ?= verilog

# RTL Sources
# Note: Ensure these file names match your actual filenames exactly.
VERILOG_SOURCES += $(PWD)/../rtl/multi_ff.sv
VERILOG_SOURCES += $(PWD)/../rtl/mem.sv
VERILOG_SOURCES += $(PWD)/../rtl/r_ptr_empty_flag.sv
VERILOG_SOURCES += $(PWD)/../rtl/w_ptr_full_flag.sv
VERILOG_SOURCES += $(PWD)/../rtl/asynch_fifo_top.sv

# Top-level module name in your Verilog
TOPLEVEL = asynch_fifo_top

# Python test script name (without .py extension)
MODULE = test_fifo

# Cocotb configuration
include $(shell cocotb-config --makefiles)/Makefile.sim

# Clean target to remove simulation artifacts
clean_all:
	rm -rf sim_build/
	rm -f results.xml
	rm -f *.jou *.log *.pb