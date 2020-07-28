import time as t
import machine


def readKeyPress():
    KeyPad = [['1', '2', '3'],
              ['4', '5', '6'],
              ['7', '8', '9'],
              ['*', '0', '#']]

    RowPins = [33, 25, 26, 27]
    ColumnPins = [14, 13, 12]

    for pin in ColumnPins:
        machine.Pin(pin, machine.Pin.OUT)
        machine.Pin(pin, value=1)

    for pin in RowPins:
        machine.Pin(pin, machine.Pin.IN, machine.Pin.PULL_UP)

    try:
        while True:
            for ColPin in range(len(ColumnPins)):
                machine.Pin(ColumnPins[ColPin], value=0)

                for RowPin in range(len(RowPins)):
                    if machine.Pin(RowPins[RowPin]).value() == 0:
                        t.sleep(0.2)
                        return KeyPad[RowPin][ColPin]
                        while(machine.Pin(RowPins[RowPin]).value() == 0):
                            pass

                machine.Pin(ColumnPins[ColPin], value=1)

    except KeyboardInterrupt:
        pass
