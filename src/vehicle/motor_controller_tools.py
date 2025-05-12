import can

# can0 = can.interface.Bus(channel = 'can0', 
#                             bustype = 'socketcan',
#                             fd = True)
# can1 = can.interface.Bus(channel = 'can1', 
#                             bustype = 'socketcan',
#                             fd = True)



with can.Bus(interface='socketcan',
              channel='can0',
              receive_own_messages=False) as bus:

    # send a message
    message = can.Message(arbitration_id=123, is_extended_id=True,
                            data=[0x11, 0x22, 0x33])
    bus.send(message, timeout=0.2)

    # iterate over received messages
    for msg in bus:
        print(f"{msg.arbitration_id:X}: {msg.data}")

    # or use an asynchronous notifier
    notifier = can.Notifier(bus, [can.Logger("recorded.log"), can.Printer()])

