# Asynchronous FIFO with Cocotb Verification

## Overview
This project implements a robust **Asynchronous FIFO (First-In-First-Out)** memory buffer designed for safe data transfer between two different clock domains (CDC). The design is verified using **Cocotb** (Python-based verification) and **Icarus Verilog**.

## Key Features
* **Architecture:** Dual-clock domain support (Write Clock & Read Clock).
* **Safety:** Gray code pointer counters to prevent metastability during CDC.
* **Timing:** 2-stage Flip-Flop synchronizers for pointer exchange.
* **Mode:** FWFT (First-Word Fall-Through) logic / Combinational Output for low-latency access.
* **Verification:** Randomized constrained testing with Cocotb to cover corner cases (Full, Empty, Burst).

## Directory Structure
* `rtl/`: SystemVerilog source files.
* `tb/`: Python testbench (Cocotb) and runner scripts.

## Prerequisites
* Python 3.x
* Icarus Verilog (simulator)
* Cocotb (`pip install cocotb`)

## How to Run Tests
1.  Navigate to the testbench directory:
    ```bash
    cd tb
    ```
2.  Run the verification script:
    ```bash
    python run.py
    ```

## Simulation Results
The testbench validates 3 critical scenarios:
1.  **Random Traffic:** Mixed read/write operations with random delays.
2.  **Full Stress:** Verifies `w_full` flag assertion and data integrity under pressure.
3.  **Empty Stress:** Verifies `r_empty` flag and data stability during drain.

*Design follows Clifford Cummings' simulation-safe FIFO guidelines.*
