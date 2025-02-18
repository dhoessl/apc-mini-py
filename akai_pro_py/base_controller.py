import mido
import asyncio

from . import errors
from .logger import setup_logger


class Controller:
    def __init__(self, midi_in=None, midi_out=None, logging_enabled=False):
        self.logger = setup_logger(__name__)
        self.logging = logging_enabled
        self.midi_out = mido.open_output(midi_out)  # Open MIDI out for controller
        self.midi_in = mido.open_input(midi_in)  # Open MIDI in for controller
        self.setup_in_progress = True
        self.midi_in.callback = self.on_midi_in  # Set callback function for incomming MIDI messages
        self.event_dispatch = None  # Defines the dispatch event to be none
        self.ready_dispatch = None
        self.raw_dispatch = False
        self.loop = asyncio.new_event_loop()  # Creates the event loop for handling button presses
        self.name = "Base Controller"  # Name of the device
        # MIDI Device Enquiry (SysEx)
        self.midi_out.send(mido.Message.from_bytes([0xF0, 0x7E, 0x7F, 0x06, 0x01, 0xF7]))

    def on_event(self, func):
        """Used to dispatch MIDI events from the controller"""
        if self.event_dispatch is not None:
            msg = "Event dispatch function is already defined!"
            if self.logging:
                self.logger.error(msg)
            raise errors.AkaiProPyError(msg)
        self.event_dispatch = func

    def on_ready(self, func):
        if self.ready_dispatch is not None:
            msg = "Ready event function already defined!"
            if self.logging:
                self.logger.error(msg)
            raise errors.AkaiProPyError(msg)
        self.ready_dispatch = func

    def on_midi_in(self, event):
        if self.setup_in_progress:
            product_detect_success = self.product_detect(event)
            if product_detect_success and self.ready_dispatch is not None:
                self.ready_dispatch()
        else:
            self.pre_event_dispatch(event)

    def product_detect(self, event):
        try:
            if event.data[4] != 6:
                msg = "Controller did not identify!"
                if self.logging:
                    self.logger.error(msg)
                raise errors.ControllerIdentificationError(
                    self, self.midi_in, msg
                )
        except KeyError:
            msg = "Controller failed to identify!"
            if self.logging:
                self.logger.error(msg)
            raise errors.ControllerIdentificationError(
                self, self.midi_in, msg
            )
        self.setup_in_progress = False
        return True

    def pre_event_dispatch(self, event):
        if self.event_dispatch is None:
            return  # Ignore if a dispatch event is not set with the on_event decorator

    def start(self):
        """Start the event loop for receiving MIDI messages"""
        self.loop.run_forever()
