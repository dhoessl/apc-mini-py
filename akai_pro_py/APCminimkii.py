from .base_controller import Controller
import mido
import time

from . import errors
from .logger import setup_logger

logger = setup_logger(__name__)


class InvalidGridButton(errors.ControllerError):
    def __init__(self, *args):
        if args:
            self.controller = args[0]
            self.midi_port = args[1]
            if isinstance(args[2], tuple):
                self.x, self.y = args[2]
                self.button_id = None
            else:
                self.x, self.y = (None, None)
                self.button_id = args[2]
        else:
            self.controller = None
            self.midi_port = None
            self.x, self.y = (None, None)

    def __str__(self):
        if self.controller and self.midi_port and self.x and self.y:
            msg = f"Grid Button {self.x},{self.y} does not exist on " \
                   f"controller {self.controller.name}, MIDI port: " \
                   f"{self.midi_port.name}"
            logger.error(msg)
            return msg
        elif self.controller and self.midi_port and self.button_id:
            msg = f"Grid Button {self.button_id} does not exist on " \
                    f"controller {self.controller.name}, MIDI port: " \
                    f"{self.midi_port.name}"
            logger.error(msg)
            return msg

        elif not self.controller and not self.midi_port and self.x and self.y:
            msg = f"Grid Button {self.x},{self.y} does not exist on " \
                    f"controller"
            logger.error(msg)
            return msg

        elif not self.controller and not self.midi_port and self.button_id:
            msg = f"Grid Button {self.button_id} does not exist on controller"
            logger.error(msg)
            return msg

        else:
            msg = "Generic invalid Grid Button error"
            logger.error(msg)
            return msg


class InvalidFader(errors.ControllerError):
    def __init__(self, *args):
        if args:
            self.controller = args[0]
            self.midi_port = args[1]
            self.fader_id = args[2]
        else:
            self.controller = None
            self.midi_port = None
            self.fader_id = None

    def __str__(self):
        if self.controller and self.midi_port and self.fader_id:
            return f"Fader {self.fader_id} does not exist on controller " \
                    f"{self.controller.name}, MIDI port: {self.midi_port.name}"

        elif not self.controller and not self.midi_port and self.button_id:
            return f"Fader {self.fader_id} does not exist on controller"

        else:
            return "Generic invalid Fader error"


class InvalidLowerButton(errors.ControllerError):
    def __init__(self, *args):
        if args:
            self.controller = args[0]
            self.midi_port = args[1]
            self.button_id = args[2]
        else:
            self.controller = None
            self.midi_port = None
            self.button_id = None

    def __str__(self):
        if self.controller and self.midi_port and self.button_id:
            return f"Lower Button button {self.button_id} does not exist on " \
                    f"controller {self.controller.name}, MIDI port: " \
                    f"{self.midi_port.name}"

        elif not self.controller and not self.midi_port and self.button_id:
            return f"Lower Button button {self.button_id} does not exist on " \
                    f"controller"

        else:
            return "Generic invalid Lower Button button error"


class InvalidSideButton(errors.ControllerError):
    def __init__(self, *args):
        if args:
            self.controller = args[0]
            self.midi_port = args[1]
            self.button_id = args[2]
        else:
            self.controller = None
            self.midi_port = None
            self.button_id = None

    def __str__(self):
        if self.controller and self.midi_port and self.button_id:
            return f"Side Button button {self.button_id} does not exist on" \
                    f"controller {self.controller.name}, MIDI port: " \
                    f"{self.midi_port.name}"

        elif not self.controller and not self.midi_port and self.button_id:
            return f"Side Button button {self.button_id} does not exist on " \
                    f"controller"

        else:
            return "Generic invalid Side Button button error"


class InvalidButtonColour(errors.ControllerError):
    def __init__(self, *args):
        if args:
            self.controller = args[0]
            self.midi_port = args[1]
            self.button = args[2]
        else:
            self.controller = None
            self.midi_port = None
            self.button = None

    def __str__(self):
        if isinstance(self.button, APCMinimkii.GridButton):
            return "Invalid button colour for Grid buttons, valid options " \
                    "are 0-127," + ",".join(APCMinimkii.GridColours.keys())

        elif isinstance(self.button, APCMinimkii.LowerButton):
            return "Invalid button colour for Lower button, valid options " \
                    "are 0-127," \
                    + ",".join(APCMinimkii.LowerButtonColours.keys())

        elif isinstance(self.button, APCMinimkii.SideButton):
            return "Invalid button colour for Side button, valid options " \
                    "are 0-127," \
                    + ",".join(APCMinimkii.LowerButtonColours.keys())

        else:
            return "Generic invalid button colour error"


class InvalidButtonEffect(errors.ControllerError):
    def __init__(self, *args):
        if args:
            self.controller = args[0]
            self.midi_port = args[1]
            self.button = args[2]
        else:
            self.controller = None
            self.midi_port = None
            self.button = None

    def __str__(self):
        if isinstance(self.button, APCMinimkii.GridButton):
            return "Invalid button colour for Grid buttons, valid options " \
                    + ",".join(APCMinimkii.GridEffects.keys()) + "," \
                    + ",".join(str(x) for x in range(18))

        else:
            return "Generic invalid button colour error"


class APCMinimkii(Controller):
    GridMapping = [
        [0, 8, 16, 24, 32, 40, 48, 56],
        [1, 9, 17, 25, 33, 41, 49, 57],
        [2, 10, 18, 26, 34, 42, 50, 58],
        [3, 11, 19, 27, 35, 43, 51, 59],
        [4, 12, 20, 28, 36, 44, 52, 60],
        [5, 13, 21, 29, 37, 45, 53, 61],
        [6, 14, 22, 30, 38, 46, 54, 62],
        [7, 15, 23, 31, 39, 47, 55, 63]
    ]  # The mapping of an XY coordinate to the MIDI note for the button grid

    GridColours = {
        "off": 0,
        "white": 3,
        "red": 5,
        "orange": 9,
        "yellow": 13,
        "green": 17,
        "lime": 21,
        "lime2": 25,
        "aqua green": 29,
        "cyan": 33,
        "sky blue": 36,
        "blue": 37,
        "blue2": 41,
        "blue3": 45,
        "magenta": 53,
        "pink": 57,
        "vivid green": 73
    }  # Dict of all available colours for the grid

    GridEffects = {
        "brightness_10": 0,
        "brightness_25": 1,
        "brightness_50": 2,
        "brightness_65": 3,
        "brightness_75": 4,
        "brightness_90": 5,
        "brightness_100": 6,
        "bright": 6,
        "dimm": 2,
        "pulse_1_16": 7,
        "pulse_1_8": 8,
        "pulse_1_4": 9,
        "pulse_1_2": 10,
        "pulse": 10,
        "blink_1_24": 11,
        "blink_1_16": 12,
        "blink_1_8": 13,
        "blink_1_4": 14,
        "blink_1_2": 15,
        "blink": 15
    }  # Channel Values for colour effects on the grid

    # Mapping of faders to their number indexed from 0
    FaderMapping = [48, 49, 50, 51, 52, 53, 54, 55, 56]

    # Mapping of side buttons from top to bottom, indexed from 0
    SideButtonMapping = [112, 113, 114, 115, 116, 117, 118, 119]

    SideButtonColours = {
        "on": 1,
        "off": 0,
        "green": 1,
        "green_blinking": 2
    }  # Dict of all colours for the side buttons

    # Mapping of lower buttons from left to right, indexed from 0
    LowerButtonMapping = [100, 101, 102, 103, 104, 105, 106, 107]

    LowerButtonColours = {
        "on": 1,
        "off": 0,
        "red": 1,
        "red_blinking": 2
    }  # Dict of all colours for the lower buttons

    ShiftButtonMapping = [122]

    def __init__(self, midi_in=None, midi_out=None):
        super().__init__(midi_in, midi_out)
        self.name = "Akai APC Mini MK 2"  # Name of the device
        self.gridbuttons = APCMinimkii.GridButtons(self)
        self.sidebuttons = APCMinimkii.SideButtons(self)
        self.lowerbuttons = APCMinimkii.LowerButtons(self)

    def reset(self, fast=False):
        """Turns off all LEDs"""
        # Build range
        all_leds = [int(x) for x in range(64)]
        all_leds += APCMinimkii.SideButtonMapping
        all_leds += APCMinimkii.LowerButtonMapping
        for i in all_leds:
            self.midi_out.send(mido.Message("note_on", note=i, velocity=0))
            if not fast:
                time.sleep(0.005)

    def product_detect(self, event):
        try:
            if event.data[2] != 6:
                raise errors.ControllerIdentificationError(
                    self, self.midi_in, "Controller did not identify!"
                )

            if event.data[4] != 71:
                raise errors.ControllerIdentificationError(
                    "MIDI device is not an Akai device!"
                )

            if event.data[5] != 79:
                raise errors.ControllerIdentificationError(
                    "MIDI device is not an Akai APC Mini"
                )
        except (AttributeError, IndexError):
            raise errors.ControllerIdentificationError(
                self, self.midi_in, "MIDI device failed to identify"
            )
        self.setup_in_progress = False
        return True

    def pre_event_dispatch(self, event):
        if self.event_dispatch is None:
            # Ignore if a dispatch event is not set with the on_event decorator
            return

        if event.type == "control_change":  # Event is a fader change
            fader = APCMinimkii.Fader(
                self,
                APCMinimkii.Fader.get_fader_id_from_number(event.control),
                event.value
            )
            self.event_dispatch(fader)

        elif event.type == "note_on" or event.type == "note_off":
            # Event is a button press
            state = True
            if event.note in range(64):  # Button grid
                if event.type == 'note_off':
                    state = False
                button = APCMinimkii.GridButton(
                    self,
                    *APCMinimkii.GridButton.get_xy_from_button_num(event.note),
                    state
                )
                self.event_dispatch(button)

            elif event.note in APCMinimkii.SideButtonMapping:  # Side buttons
                if event.type == 'note_off':
                    state = False
                button = APCMinimkii.SideButton(
                    self,
                    APCMinimkii.SideButton.get_button_id_from_button_num(event.note),  # noqa: E501
                    state
                )
                self.event_dispatch(button)

            elif event.note in APCMinimkii.LowerButtonMapping:  # Lower buttons
                if event.type == 'note_off':
                    state = False
                button = APCMinimkii.LowerButton(
                    self,
                    APCMinimkii.LowerButton.get_button_id_from_button_num(event.note),  # noqa: E501
                    state
                )
                self.event_dispatch(button)

            elif event.note in APCMinimkii.ShiftButtonMapping:
                if event.type == 'note_off':
                    state = False
                button = APCMinimkii.ShiftButton(self, state)
                self.event_dispatch(button)

    class GridButtons:  # All the grid buttons
        def __init__(self, controller):
            self.controller = controller

        def set_led(self, x, y, colour, effect):
            """Sets an LED on the button grid"""
            APCMinimkii.GridButton(self.controller, x, y).set_led(colour, effect)  # noqa: E501

        def reset_led(self, x, y):
            """ Turns of an LED on the button grid """
            APCMinimkii.GridButton(self.controller, x, y).set_led(0, 0)  # noqa: E501

        def reset_all_leds(self):
            for button in range(64):
                self.controller.midi_out.send(
                    mido.Message("note_on", note=button, velocity=0)
                )

    class GridButton:  # A specific grid button
        def __init__(self, controller, x: int, y: int, state: bool = False):
            self.controller = controller
            self.x = x
            self.y = y
            self.state = state

        @staticmethod
        def get_xy_from_button_num(button_num):
            for column in APCMinimkii.GridMapping:
                x = APCMinimkii.GridMapping.index(column)
                if button_num in column:
                    return x, APCMinimkii.GridMapping[x].index(button_num)
                else:
                    continue
            raise InvalidGridButton(None, None, button_num)

        def set_led(self, colour, effect):
            """Sets this specific button's LED to be the colour given"""
            if not isinstance(colour, int):
                # if colour is given as string check APCMinimkii.GridColours
                # for the string and set the correct value
                if colour not in APCMinimkii.GridColours:
                    raise InvalidButtonColour(
                        self.controller,
                        self.controller.midi_in,
                        self
                    )
                colour = APCMinimkii.GridColours[colour]
            if not isinstance(effect, int):
                # if effect is given as string check APCMinimkii.GridEffects
                # for the string and set the correct value
                if effect not in APCMinimkii.GridEffects:
                    raise InvalidButtonEffect(
                        self.controller,
                        self.controller.midi_in,
                        self
                    )
                effect = APCMinimkii.GridEffects[effect]
            if colour not in range(128):
                # Check if colour value is inside of the allowed 128 values
                raise InvalidButtonColour(
                    self.controller, self.controller.midi_in, self
                )
            if effect not in range(16):
                # Check if effect value is inside of the allowed 16 values
                raise InvalidButtonEffect(
                    self.controller, self.controller.midi_in, self
                )
            try:  # Try to set the led
                self.controller.midi_out.send(
                    mido.Message(
                        "note_on",
                        note=APCMinimkii.GridMapping[self.x][self.y],
                        velocity=colour,
                        channel=effect
                    )
                )
            except IndexError:
                raise InvalidGridButton(
                    self.controller, self.controller.midi_in,
                    (self.x, self.y)
                )

    class Fader:  # A single fader
        def __init__(self, controller, fader_id, value):
            self.controller = controller
            self.fader_id = fader_id
            self.value = value

        @staticmethod
        def get_fader_id_from_number(fader_num):
            try:
                return APCMinimkii.FaderMapping.index(fader_num)
            except IndexError:
                raise InvalidFader(None, None, fader_num)

    class SideButtons:  # All the side buttons
        def __init__(self, controller):
            self.controller = controller

        def set_led(self, button_id, colour):
            """Sets an LED on the side buttons"""
            APCMinimkii.SideButton(self.controller, button_id).set_led(colour)

        def reset_led(self, button_id):
            """Turns of an LED on the side buttons"""
            APCMinimkii.SideButton(self.controller, button_id).set_led(0)

        def reset_all_leds(self):
            """Turns of all LEDs on the side buttons"""
            for button in range(len(APCMinimkii.SideButtonMapping)):
                self.reset_led(button)

    class SideButton:  # A specific side button
        def __init__(self, controller, button_id: int, state: bool = False):
            self.controller = controller
            self.button_id = button_id
            self.state = state

        @staticmethod
        def get_button_id_from_button_num(button_num):
            return APCMinimkii.SideButtonMapping.index(button_num)

        def set_led(self, colour):
            """Sets this specific button's LED to be the colour given"""
            if not isinstance(colour, int):
                if colour not in APCMinimkii.SideButtonColours:
                    raise InvalidButtonColour(
                        self.controller,
                        self.controller.midi_in,
                        self
                    )
                colour = APCMinimkii.SideButtonColours[colour]
            if colour not in range(128):
                # Check if colour is a valid value
                raise InvalidButtonColour(
                    self.controller,
                    self.controller.midi_in,
                    self
                )
            try:  # Try to send the event
                self.controller.midi_out.send(
                    mido.Message(
                        "note_on",
                        note=APCMinimkii.SideButtonMapping[self.button_id],
                        velocity=colour
                    )
                )
            except IndexError:
                raise InvalidSideButton(
                    self.controller,
                    self.controller.midi_in,
                    self.button_id
                )

    class LowerButtons:  # All the lower buttons
        def __init__(self, controller):
            self.controller = controller

        def set_led(self, button_id, colour):
            """Sets an LED on the lower buttons"""
            APCMinimkii.LowerButton(self.controller, button_id).set_led(colour)

        def reset_led(self, button_id):
            """Turns of an LED on the lower buttons"""
            APCMinimkii.LowerButton(self.controller, button_id).set_led(0)

        def reset_all_leds(self):
            """Turns of all LEDs on the lower buttons"""
            for button in range(len(APCMinimkii.LowerButtonMapping)):
                self.reset_led(button)

    class LowerButton:  # A specific side button
        def __init__(self, controller, button_id: int, state: bool = False):
            self.controller = controller
            self.button_id = button_id
            self.state = state

        @staticmethod
        def get_button_id_from_button_num(button_num):
            try:
                return APCMinimkii.LowerButtonMapping.index(button_num)
            except IndexError:
                raise InvalidLowerButton(None, None, button_num)

        def set_led(self, colour):
            """Sets this specific button's LED to be the colour given"""
            if not isinstance(colour, int):
                if colour not in APCMinimkii.LowerButtonColours:
                    raise InvalidButtonColour(
                        self.controller,
                        self.controller.midi_in,
                        self
                    )
                colour = APCMinimkii.LowerButtonColours[colour]
            if colour not in range(128):
                # Check if colour is a valid value
                raise InvalidButtonColour(
                    self.controller,
                    self.controller.midi_in,
                    self
                )
            try:
                self.controller.midi_out.send(
                    mido.Message(
                        "note_on",
                        note=APCMinimkii.LowerButtonMapping[self.button_id],  # noqa: E501
                        velocity=colour
                    )
                )
            except IndexError:
                raise InvalidLowerButton(
                    self.controller,
                    self.controller.midi_in,
                    self.button_id
                )

    class ShiftButton:  # The shift button
        def __init__(self, controller, state: bool = False):
            self.controller = controller
            self.state = state
