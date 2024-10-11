import asyncio
import struct
from bleak import BleakScanner, BleakClient
from bleak.backends.device import BLEDevice


U16 = 65_536
SLEEP_BEFORE_SUBSCRIBE = 5 # sec

GENERIC_SERVICE_UUID = "1801"
COEFFICIENT_CHAR_UUID = "2AE8"



async def discover_picos():
    devices = await BleakScanner.discover() # Scan for peripherials
    picos = []
    for d in devices:
        if d.name is not None and d.name.startswith("pico"): # Peripharial matches
            picos.append(d)
    return picos


async def handle_server(pico: BLEDevice, queue: asyncio.Queue):
    async with BleakClient(pico) as client:
        await client.read_gatt_char(COEFFICIENT_CHAR_UUID)
        await asyncio.sleep(SLEEP_BEFORE_SUBSCRIBE)
        while True:
            data = await client.read_gatt_char("2AE8")
            x, y, b = struct.unpack("<HHB", data)
            print(x, y, b)


async def main():
    picos = await discover_picos()
    if len(picos) == 0: raise Exception("Not a single pico found")
    if len(picos) > 6: raise Exception("Too many picos found")
    print(picos)

    queue = asyncio.Queue()
    await asyncio.gather(*[handle_server(pico, queue) for pico in picos])



if __name__ == "__main__":
    asyncio.run(main())