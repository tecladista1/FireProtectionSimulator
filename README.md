# Fire Protection System Simulator

This is a Python script that acts as a BACnet IP server describing the states of a Fire Protection system, containing 19 Boolean tags.

## Prerequisites

This script can be run on both Windows and Linux OS. It supports Python versions 3.8 to 3.14+ (the required `pyasyncore` package is included to support Python 3.12+ since native `asyncore` was removed).

### Windows Setup

1. Create and activate a Virtual Environment:
   ```cmd
   python -m venv venv
   venv\Scripts\activate
   ```

2. Install the dependencies using the supplied `requirements.txt`:
   ```cmd
   pip install -r requirements.txt
   ```

### Linux Setup

1. Update package list and ensure you have `pip` installed:
   ```bash
   sudo apt-get update
   sudo apt-get install python3-pip
   ```

2. Install the required BACnet library dependencies using the supplied `requirements.txt`:
   ```bash
   pip3 install -r requirements.txt
   ```

## Running the Simulator

Execute the script using Python:

```bash
python fire_protection_simulator.py
```

An interactive menu will appear in the terminal, allowing you to select different system scenarios (1 through 6). 
Selecting a scenario will instantly update the 19 BACnet tags being broadcasted by your Linux VM, making them available to any SCADA, Dashboard, or BMS software querying the VM's IP address on port 47808.

## Scenarios

1.  **STANDBY**: pressure 7 bar, all flow events FALSE, pumps OFF
2.  **MINOR LOSS OF PRESSURE**: Jockey starts (no tag for jockey state but Jockey_Fault_Active=FALSE)
3.  **DIESEL PUMP TEST**: Valve_Discharge_Closed=TRUE, Pump_Run_Event=TRUE
4.  **SPRINKLER SYSTEM DEMAND**: Valve_Sprinkler_Main_Closed=FALSE, Sprinkler_Flow_Event=TRUE, Post_Flow_Event=TRUE, Pump_Run_Event=TRUE
5.  **RIA HOSE DEMAND**: RIA_Flow_Event=TRUE, Pump_Run_Event=TRUE
6.  **TANK DEPLETED**: Tank_Low_Active=TRUE, Tank_High_Active=FALSE, Post_Flow_Event=TRUE
