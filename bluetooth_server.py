from machine import Pin, ADC
import uasyncio as asyncio
import ustruct as struct
from bluetooth import UUID
import aioble


U16 = const(65_536)
ADVERTISE_INTERVAL = const(250_000) # millisec
DEVICE_NAME = "pico1"

BUTTON_SERVICE_UUID = UUID("00000001-0001-0000-0000-ABCABCABCDEF")
BUTTON_CHAR_UUID = UUID("00000002-0001-0000-0000-ABCABCABCDEF")
SENSOR_APPEARANCE = const(0x015)


btn0 = Pin(0, Pin.IN, Pin.PULL_UP) # Failsafe
led25 = Pin("LED", Pin.OUT) # Pico LED
btn20 = Pin(20, Pin.IN, Pin.PULL_UP) # Joystick Button
Pin(21, Pin.OUT).on() # Joystick +V
pot26 = ADC(Pin(26, Pin.IN)) # Joystick Y
pot27 = ADC(Pin(27, Pin.IN)) # Joystick X



# Profile delerations
joystick_service = aioble.Service(BUTTON_SERVICE_UUID)
joystick_char = aioble.Characteristic(joystick_service, BUTTON_CHAR_UUID, read=True, notify=True)

aioble.register_services(joystick_service)



def get_joystick_state():
    # d = joystick direction, 0 is center, then 1...8 are placed clockwise
    # b = is button pressed
    x = pot27.read_u16()
    y = pot26.read_u16()
    b = 1 - btn20.value()

    d = 0
    if x < U16//4 and y < U16//4: d = 8
    elif x < U16//4 and y < U16*3//4: d = 7
    elif x < U16//4: d = 6
    elif x < U16*3//4 and y < U16//4: d = 1
    elif x < U16*3//4 and y < U16*3//4: d = 0
    elif x < U16*3//4: d = 5
    elif y < U16//4: d = 2
    elif y < U16*3//4: d = 3
    else: d = 4

    return (d, b)


async def blink(n: int = 1, t: float = 0.1):
    for _ in range(n):
        led25.on()
        await asyncio.sleep(t/2)
        led25.off()
        await asyncio.sleep(t/2)


async def main():
    connection = await aioble.advertise(
        ADVERTISE_INTERVAL,
        name=DEVICE_NAME,
        services=[BUTTON_SERVICE_UUID],
        appearance=SENSOR_APPEARANCE
    )
    if connection is None: raise Exception("Connection bad")
    await blink(5, 0.1)

    prev_state = (0, 0)
    try:
        while True:
            curr_state = get_joystick_state()
            data = struct.pack("<BB", *curr_state) # {d}[uchar]{b}[uchar]
            print(data)
            joystick_char.write(data)
            if curr_state != prev_state:
                joystick_char.notify(connection, data)
                prev_state = curr_state
            await asyncio.sleep_ms(20)
    finally:
        await connection.disconnect()



if btn0.value() == 1: # Failsafe wire unattached
    asyncio.run(main())