import time
import sys
import threading
import socket

def get_local_ip():
    ip = '127.0.0.1'
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
    except Exception:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('10.255.255.255', 1))
            ip = s.getsockname()[0]
            s.close()
        except Exception:
            try:
                ip = socket.gethostbyname(socket.gethostname())
            except Exception:
                pass
    return ip

try:
    import BAC0
    from bacpypes.object import BinaryValueObject
    from bacpypes.primitivedata import CharacterString
except ImportError:
    print("BAC0 is required. Please run 'pip install BAC0'")
    sys.exit(1)

# Tags Dictionary Mapping
TAGS = {
    "TAG1": "RIA_Flow_Event",
    "TAG2": "Post_Flow_Event",
    "TAG3": "Sprinkler_Flow_Event",
    "TAG4": "Pump_Run_Event",
    "TAG5": "Valve_Sprinkler_Main_Closed",
    "TAG6": "Valve_Discharge_Closed",
    "TAG7": "Freeze_Risk_Active",
    "TAG8": "Tank_Low_Active",
    "TAG9": "Tank_High_Active",
    "TAG10": "Electrical_Fault_Active",
    "TAG11": "Valve_Suction_Closed",
    "TAG12": "Pump_NonAuto_Active",
    "TAG13": "Pump_Start_Failure_Event",
    "TAG14": "Pump_GeneralFault_Active",
    "TAG15": "Valve_RIA_Closed",
    "TAG16": "Valve_Antifreeze_Down_Closed",
    "TAG17": "Valve_Antifreeze_Up_Closed",
    "TAG18": "Valve_Poste_Closed",
    "TAG19": "Jockey_Fault_Active",
}

class FireProtectionSimulator:
    def __init__(self, ip_address=None):
        if ip_address:
            local_ip = ip_address
        else:
            local_ip = get_local_ip()
            
        try:
            BAC0.log_level('error')
        except:
            pass
            
        print(f"Initializing BACnet server on {local_ip}/24...")
        self.bacnet = BAC0.lite(ip=f"{local_ip}/24", deviceId=1234)
        self.objects = {}
        self._current_task = None
        self._cancel_event = threading.Event()
        
        print("Registering BACnet properties...")
        # Create objects
        for i, (tag_id, tag_name) in enumerate(TAGS.items(), start=1):
            obj = BinaryValueObject(
                objectIdentifier=('binaryValue', i),
                objectName=tag_id,
                presentValue='inactive',
                description=tag_name,
            )
            # add object to the BAC0 app
            self.bacnet.this_application.add_object(obj)
            self.objects[tag_name] = obj
            
        self._set_active_scenario("STANDBY")

    def _set_active_scenario(self, name):
        self.active_scenario = name
        self.scenario_start_time = time.strftime("%H:%M:%S")
            
    def set_tag(self, tag_name, state: bool):
        val = 'active' if state else 'inactive'
        obj = self.objects.get(tag_name)
        if obj:
            # Updating presentValue property
            obj.presentValue = val
            
    def reset_all(self):
        # Defaults to False (standby typical states)
        for tag_name in TAGS.values():
            self.set_tag(tag_name, False)

    def print_status(self):
        print("\n--- Current TAG Status ---")
        for tag_id in sorted(TAGS.keys(), key=lambda x: int(x[3:])):
            tag_name = TAGS[tag_id]
            val = self.objects[tag_name].presentValue
            val_bool = "TRUE" if str(val).lower() == "active" else "FALSE"
            print(f"{tag_id:<8} - {tag_name:<30}: {val_bool}")
        print("--------------------------\n")

    def _start_background_task(self, target):
        self._cancel_task()
        self._cancel_event.clear()
        self._current_task = threading.Thread(target=target, daemon=True)
        self._current_task.start()

    def _cancel_task(self):
        if self._current_task and self._current_task.is_alive():
            self._cancel_event.set()
            if self._current_task != threading.current_thread():
                self._current_task.join(timeout=1.0)

    def _sleep(self, seconds):
        """Wait for given seconds. Returns True if canceled."""
        return self._cancel_event.wait(seconds)

    def _scenario_standby_logic(self):
        self._set_active_scenario("STANDBY")
        self.reset_all()
        # Only tag 18 is true
        self.set_tag("Valve_Poste_Closed", True)

    def _scenario_standby_task(self):
        while True:
            self._scenario_standby_logic()
            
            # Wait 60 minutes
            if self._sleep(3600.0): return
            
            print("\n\n>> Auto-transition: 60 minutes in STANDBY. Transitioning to DIESEL PUMP TEST.")
            self._set_active_scenario("DIESEL PUMP TEST")
            self.reset_all()
            # Only tags 4, 6 and 18 are true
            self.set_tag("Pump_Run_Event", True)
            self.set_tag("Valve_Discharge_Closed", True)
            self.set_tag("Valve_Poste_Closed", True)
            
            print_menu(self)
            print("Select an option (0-7): ", end="", flush=True)
            
            # Diesel test runs for 5 minutes
            if self._sleep(300.0): return
            
            print("\n\n>> Auto-transition: 5 minutes elapsed. Returning to STANDBY.")
            print_menu(self)
            print("Select an option (0-7): ", end="", flush=True)

    def scenario_standby(self):
        self._start_background_task(self._scenario_standby_task)

    def _scenario_minor_loss_task(self):
        self._set_active_scenario("MINOR LOSS OF PRESSURE")
        self.reset_all()
        # Only tags 3 and 18 are true
        self.set_tag("Sprinkler_Flow_Event", True)
        self.set_tag("Valve_Poste_Closed", True)
        
        if self._sleep(45.0): return
        
        self.set_tag("Sprinkler_Flow_Event", False)
        
        print("\n\n>> Auto-transition: 45 seconds elapsed. Returning to STANDBY.")
        self.scenario_standby()
        print_menu(self)
        print("Select an option (0-7): ", end="", flush=True)

    def scenario_minor_loss(self):
        self._start_background_task(self._scenario_minor_loss_task)

    def _scenario_diesel_test_task(self):
        self._set_active_scenario("DIESEL PUMP TEST")
        self.reset_all()
        # Only tags 4, 6 and 18 are true
        self.set_tag("Pump_Run_Event", True)
        self.set_tag("Valve_Discharge_Closed", True)
        self.set_tag("Valve_Poste_Closed", True)
        
        # Scenario takes no longer than 5 minutes
        if self._sleep(300.0): return
        
        print("\n>> Auto-transition: 5 minutes elapsed. Returning to STANDBY.")
        self.scenario_standby()
        print_menu(self)
        print("Select an option (0-7): ", end="", flush=True)

    def scenario_diesel_test(self):
        self._start_background_task(self._scenario_diesel_test_task)

    def _scenario_sprinkler_demand_task(self):
        self._set_active_scenario("SPRINKLER SYSTEM DEMAND")
        self.reset_all()
        # Only tags 3, 4 and 18 are true
        self.set_tag("Sprinkler_Flow_Event", True)
        self.set_tag("Pump_Run_Event", True)
        self.set_tag("Valve_Poste_Closed", True)
        
        # Takes no longer than 15 minutes
        if self._sleep(900.0): return
        
        print("\n\n>> Auto-transition: 15 minutes elapsed. Moving to TANK DEPLETED.")
        self.scenario_tank_depleted()

    def scenario_sprinkler_demand(self):
        self._start_background_task(self._scenario_sprinkler_demand_task)

    def _scenario_ria_demand_task(self):
        self._set_active_scenario("RIA HOSE DEMAND")
        self.reset_all()
        # Only tags 1, 4 and 18 are true
        self.set_tag("RIA_Flow_Event", True)
        self.set_tag("Pump_Run_Event", True)
        self.set_tag("Valve_Poste_Closed", True)

        # Takes no longer than 15 minutes
        if self._sleep(900.0): return
        
        print("\n\n>> Auto-transition: 15 minutes elapsed. Moving to TANK DEPLETED.")
        self.scenario_tank_depleted()

    def scenario_ria_demand(self):
        self._start_background_task(self._scenario_ria_demand_task)

    def _scenario_tank_depleted_logic(self):
        self._set_active_scenario("TANK DEPLETED")
        self.reset_all()
        # Only tags 1, 2, 3 and 8 are true
        self.set_tag("RIA_Flow_Event", True)
        self.set_tag("Post_Flow_Event", True)
        self.set_tag("Sprinkler_Flow_Event", True)
        self.set_tag("Tank_Low_Active", True)

    def _scenario_tank_depleted_task(self):
        self._scenario_tank_depleted_logic()
        
        # System stays in Tank Depleted for 10 minutes
        if self._sleep(600.0): return
        
        print("\n\n>> Auto-transition: Tank Depleted for 10 minutes. Returning to STANDBY.")
        self.scenario_standby()
        print_menu(self)
        print("Select an option (0-7): ", end="", flush=True)

    def scenario_tank_depleted(self):
        self._start_background_task(self._scenario_tank_depleted_task)

def print_menu(sim):
    print("\n" + "="*45)
    print("  FIRE PROTECTION SIMULATOR SCENARIOS")
    print(f"  [ ACTIVE: {sim.active_scenario} | SINCE: {sim.scenario_start_time} ]")
    print("="*45)
    print("1) STANDBY")
    print("2) MINOR LOSS OF PRESSURE")
    print("3) DIESEL PUMP TEST")
    print("4) SPRINKLER SYSTEM DEMAND")
    print("5) RIA HOSE DEMAND")
    print("6) TANK DEPLETED")
    print("7) DISPLAY CURRENT TAG STATES")
    print("0) EXIT")
    print("="*45)

def get_input_timeout(prompt, timeout, default):
    print(f"{prompt} (Timeout in {timeout}s)\n> ", end="", flush=True)
    if sys.platform == 'win32':
        import msvcrt
        start_time = time.time()
        input_str = ""
        while time.time() - start_time < timeout:
            if msvcrt.kbhit():
                char = msvcrt.getche()
                if char in (b'\r', b'\n'):
                    print()
                    return input_str if input_str else default
                elif char == b'\x08': # Backspace
                    input_str = input_str[:-1]
                    print(" \b", end="", flush=True)
                else:
                    try:
                        input_str += char.decode('utf-8')
                    except UnicodeDecodeError:
                        pass
            time.sleep(0.05)
        print(f"\n>> Timeout reached. Defaulting to: {default}\n")
        return default
    else:
        import select
        i, o, e = select.select([sys.stdin], [], [], timeout)
        if i:
            val = sys.stdin.readline().strip()
            return val if val else default
        else:
            print(f"\n>> Timeout reached. Defaulting to: {default}\n")
            return default

def main():
    if len(sys.argv) > 1:
        ip_address = sys.argv[1]
    else:
        auto_ip = get_local_ip()
        print("\n=== NETWORK SETUP ===")
        user_input = get_input_timeout(f"Enter the IP address for the BACnet server to use (Press Enter to use auto-detected IP [{auto_ip}])", 10, auto_ip)
        ip_address = user_input if user_input else auto_ip
        
    sim = FireProtectionSimulator(ip_address=ip_address)
    sim.scenario_standby()
    
    while True:
        print_menu(sim)
        choice = input("Select an option (0-7): ").strip()
        
        if choice == '1':
            sim.scenario_standby()
            print(">> Scenario Applied: STANDBY")
        elif choice == '2':
            sim.scenario_minor_loss()
            print(">> Scenario Applied: MINOR LOSS OF PRESSURE")
        elif choice == '3':
            sim.scenario_diesel_test()
            print(">> Scenario Applied: DIESEL PUMP TEST")
        elif choice == '4':
            sim.scenario_sprinkler_demand()
            print(">> Scenario Applied: SPRINKLER SYSTEM DEMAND")
        elif choice == '5':
            sim.scenario_ria_demand()
            print(">> Scenario Applied: RIA HOSE DEMAND")
        elif choice == '6':
            sim.scenario_tank_depleted()
            print(">> Scenario Applied: TANK DEPLETED")
        elif choice == '7':
            sim.print_status()
        elif choice == '0':
            print("Exiting...")
            try:
                sim.bacnet.disconnect()
            except:
                pass
            break
        else:
            print("Invalid selection.")

if __name__ == '__main__':
    main()
