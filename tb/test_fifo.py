import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, Timer, Combine, ReadOnly
import random

class FifoTB:
    def __init__(self, dut):
        self.dut = dut
        self.expected_queue = []
        self.dut.w_inc.value = 0
        self.dut.r_inc.value = 0
        self.dut.w_data.value = 0
        self.dut.w_rst_n.value = 1
        self.dut.r_rst_n.value = 1

    async def reset_dut(self):
        self.dut.w_rst_n.value = 0
        self.dut.r_rst_n.value = 0
        await Timer(50, unit="ns")
        self.dut.w_rst_n.value = 1
        await Timer(20, unit="ns")
        self.dut.r_rst_n.value = 1
        self.expected_queue = []

# --- DEBUG MONITOR (Canlı Durum Takibi) ---
async def debug_monitor(dut):
    """FIFO'nun durumunu her 1000ns'de bir veya kilitlenince basar."""
    while True:
        await Timer(1000, unit="ns")
        # Sadece debugging gerekirse uncomment yapabilirsiniz
        # dut._log.info(f"[Monitor] W_Ptr: {dut.w_gray.value} R_Ptr: {dut.r_gray.value} Full: {dut.w_full.value} Empty: {dut.r_empty.value}")

async def producer(dut, tb, num_transactions=500, pressure_mode="random"):
    dut._log.info("Producer Başladı")
    write_count = 0
    
    # DÜZELTME: for döngüsü yerine while kullandık.
    # Sadece BAŞARILI yazma işleminden sonra sayacı artırıyoruz.
    while write_count < num_transactions:
        # Düşen kenarda hazırla
        await FallingEdge(dut.w_clk)
        
        if pressure_mode == "high": should_write = random.random() < 0.95
        elif pressure_mode == "low": should_write = random.random() < 0.10
        else: should_write = random.choice([True, False])

        # Eğer yazma kararı verdiysek VE FIFO dolu değilse
        if should_write and not dut.w_full.value:
            data = random.randint(0, 255)
            dut.w_data.value = data
            dut.w_inc.value = 1
            tb.expected_queue.append(data)
            
            write_count += 1 # Sadece başarılı yazmada artır
        else:
            # Doluysa veya yazmıyorsak sinyali indir
            dut.w_inc.value = 0
            # Döngü sayacı artmaz, aynı veriyi (veya yeni denemeyi) tekrar deneriz.
            
    # Bitiş temizliği
    await FallingEdge(dut.w_clk)
    dut.w_inc.value = 0
    dut._log.info("Producer Bitti")

async def consumer(dut, tb, num_transactions=500, pressure_mode="random"):
    dut._log.info("Consumer Başladı")
    read_count = 0
    timeout = 0
    
    while read_count < num_transactions:
        await FallingEdge(dut.r_clk)
        
        if pressure_mode == "high": should_read = random.random() < 0.95
        elif pressure_mode == "low": should_read = random.random() < 0.10
        else: should_read = random.choice([True, False])

        if should_read and not dut.r_empty.value:
            # 1. Veriyi Oku (FWFT - Pointer artmadan veri hazır)
            try:
                actual = int(dut.r_data.value)
            except ValueError:
                if len(tb.expected_queue) > 0:
                    dut._log.error(f"X Değeri! r_data: {dut.r_data.value}")
                    raise
                else: actual = 0

            # 2. Kontrol Et
            if tb.expected_queue:
                expected = tb.expected_queue.pop(0)
                assert actual == expected, f"VERİ HATASI! Beklenen: {expected}, Gelen: {actual} (İndex: {read_count})"
                read_count += 1
                timeout = 0
                
                # İlerleme Logu
                if read_count % 50 == 0:
                    dut._log.info(f"Consumer İlerleme: {read_count}/{num_transactions}")
            else:
                # Producer yavaşsa queue boş olabilir, normal.
                pass

            # 3. Onayla ve İlerlet (POP)
            dut.r_inc.value = 1
            await RisingEdge(dut.r_clk) # RTL işlesin
            dut.r_inc.value = 0 # Hemen düşür
            
        else:
            dut.r_inc.value = 0
            timeout += 1
            
        # Timeout süresini artırdık (Producer yavaş olabilir)
        if timeout > 100000:
             # Debug bilgisi vererek hata fırlat
             dut._log.error(f"TIMEOUT DEBUG INFO:")
             dut._log.error(f"  Target Reads: {num_transactions}, Actual: {read_count}")
             dut._log.error(f"  FIFO Empty Flag: {dut.r_empty.value}")
             dut._log.error(f"  FIFO Full Flag: {dut.w_full.value}")
             raise Exception(f"TIMEOUT! Okunan: {read_count}/{num_transactions}")
             
    dut._log.info("Consumer Bitti")

@cocotb.test()
async def test_random_traffic(dut):
    tb = FifoTB(dut)
    cocotb.start_soon(Clock(dut.w_clk, 10, unit="ns").start()) 
    cocotb.start_soon(Clock(dut.r_clk, 25, unit="ns").start()) 
    # Debug monitörünü başlat
    cocotb.start_soon(debug_monitor(dut))
    
    await tb.reset_dut()
    
    await Combine(
        cocotb.start_soon(producer(dut, tb, 200)),
        cocotb.start_soon(consumer(dut, tb, 200))
    )

@cocotb.test()
async def test_fifo_full(dut):
    tb = FifoTB(dut)
    cocotb.start_soon(Clock(dut.w_clk, 5, unit="ns").start()) 
    cocotb.start_soon(Clock(dut.r_clk, 20, unit="ns").start()) 
    await tb.reset_dut()
    
    await Combine(
        cocotb.start_soon(producer(dut, tb, 300, "high")), # Hızlı yaz
        cocotb.start_soon(consumer(dut, tb, 300, "low"))   # Yavaş oku (FIFO dolsun)
    )

@cocotb.test()
async def test_fifo_empty(dut):
    tb = FifoTB(dut)
    cocotb.start_soon(Clock(dut.w_clk, 50, unit="ns").start()) 
    cocotb.start_soon(Clock(dut.r_clk, 10, unit="ns").start()) 
    await tb.reset_dut()
    
    await Combine(
        cocotb.start_soon(producer(dut, tb, 100, "low")),  # Yavaş yaz
        cocotb.start_soon(consumer(dut, tb, 100, "high"))  # Hızlı oku (FIFO boşalsın)
    )