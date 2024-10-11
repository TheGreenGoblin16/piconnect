import asyncio
import struct
from bleak import BleakScanner, BleakClient
from bleak.backends.device import BLEDevice


U16 = 65_536
SLEEP_BETWEEN_LIFECHECK = 2 # sec

BUTTON_SERVICE_UUID = "00000001-0001-0000-0000-ABCABCABCDEF"
BUTTON_CHAR_UUID = "00000002-0001-0000-0000-ABCABCABCDEF"



async def discover_picos():
    devices = await BleakScanner.discover() # Scan for peripherials
    picos = []
    for d in devices:
        if d.name is not None and d.name.startswith("pico"): # Peripharial matches
            picos.append(d)
    return picos


async def handle_notification(char, data: bytearray):
    d, b = struct.unpack("<BB", data)
    print(d, b)


async def handle_server(pico: BLEDevice, queue: asyncio.Queue):
    async with BleakClient(pico) as client:
        await client.start_notify(BUTTON_CHAR_UUID, handle_notification)
        print(f"Listening to {pico.name}")
        while True:
            await client.read_gatt_char(BUTTON_CHAR_UUID)
            await asyncio.sleep(SLEEP_BETWEEN_LIFECHECK)
    return


async def main():
    picos = await discover_picos()
    if len(picos) == 0: raise Exception("Not a single pico found")
    if len(picos) > 6: raise Exception("Too many picos found")
    print(picos)

    queue = asyncio.Queue()
    await asyncio.gather(*[handle_server(pico, queue) for pico in picos])



if __name__ == "__main__":
    asyncio.run(main())