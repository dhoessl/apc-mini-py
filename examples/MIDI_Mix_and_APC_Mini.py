from akai_pro_py import controllers
from scipy.interpolate import interp1d


# Define the MIDI Mix and APC Mini
# first argument: MIDI in
# second argument: MIDI out
midi_mix = controllers.MIDIMix('MIDI Mix MIDI 1', 'MIDI Mix MIDI 1')
apc = controllers.APCMini('APC MINI MIDI 1', 'APC MINI MIDI 1')

# Creates a map from the 7 bit values of MIDI to a 3 bit value for display
midi_to_led = interp1d([0, 127], [0, 7])

apc.reset()  # turn off all leds
midi_mix.reset()


@midi_mix.on_event
def on_event_midi_mix(event):
    if isinstance(event, controllers.MIDIMix.Knob):
        print(
            f"Knob {event.x},{event.y} was changed to {event.value} on "
            f"{event.controller.name}"
        )
    if isinstance(event, controllers.MIDIMix.Fader):
        print(
            f"Fader {event.fader_id} was changed to {event.value} on "
            f"{event.controller.name}"
        )
    if isinstance(event, controllers.MIDIMix.MuteButton):
        print(
            f"Mute Button {event.button_id} was changed to {event.state} "
            f"on {event.controller.name}"
        )
        if event.state:
            event.set_led("on")
        else:
            event.set_led("off")
    if isinstance(event, controllers.MIDIMix.RecArmButton):
        print(
            f"Record Arm Button {event.button_id} was changed to {event.state}"
            f" on {event.controller.name}"
        )
        if event.state:
            event.set_led("on")
        else:
            event.set_led("off")
    if isinstance(event, controllers.MIDIMix.SoloButton):
        print(
            f"Solo Button was changed to {event.state} on "
            f"{event.controller.name}"
        )
    if isinstance(event, controllers.MIDIMix.BankButton):
        print(
            f"Bank Button {event.button_id} was changed to {event.state} on "
            f"{event.controller.name}"
        )
        if event.state:
            event.set_led("on")
        else:
            event.set_led("off")


@apc.on_event
def on_event_apc_mini(event):  # Register event function
    # Checks if the event is a grid button press
    if isinstance(event, controllers.APCMini.GridButton):
        if event.state:
            # Turn the button red when pressed
            apc.gridbuttons.set_led(event.x, event.y, "red")
        else:
            # and off when not pressed
            apc.gridbuttons.set_led(event.x, event.y, "off")
    elif isinstance(event, controllers.APCMini.ShiftButton):
        apc.reset()
    elif isinstance(event, controllers.APCMini.Fader):
        if event.fader_id == 8:  # Ignore fader ID 8 (the master fader)
            return
        # Map the MIDI value (0,127) to 3 bit (0,7)
        value = int(midi_to_led(event.value))
        if value == 0:  # If the value is 0 (fader at minimum)
            for i in range(0, 8):
                # Set all LEDs in the column to off
                apc.gridbuttons.set_led(event.fader_id, i, "off")
        elif value == 7:  # If the value is 7 (fader at maximum)
            for i in range(0, 8):
                # Set all LEDs in column to green
                apc.gridbuttons.set_led(event.fader_id, i, "green")
        else:
            # Go through all the LEDs that should be on
            for i in range(0, value):
                # and set them to green
                apc.gridbuttons.set_led(event.fader_id, i, "green")
            # Go through all the LEDs that should be off
            for i in range(value+1, 8):
                # and set them to off
                apc.gridbuttons.set_led(event.fader_id, i, "off")


midi_mix.start()  # Start event loop
