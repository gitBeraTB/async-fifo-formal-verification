import os
from pathlib import Path
from cocotb_tools.runner import get_runner

def test_fifo():
    sim = os.getenv("SIM", "icarus")
    proj_path = Path(__file__).resolve().parent.parent
    
    # YENİ DOSYA LİSTESİ
    sources = [
        proj_path / "rtl" / "multi_ff.sv",
        proj_path / "rtl" / "w_ptr_full_flag.sv",
        proj_path / "rtl" / "r_ptr_empty_flag.sv",
        proj_path / "rtl" / "mem.sv",
        proj_path / "rtl" / "asynch_fifo_top.sv"
    ]

    runner = get_runner(sim)
    runner.build(
        verilog_sources=sources,
        hdl_toplevel="asynch_fifo_top",
        build_dir="sim_build",
        waves=True,
        build_args=["-g2012"]
    )

    runner.test(
        hdl_toplevel="asynch_fifo_top",
        test_module="test_fifo",
        test_dir=Path(__file__).parent,
        waves=True
    )

if __name__ == "__main__":
    test_fifo()