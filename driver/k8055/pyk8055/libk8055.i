/* $Id: libk8055.i,v 1.3 2007/03/28 10:08:13 pjetur Exp $
 *
 *   Modernized for Python 3 and to link against the shared library.
 *   Copyright (C) 2007  by Pjetur G. Hjaltason
 */
%module pyk8055
%include "typemaps.i"

/* This SWIG typemap correctly handles C functions that use pointers
   to return multiple values, converting them into a Python tuple. */
%apply long *OUTPUT { long int *data1, long int *data2, long int *data3, long int *data4, long int *data5 };

/*
 * The inline C functions below that accessed global variables (data_in, data_out)
 * have been removed. They are incompatible with linking against a pre-compiled
 * shared library, which does not expose its internal state variables.
 * All core functionality is preserved.
*/
%inline %{
%}

/*
 * This block declares all the C functions from k8055.h that SWIG needs
 * to create wrappers for.
*/
%{
#include "k8055.h"
%}

/*
 * This block tells SWIG to wrap the C functions defined in k8055.h.
*/
%include "k8055.h"


/*
 * This block injects a Python class into the final pyk8055.py module.
 * This provides a high-level, user-friendly object-oriented interface.
 * It has been updated for Python 3 syntax.
*/
%pythoncode %{
K8055_ERROR = -1
_K8055_CLOSED = -1

class k8055:
    "Class interface to the libk8055 library (Python 3)"
    def __init__(self, BoardAddress=None):
        """Constructor, optionally opens the board.

         k=k8055()      # Does not connect to the board.
         k=k8055(0)     # Connects to the board at address 0.
        """
        self.dev = _K8055_CLOSED
        self.Address = BoardAddress
        if BoardAddress is not None:
            self.OpenDevice(BoardAddress)

    def __str__(self):
        """String format (almost) as from K8055 program"""
        if self.__opentest():    # Device open
            all_values = self.ReadAllValues()
            # The C function returns a tuple; we format the actual values.
            return f"{all_values[0]};{all_values[1]};{all_values[2]};{all_values[3]};{all_values[4]}"
        else:
            return "Device is not open."

    def __opentest(self):
        return self.dev != _K8055_CLOSED

    def OpenDevice(self, BoardAddress):
        """Open the connection to the K8055 board.

        k=k8055()
        try:
           k.OpenDevice(0) # possible addresses are 0, 1, 2, 3
        except IOError:
            ...
        Throws IOError if the board is not found or cannot be accessed.
        """
        if not self.__opentest():    # Not open yet
            self.dev = OpenDevice(BoardAddress)
            if self.dev == K8055_ERROR:
                # Correct Python 3 exception syntax
                raise IOError("Could not open device. Check connection, permissions (udev), and address.")
            self.Address = BoardAddress
        return self.dev

    def CloseDevice(self):
        """Close the connection to the K8055 board. Returns 0 if OK."""
        if self.dev != _K8055_CLOSED:
            ret = CloseDevice()
            self.dev = _K8055_CLOSED
            return ret

    def OutputAnalogChannel(self, Channel, value=0):
        """Set analog output channel value (0-255)."""
        if not self.__opentest(): return K8055_ERROR
        return OutputAnalogChannel(Channel, value)

    def ReadAnalogChannel(self, Channel):
        """Read data from an analog input channel (1 or 2)."""
        if not self.__opentest(): return K8055_ERROR
        return ReadAnalogChannel(Channel)

    def ReadAllAnalog(self):
        """Read data from both analog input channels at once.
        Returns a tuple: (analog1, analog2)
        """
        if not self.__opentest(): return K8055_ERROR, K8055_ERROR
        return ReadAllAnalog()

    def OutputAllAnalog(self, data1, data2):
        """Set both analog output channels at once (0-255)."""
        if not self.__opentest(): return K8055_ERROR
        return OutputAllAnalog(data1, data2)

    def ClearAllAnalog(self):
        """Set both analog output channels to 0."""
        if not self.__opentest(): return K8055_ERROR
        return ClearAllAnalog()

    def ClearAnalogChannel(self, Channel):
        """Set an analog output channel (1 or 2) to 0."""
        if not self.__opentest(): return K8055_ERROR
        return ClearAnalogChannel(Channel)

    def SetAnalogChannel(self, Channel):
        """Set an analog output channel (1 or 2) to 255 (high)."""
        if not self.__opentest(): return K8055_ERROR
        return SetAnalogChannel(Channel)

    def SetAllAnalog(self):
        """Set both analog output channels to 255 (high)."""
        if not self.__opentest(): return K8055_ERROR
        return SetAllAnalog()

    def WriteAllDigital(self, data):
        """Write a bitmask to the digital output channels (0-255)."""
        if not self.__opentest(): return K8055_ERROR
        return WriteAllDigital(data)

    def ClearDigitalChannel(self, Channel):
        """Clear a single digital output channel (1-8)."""
        if not self.__opentest(): return K8055_ERROR
        return ClearDigitalChannel(Channel)

    def ClearAllDigital(self):
        """Set all digital output channels to 0."""
        if not self.__opentest(): return K8055_ERROR
        return ClearAllDigital()

    def SetDigitalChannel(self, Channel):
        """Set a single digital output channel (1-8)."""
        if not self.__opentest(): return K8055_ERROR
        return SetDigitalChannel(Channel)

    def SetAllDigital(self):
        """Set all digital output channels to 1."""
        if not self.__opentest(): return K8055_ERROR
        return SetAllDigital()

    def ReadDigitalChannel(self, Channel):
        """Read a single digital input channel (1-5), returns 0 or 1."""
        if not self.__opentest(): return K8055_ERROR
        return ReadDigitalChannel(Channel)

    def ReadAllDigital(self):
        """Read all digital inputs as a bitmask (0-31)."""
        if not self.__opentest(): return K8055_ERROR
        return ReadAllDigital()

    def ResetCounter(self, CounterNo):
        """Reset an input counter (1 or 2)."""
        if not self.__opentest(): return K8055_ERROR
        return ResetCounter(CounterNo)

    def ReadCounter(self, CounterNo):
        """Read an input counter (1 or 2)."""
        if not self.__opentest(): return K8055_ERROR
        return ReadCounter(CounterNo)

    def SetCounterDebounceTime(self, CounterNo, DebounceTime):
        """Set debounce time for a counter (1-7450 ms)."""
        if not self.__opentest(): return K8055_ERROR
        return SetCounterDebounceTime(CounterNo, DebounceTime)

    def SetCurrentDevice(self):
        """Re-asserts the current device context. Usually not needed."""
        if not self.__opentest(): return K8055_ERROR
        return SetCurrentDevice(self.Address)

    def DeviceAddress(self):
        """Returns the address of the currently open device."""
        return self.Address

    def IsOpen(self):
        """Returns True if the device is open, False otherwise."""
        return self.__opentest()

    def ReadAllValues(self):
        """Read all inputs at once.
        Returns a tuple: (digital, analog1, analog2, counter1, counter2)
        """
        if not self.__opentest(): return K8055_ERROR, K8055_ERROR, K8055_ERROR, K8055_ERROR, K8055_ERROR
        return ReadAllValues()

    def SetAllValues(self, digitaldata, addata1, addata2):
        """Set all outputs at once."""
        if not self.__opentest(): return K8055_ERROR
        return SetAllValues(digitaldata, addata1, addata2)

    def Version(self):
        """Returns the version string of the C library."""
        return Version()

%}
