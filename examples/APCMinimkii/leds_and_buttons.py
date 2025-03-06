from akai_pro_py import controllers
from scipy.interpolate import interp1d
from rtmidi import MidiOut, MidiIn
from re import match


def get_midi_in(search) -> str:
    for port in MidiIn().get_ports():
        matching = match(search, port)
        if matching:
            return matching.group()


def get_midi_out(search) -> str:
    for port in MidiOut().get_ports():
        matching = match(search, port)
        if matching:
            return matching.group()


# Names may change for your system
# probe for them using rtmidi.MidiOut().get_ports()
# or rtmidi.MidiIn().get_ports()
apc = controllers.APCMinimkii(
    get_midi_in(r"^APC.*?Contr.*$"),
    get_midi_out(r"^APC.*?Contr.*$")
)
midi_mix = controllers.MIDIMix(
    get_midi_in(r"MIDI Mix.*?$"),
    get_midi_out(r"MIDI Mix.*?$")
)

apc.reset()  # turn off all leds
midi_mix.reset()  # reset midi_mix

# Creates a map from the 7 bit values of MIDI to a 3 bit value for display
midi_to_led = interp1d([0, 127], [0, 7])


# Defines this function for recieving button presses/fader changes
@apc.on_event
def on_control_event(event):
    # Checks if the event is a grid button press
    if isinstance(event, controllers.APCMinimkii.GridButton):
        if event.state:
            # Turn the button red when pressed
            apc.gridbuttons.set_led(event.x, event.y, "red", "bright")
            print("button " + str(event.x) + "x" + str(event.y) + " pressed")
        else:
            # and off when not pressed
            apc.gridbuttons.set_led(event.x, event.y, "off", 6)
            print("button released")
    elif isinstance(event, controllers.APCMinimkii.SideButton):
        if event.state:
            apc.sidebuttons.set_led(event.button_id, 2)
        else:
            apc.sidebuttons.set_led(event.button_id, 0)
    elif isinstance(event, controllers.APCMinimkii.LowerButton):
        if event.state:
            print("turn on on button " + str(event.button_id))
            apc.lowerbuttons.set_led(event.button_id, 1)
        else:
            print("turn off on button " + str(event.button_id))
            apc.lowerbuttons.set_led(event.button_id, 0)
    elif isinstance(event, controllers.APCMinimkii.ShiftButton):
        # apc.reset()
        apc.gridbuttons.reset_all_leds()
    elif isinstance(event, controllers.APCMinimkii.Fader):
        # Ignore fader ID 8 (the master fader)
        if event.fader_id == 8:
            return
        # Map the MIDI value (0,127) to 3 bit (0,7)
        value = int(midi_to_led(event.value))
        print(event.value)
        print(value)
        if event.value == 0:  # If the value is 0 (fader at minimum)
            for i in range(0, 8):
                # Set all LEDs in the column to off
                apc.gridbuttons.set_led(event.fader_id, i, "off", 0)
        else:
            # Go through all the LEDs that should be on
            for i in range(0, value + 1):
                # and set them to green
                if event.value == 127:
                    apc.gridbuttons.set_led(
                        event.fader_id, i, "green", "blink"
                    )
                else:
                    apc.gridbuttons.set_led(event.fader_id, i, "blue", "pulse")
            # Go through all the LEDs that should be off
            for i in range(value + 1, 8):
                # and set them to off
                apc.gridbuttons.set_led(event.fader_id, i, "off", 0)


@midi_mix.on_event
def on_event_midi_mix(event):
    print(event)
    if isinstance(event, controllers.MIDIMix.Knob):
        print(
            f"Knob {event.x},{event.y} was changed to "
            f"{event.value} on {event.controller.name}"
        )
    if isinstance(event, controllers.MIDIMix.Fader):
        print(
            f"Fader {event.fader_id} was changed to "
            f"{event.value} on {event.controller.name}"
        )
    if isinstance(event, controllers.MIDIMix.MuteButton):
        print(
            f"Mute Button {event.button_id} was changed "
            f"to {event.state} on {event.controller.name}"
        )
        if event.state:
            event.set_led("on")
        else:
            event.set_led("off")
    if isinstance(event, controllers.MIDIMix.RecArmButton):
        print(
            f"Record Arm Button {event.button_id} was changed "
            f"to {event.state} on {event.controller.name}"
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
            f"Bank Button {event.button_id} was changed to "
            f"{event.state} on {event.controller.name}"
        )
        if event.state:
            event.set_led("on")
        else:
            event.set_led("off")


if __name__ == "__main__":
    apc.start()
