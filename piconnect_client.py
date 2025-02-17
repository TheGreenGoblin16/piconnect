import asyncio
import struct
import queue
from functools import partial
from bleak import BleakScanner, BleakClient
from bleak.backends.device import BLEDevice
from bleak.backends.characteristic import BleakGATTCharacteristic


U16 = 65_536
SLEEP_BETWEEN_LIFECHECKS = 2 # sec

BUTTON_SERVICE_UUID = "00001336-0001-0000-0000-ABCABCABCDEF"
BUTTON_CHAR_UUID = "00001336-0001-0001-0000-ABCABCABCDEF"



class PiconnectEvent():
    def __init__(self, name: str, d: int, b: int):
        self.name: str = name
        self.d: int = d
        self.b: int = b



class PiconnectClient():
    def __init__(self):
        self.picos: list[BLEDevice] = []
        self.queue: queue.Queue = queue.Queue()
    

    async def discover_picos(self):
        devices = await BleakScanner.discover() # Scan for peripherials
        for device in devices:
            if device.name is not None and device.name.startswith("pico"): # Peripharial matches
                self.picos.append(device)
        return
    

    async def notification_callback(self, name: str, char: BleakGATTCharacteristic, data: bytearray):
        d, b = struct.unpack("<BB", data)
        self.queue.put(PiconnectEvent(name, d, b))
        return
    

    async def handle_server(self, pico: BLEDevice):
        name = str(pico.name)
        async with BleakClient(pico) as client:
            await client.start_notify(BUTTON_CHAR_UUID, partial(self.notification_callback, name))
            print(f"Listening to {pico.name}")
            while True:
                await client.read_gatt_char(BUTTON_CHAR_UUID)
                await asyncio.sleep(SLEEP_BETWEEN_LIFECHECKS)
        return
    

    async def initiate(self):
        await self.discover_picos()
        if len(self.picos) == 0: raise Exception("Not a single pico found")
        if len(self.picos) > 6: raise Exception("Too many picos found")
    
        await asyncio.gather(*[self.handle_server(pico) for pico in self.picos])
    

    def run(self):
        asyncio.run(self.initiate())


    def drain_queue(self) -> list[PiconnectEvent]:
        elements = []
        while self.queue.qsize() > 0: # Probably not risky because all of this is in the same thread
            elements.append(self.queue.get())
        return elements
