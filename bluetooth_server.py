from machine import Pin, ADC
import uasyncio as asyncio
import ustruct as struct
from bluetooth import UUID
import aioble


U16 = const(65_536)
ADVERTISE_INTERVAL = const(250_000) # millisec

GENERIC_SERVICE_UUID = UUID(0x1801)
COEFFICIENT_CHAR_UUID = UUID(0x2AE8)
SENSOR_APPEARANCE = const(0x015)


btn0 = Pin(0, Pin.IN, Pin.PULL_UP) # Failsafe
led25 = Pin("LED", Pin.OUT) # Pico LED
btn20 = Pin(20, Pin.IN, Pin.PULL_UP) # Joystick Button
Pin(21, Pin.OUT).on() # Joystick +V
pot26 = ADC(Pin(26, Pin.IN)) # Joystick Y
pot27 = ADC(Pin(27, Pin.IN)) # Joystick X



# Profile delerations
button_service = aioble.Service(GENERIC_SERVICE_UUID)
button_char = aioble.Characteristic(button_service, COEFFICIENT_CHAR_UUID, read=True, initial="707")

aioble.register_services(button_service)



async def blink(n: int = 1, t: float = 0.1):
    for _ in range(n):
        led25.on()
        await asyncio.sleep(t/2)
        led25.off()
        await asyncio.sleep(t/2)


async def main():
    connection = await aioble.advertise( # Advertise itself as "pico1"
        ADVERTISE_INTERVAL,
        name="pico1",
        services=[GENERIC_SERVICE_UUID],
        appearance=SENSOR_APPEARANCE
    )
    if connection is None: raise Exception("Connection bad")
    print(connection.device)
    await blink(5, 0.1)

    for _ in range(1000):
        data = (pot27.read_u16(), pot26.read_u16(), 1 - btn20.value())
        data = struct.pack("<HHB", *data) # {x}[ushort]{y}[ushort]{b}[uchar]
        button_char.write(data)
        await asyncio.sleep_ms(200)
    
    await connection.disconnect()
    return



if btn0.value() == 1: # Failsafe wire unattached
    asyncio.run(main())