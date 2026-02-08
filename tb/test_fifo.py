import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, Timer, Combine, ReadOnly
import random
import matplotlib.pyplot as plt # Grafik kütüphanesi eklendi

# --- VISUALIZATION HELPERS ---
class Colors:
    """ANSI Escape codes for colored terminal output."""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_banner(text):
    """Prints a styled ASCII banner."""
    print(f"\n{Colors.HEADER}{'='*60}")
    print(f"   🚀 {text}")
    print(f"{'='*60}{Colors.ENDC}")

def plot_results(test_name, time_data, fill_data):
    """
    TEST SONUNDA GRAFİK PENCERESİ AÇAR.
    Bu fonksiyon FIFO doluluk oranını zamanla gösteren bir grafik çizer.
    """
    try:
        plt.figure(figsize=(10, 5))
        plt.plot(time_data, fill_data, label='FIFO Scoreboard Level', color='blue', linewidth=1.5)
        plt.fill_between(time_data, fill_data, color='blue', alpha=0.1)
        
        plt.title(f"Test Analysis: {test_name}", fontsize=14, fontweight='bold')
        plt.xlabel("Simulation Time (ns)", fontsize=12)
        plt.ylabel("Items in FIFO (Count)", fontsize=12)
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.legend()
        
        # Kritik seviyeleri işaretle
        max_level = max(fill_data) if fill_data else 0
        plt.axhline(y=max_level, color='r', linestyle=':', label=f'Max Fill: {max_level}')
        plt.legend()

        print(f"{Colors.CYAN}[Graph] Opening performance window... (Close window to continue){Colors.ENDC}")
        plt.show() # Pencereyi açar ve kapatılana kadar bekler
    except Exception as e:
        print(f"{Colors.WARNING}Could not create plot: {e}{Colors.ENDC}")

# --- TESTBENCH CLASS ---
class FifoTB:
    def __init__(self, dut):
        self.dut = dut
        self.expected_queue = []
        # Monitor Data Containers
        self.history_time = []
        self.history_fill = []
        
        # Initialize signals
        self.dut.w_inc.value = 0
        self.dut.r_inc.value = 0
        self.dut.w_data.value = 0
        self.dut.w_rst_n.value = 1
        self.dut.r_rst_n.value = 1

    async def reset_dut(self):
        """Resets the DUT (Device Under Test)."""
        self.dut._log.info(f"{Colors.WARNING}⚡ Resetting DUT...{Colors.ENDC}")
        self.dut.w_rst_n.value = 0
        self.dut.r_rst_n.value = 0
        await Timer(50, unit="ns")
        self.dut.w_rst_n.value = 1
        await Timer(20, unit="ns")
        self.dut.r_rst_n.value = 1
        self.expected_queue = []
        self.history_time = [] # Reset history
        self.history_fill = []
        self.dut._log.info(f"{Colors.GREEN}✔ Reset Complete.{Colors.ENDC}")

# --- DATA MONITOR ---
async def performance_monitor(dut, tb):
    """
    Her 10ns'de bir FIFO doluluk oranını kaydeder.
    Bu veri test sonunda grafiğe dökülecektir.
    """
    while True:
        current_time = cocotb.utils.get_sim_time(units='ns')
        current_fill = len(tb.expected_queue)
        
        tb.history_time.append(current_time)
        tb.history_fill.append(current_fill)
        
        await Timer(10, unit="ns")

# --- PRODUCER ---
async def producer(dut, tb, num_transactions=500, pressure_mode="random"):
    dut._log.info(f"{Colors.BLUE}[Producer] Started (Mode: {pressure_mode}){Colors.ENDC}")
    write_count = 0
    
    while write_count < num_transactions:
        await FallingEdge(dut.w_clk)
        
        if pressure_mode == "high": should_write = random.random() < 0.95
        elif pressure_mode == "low": should_write = random.random() < 0.10
        else: should_write = random.choice([True, False])

        if should_write and not dut.w_full.value:
            data = random.randint(0, 255)
            dut.w_data.value = data
            dut.w_inc.value = 1
            tb.expected_queue.append(data)
            write_count += 1
        else:
            dut.w_inc.value = 0
            
    await FallingEdge(dut.w_clk)
    dut.w_inc.value = 0
    dut._log.info(f"{Colors.GREEN}[Producer] DONE. Sent {num_transactions} items.{Colors.ENDC}")

# --- CONSUMER ---
async def consumer(dut, tb, num_transactions=500, pressure_mode="random"):
    dut._log.info(f"{Colors.BLUE}[Consumer] Started (Mode: {pressure_mode}){Colors.ENDC}")
    read_count = 0
    timeout = 0
    
    while read_count < num_transactions:
        await FallingEdge(dut.r_clk)
        
        if pressure_mode == "high": should_read = random.random() < 0.95
        elif pressure_mode == "low": should_read = random.random() < 0.10
        else: should_read = random.choice([True, False])

        if should_read and not dut.r_empty.value:
            # 1. READ (FWFT)
            try:
                actual = int(dut.r_data.value)
            except ValueError:
                if len(tb.expected_queue) > 0:
                    dut._log.error(f"{Colors.FAIL}❌ X Value Detected!{Colors.ENDC}")
                    raise
                else: actual = 0

            # 2. VERIFY
            if tb.expected_queue:
                expected = tb.expected_queue.pop(0)
                assert actual == expected, \
                    f"{Colors.FAIL}MISMATCH! Exp: {expected}, Got: {actual}{Colors.ENDC}"
                
                read_count += 1
                timeout = 0
                
                # --- LIVE PROGRESS BAR ---
                if read_count % (num_transactions // 20) == 0 or read_count == num_transactions:
                    percent = (read_count / num_transactions) * 100
                    bar_len = 25
                    filled = int(bar_len * read_count // num_transactions)
                    bar = '█' * filled + '░' * (bar_len - filled)
                    dut._log.info(f"{Colors.CYAN}Progress: {bar} {percent:.1f}% ({read_count}/{num_transactions}){Colors.ENDC}")
            else:
                pass

            # 3. POP
            dut.r_inc.value = 1
            await RisingEdge(dut.r_clk)
            dut.r_inc.value = 0
        else:
            dut.r_inc.value = 0
            timeout += 1
            
        if timeout > 150000:
             raise Exception(f"{Colors.FAIL}TIMEOUT! Stuck at {read_count}/{num_transactions}{Colors.ENDC}")
             
    dut._log.info(f"{Colors.GREEN}[Consumer] DONE. Verified {num_transactions} items.{Colors.ENDC}")

# --- TESTS ---

@cocotb.test()
async def test_random_traffic(dut):
    """Test 1: Random Traffic Analysis"""
    print_banner("TEST 1: RANDOM TRAFFIC")
    tb = FifoTB(dut)
    
    cocotb.start_soon(Clock(dut.w_clk, 10, unit="ns").start()) 
    cocotb.start_soon(Clock(dut.r_clk, 25, unit="ns").start()) 
    cocotb.start_soon(performance_monitor(dut, tb)) # Start Data Recorder
    
    await tb.reset_dut()
    
    await Combine(
        cocotb.start_soon(producer(dut, tb, 200)),
        cocotb.start_soon(consumer(dut, tb, 200))
    )
    
    print_banner("✅ TEST 1 PASSED")
    # Show Graph Window
    plot_results("Random Traffic Pattern", tb.history_time, tb.history_fill)

@cocotb.test()
async def test_fifo_full(dut):
    """Test 2: Overflow Stress Analysis"""
    print_banner("TEST 2: FULL STRESS")
    tb = FifoTB(dut)
    
    cocotb.start_soon(Clock(dut.w_clk, 5, unit="ns").start())  # Fast Write
    cocotb.start_soon(Clock(dut.r_clk, 20, unit="ns").start()) # Slow Read
    cocotb.start_soon(performance_monitor(dut, tb))
    
    await tb.reset_dut()
    
    await Combine(
        cocotb.start_soon(producer(dut, tb, 300, "high")),
        cocotb.start_soon(consumer(dut, tb, 300, "low"))
    )
    
    print_banner("✅ TEST 2 PASSED")
    plot_results("Full Stress (Overflow Test)", tb.history_time, tb.history_fill)

@cocotb.test()
async def test_fifo_empty(dut):
    """Test 3: Underflow Stress Analysis"""
    print_banner("TEST 3: EMPTY STRESS")
    tb = FifoTB(dut)
    
    cocotb.start_soon(Clock(dut.w_clk, 50, unit="ns").start()) # Slow Write
    cocotb.start_soon(Clock(dut.r_clk, 10, unit="ns").start()) # Fast Read
    cocotb.start_soon(performance_monitor(dut, tb))
    
    await tb.reset_dut()
    
    await Combine(
        cocotb.start_soon(producer(dut, tb, 100, "low")),
        cocotb.start_soon(consumer(dut, tb, 100, "high"))
    )
    
    print_banner("✅ TEST 3 PASSED")
    plot_results("Empty Stress (Underflow Test)", tb.history_time, tb.history_fill)