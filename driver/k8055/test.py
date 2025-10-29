import pyk8055
import time
import sys

# Address of the board (0-3). Change this if your board is not set to 0.
BOARD_ADDRESS = 0

print("--- K8055 Python 3 Test Script ---")

try:
    # --- Step 1: Connect to the board ---
    k = pyk8055.k8055(BOARD_ADDRESS)
    print(f"Successfully connected to board at address {BOARD_ADDRESS}.")
    print(f"Using C-library version: {k.Version()}")

    # --- Step 2: Read all initial values ---
    digital_inputs = k.ReadAllDigital()
    
    # --- THIS IS THE FIX ---
    # ReadAllAnalog returns a tuple: (return_code, value1, value2)
    # We only care about the values, which are at index 1 and 2.
    analog_values = k.ReadAllAnalog()
    analog1 = analog_values[1]
    analog2 = analog_values[2]
    
    counter1 = k.ReadCounter(1)
    counter2 = k.ReadCounter(2)
    
    print(f"\nInitial Digital Inputs: {digital_inputs} (binary: {digital_inputs:05b})")
    print(f"Initial Analog Inputs:  A1={analog1}, A2={analog2}")
    print(f"Initial Counters:       C1={counter1}, C2={counter2}")

    # --- Step 3: Perform a test sequence ---
    print("\nStarting test sequence in 3 seconds (Press Ctrl+C to skip)...")
    time.sleep(3)
    
    print("--> Turning all digital outputs ON.")
    k.SetAllDigital()
    time.sleep(2)

    print("--> Turning all digital outputs OFF.")
    k.ClearAllDigital()
    time.sleep(1)

    print("--> Setting analog outputs to 50% (127) and 75% (191).")
    k.OutputAllAnalog(127, 191)
    time.sleep(2)

    print("--> Resetting all outputs to zero.")
    k.ClearAllAnalog()
    
    # --- Step 4: Close the connection ---
    k.CloseDevice()
    print("\nTest complete. Device connection closed successfully.")

except IOError as e:
    print(f"\nERROR: Could not connect to the board.", file=sys.stderr)
    print(f"Details: {e}", file=sys.stderr)
    print("Please check the following:", file=sys.stderr)
    print("1. The board is connected to USB and powered.", file=sys.stderr)
    print(f"2. The board address is correctly set to {BOARD_ADDRESS}.", file=sys.stderr)
    print("3. You have the correct permissions (udev rules are set and you have rebooted).", file=sys.stderr)
    sys.exit(1)
    
except Exception as e:
    print(f"\nAn unexpected error occurred: {e}", file=sys.stderr)
    sys.exit(1)
