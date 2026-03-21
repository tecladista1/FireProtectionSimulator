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

## Scenarios & Auto-Transitions

The simulator features 6 built-in scenarios. By default, it operates on an active background timer loop:

1. **STANDBY**: Only `Valve_Poste_Closed` (TAG 18) active.
   - **Cycle**: Runs for **60 minutes**. If uninterrupted, it automatically triggers a 5-minute **DIESEL PUMP TEST** (Scenario 3) and then loops back to Standby.
2. **MINOR LOSS OF PRESSURE**: Only `Sprinkler_Flow_Event` (TAG 3) & `Valve_Poste_Closed` (TAG 18) active.
   - **Cycle**: Runs for **45 seconds**, then auto-reverts to STANDBY.
3. **DIESEL PUMP TEST**: Only `Pump_Run_Event` (TAG 4), `Valve_Discharge_Closed` (TAG 6) & `Valve_Poste_Closed` (TAG 18) active.
   - **Cycle**: Runs for **5 minutes**, then auto-reverts to STANDBY.
4. **SPRINKLER SYSTEM DEMAND**: Only `Sprinkler_Flow_Event` (TAG 3), `Pump_Run_Event` (TAG 4) & `Valve_Poste_Closed` (TAG 18) active.
   - **Cycle**: Runs for **15 minutes**, then auto-transitions to TANK DEPLETED (Scenario 6).
5. **RIA HOSE DEMAND**: Only `RIA_Flow_Event` (TAG 1), `Pump_Run_Event` (TAG 4) & `Valve_Poste_Closed` (TAG 18) active.
   - **Cycle**: Runs for **15 minutes**, then auto-transitions to TANK DEPLETED (Scenario 6).
6. **TANK DEPLETED**: Only `RIA_Flow_Event` (TAG 1), `Post_Flow_Event` (TAG 2), `Sprinkler_Flow_Event` (TAG 3) & `Tank_Low_Active` (TAG 8) active.
   - **Cycle**: Runs for **10 minutes**, then auto-reverts to STANDBY.
