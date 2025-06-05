import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
import time
import random
import threading
import pyautogui # For simulating keyboard and mouse actions

class ActivitySimulatorApp:
    def __init__(self, master):
        self.master = master
        master.title("Advanced Activity Simulator")
        master.geometry("550x800") # Increased height significantly for more options
        master.resizable(False, False)

        # --- Automation Control Variables ---
        self.is_running = tk.BooleanVar(value=False)
        self.min_interval_seconds = tk.IntVar(value=120)  # Default min 2 minutes
        self.max_interval_seconds = tk.IntVar(value=180)  # Default max 3 minutes
        self.start_delay_minutes = tk.IntVar(value=1)     # Default 1 minute delay

        # --- NEW: Custom Key Presses Variables ---
        self.custom_keys_enabled = tk.BooleanVar(value=True)
        # Default keys include common non-disruptive ones, plus up/down arrows
        self.custom_keys_string = tk.StringVar(value="shift,ctrl,alt,f13,f14,f15,up,down,numlock,scrolllock")
        self.custom_key_frequency = tk.IntVar(value=1) # Default: every 1st activity (always active if enabled)

        # --- NEW: Scroll Wheel Simulation Variables ---
        self.scroll_enabled = tk.BooleanVar(value=False)
        self.scroll_amount = tk.IntVar(value=3) # Default: 3 clicks
        self.scroll_frequency = tk.IntVar(value=3) # Default: every 3rd activity

        # --- NEW: Full Screen Mouse Movement Variables ---
        self.full_screen_mouse_enabled = tk.BooleanVar(value=False)
        self.full_screen_mouse_frequency = tk.IntVar(value=5) # Default: every 5th activity

        # --- Initialize pyautogui fail-safe ---
        pyautogui.FAILSAFE = True # Moving mouse to top-left corner will stop the script.

        self.create_widgets()
        self.automation_thread = None # To hold the thread that runs automation

    def create_widgets(self):
        # --- Initial Delay Settings Frame ---
        delay_frame = tk.LabelFrame(self.master, text="Initial Start Delay")
        delay_frame.pack(padx=10, pady=5, fill="x") # Reduced pady for compactness

        tk.Label(delay_frame, text="Start automation after:").pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Entry(delay_frame, textvariable=self.start_delay_minutes, width=10).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Label(delay_frame, text="minutes").pack(side=tk.LEFT, padx=5, pady=5)

        # --- Main Activity Interval Settings Frame ---
        interval_frame = tk.LabelFrame(self.master, text="Overall Activity Interval (Seconds)")
        interval_frame.pack(padx=10, pady=5, fill="x")

        tk.Label(interval_frame, text="Min:").pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Entry(interval_frame, textvariable=self.min_interval_seconds, width=10).pack(side=tk.LEFT, padx=5, pady=5)

        tk.Label(interval_frame, text="Max:").pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Entry(interval_frame, textvariable=self.max_interval_seconds, width=10).pack(side=tk.LEFT, padx=5, pady=5)

        # --- NEW: Custom Key Presses Frame ---
        custom_keys_frame = tk.LabelFrame(self.master, text="Custom Key Presses")
        custom_keys_frame.pack(padx=10, pady=5, fill="x")

        ttk.Checkbutton(custom_keys_frame, text="Enable Custom Key Simulation", variable=self.custom_keys_enabled).pack(anchor=tk.W, padx=5, pady=2)
        tk.Label(custom_keys_frame, text="Keys (comma-separated):").pack(anchor=tk.W, padx=5)
        ttk.Entry(custom_keys_frame, textvariable=self.custom_keys_string, width=60).pack(padx=5, pady=2, fill="x")
        
        freq_frame_keys = tk.Frame(custom_keys_frame)
        freq_frame_keys.pack(anchor=tk.W, padx=5, pady=2)
        tk.Label(freq_frame_keys, text="Press a custom key every").pack(side=tk.LEFT)
        ttk.Entry(freq_frame_keys, textvariable=self.custom_key_frequency, width=5).pack(side=tk.LEFT, padx=5)
        tk.Label(freq_frame_keys, text="activities.").pack(side=tk.LEFT)

        # --- NEW: Scroll Wheel Simulation Frame ---
        scroll_frame = tk.LabelFrame(self.master, text="Scroll Wheel Simulation")
        scroll_frame.pack(padx=10, pady=5, fill="x")

        ttk.Checkbutton(scroll_frame, text="Enable Scroll Simulation", variable=self.scroll_enabled).pack(anchor=tk.W, padx=5, pady=2)
        
        scroll_amt_frame = tk.Frame(scroll_frame)
        scroll_amt_frame.pack(anchor=tk.W, padx=5, pady=2)
        tk.Label(scroll_amt_frame, text="Scroll amount (clicks):").pack(side=tk.LEFT)
        ttk.Entry(scroll_amt_frame, textvariable=self.scroll_amount, width=5).pack(side=tk.LEFT, padx=5)

        freq_frame_scroll = tk.Frame(scroll_frame)
        freq_frame_scroll.pack(anchor=tk.W, padx=5, pady=2)
        tk.Label(freq_frame_scroll, text="Perform scroll every").pack(side=tk.LEFT)
        ttk.Entry(freq_frame_scroll, textvariable=self.scroll_frequency, width=5).pack(side=tk.LEFT, padx=5)
        tk.Label(freq_frame_scroll, text="activities.").pack(side=tk.LEFT)

        # --- NEW: Full Screen Mouse Movement Frame ---
        full_mouse_frame = tk.LabelFrame(self.master, text="Full Screen Mouse Movement")
        full_mouse_frame.pack(padx=10, pady=5, fill="x")

        ttk.Checkbutton(full_mouse_frame, text="Enable Full Screen Mouse Movement", variable=self.full_screen_mouse_enabled).pack(anchor=tk.W, padx=5, pady=2)
        
        freq_frame_mouse = tk.Frame(full_mouse_frame)
        freq_frame_mouse.pack(anchor=tk.W, padx=5, pady=2)
        tk.Label(freq_frame_mouse, text="Move mouse every").pack(side=tk.LEFT)
        ttk.Entry(freq_frame_mouse, textvariable=self.full_screen_mouse_frequency, width=5).pack(side=tk.LEFT, padx=5)
        tk.Label(freq_frame_mouse, text="activities.").pack(side=tk.LEFT)


        # --- Control Buttons Frame ---
        button_frame = tk.Frame(self.master)
        button_frame.pack(pady=10)

        self.start_button = tk.Button(button_frame, text="Start Simulation", command=self.start_simulation,
                                      bg="green", fg="white", font=("Helvetica", 10, "bold"), width=18)
        self.start_button.pack(side=tk.LEFT, padx=10)

        self.stop_button = tk.Button(button_frame, text="Stop Simulation", command=self.stop_simulation,
                                     bg="red", fg="white", font=("Helvetica", 10, "bold"), width=18, state=tk.DISABLED)
        self.stop_button.pack(side=tk.RIGHT, padx=10)

        # --- Status Label ---
        self.status_label = tk.Label(self.master, text="Status: Idle", fg="blue", font=("Helvetica", 10, "italic"))
        self.status_label.pack(pady=5)

        # --- Log Area ---
        log_frame = tk.LabelFrame(self.master, text="Activity Log")
        log_frame.pack(padx=10, pady=10, fill="both", expand=True)

        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, width=60, height=15, state='disabled', font=("Consolas", 9))
        self.log_text.pack(padx=5, pady=5, fill="both", expand=True)

        self.log_message("Welcome to the Advanced Activity Simulator. Set options and click Start.")
        self.log_message("Remember: Move mouse to top-left corner to EMERGENCY STOP!")

    def log_message(self, message):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        self.log_text.config(state='normal') # Enable editing
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END) # Scroll to the end
        self.log_text.config(state='disabled') # Disable editing

    def validate_inputs(self):
        try:
            min_int = self.min_interval_seconds.get()
            max_int = self.max_interval_seconds.get()
            start_delay = self.start_delay_minutes.get()

            # Validate main intervals and delay
            if not all(isinstance(val, int) for val in [min_int, max_int, start_delay]):
                raise ValueError("Main intervals and delay must be whole numbers.")
            if min_int <= 0 or max_int <= 0:
                raise ValueError("Main intervals must be positive.")
            if min_int > max_int:
                raise ValueError("Minimum interval cannot be greater than maximum interval.")
            if start_delay < 0:
                raise ValueError("Start delay cannot be negative.")

            # Validate Custom Keys
            if self.custom_keys_enabled.get():
                keys_list_str = self.custom_keys_string.get()
                if not keys_list_str.strip():
                    raise ValueError("Custom keys list cannot be empty if enabled.")
                # Basic validation: split and check against pyautogui's known keys
                keys = [k.strip() for k in keys_list_str.split(',') if k.strip()]
                if not keys:
                    raise ValueError("No valid keys found in custom keys list.")
                # Note: pyautogui.KEYBOARD_KEYS is a tuple of all valid key names
                # We can't strictly validate all here as it's a large set, but can check for basic format.
                # A more robust check might involve iterating through and catching pyautogui.FailSafeException if a bad key is pressed.
                freq = self.custom_key_frequency.get()
                if not isinstance(freq, int) or freq <= 0:
                    raise ValueError("Custom key frequency must be a positive whole number.")

            # Validate Scroll Wheel
            if self.scroll_enabled.get():
                amount = self.scroll_amount.get()
                freq = self.scroll_frequency.get()
                if not isinstance(amount, int) or amount == 0: # Scroll amount can be negative for down, but 0 is useless
                    raise ValueError("Scroll amount must be a non-zero whole number.")
                if not isinstance(freq, int) or freq <= 0:
                    raise ValueError("Scroll frequency must be a positive whole number.")

            # Validate Full Screen Mouse Movement
            if self.full_screen_mouse_enabled.get():
                freq = self.full_screen_mouse_frequency.get()
                if not isinstance(freq, int) or freq <= 0:
                    raise ValueError("Full screen mouse frequency must be a positive whole number.")

            # Ensure at least one activity type is enabled if intervals are set
            if not (self.custom_keys_enabled.get() or self.scroll_enabled.get() or self.full_screen_mouse_enabled.get()):
                result = messagebox.showwarning("No Actions Enabled", "No specific activity types (custom keys, scroll, full screen mouse) are enabled. The simulator will simply sleep for the set intervals. Do you want to continue?", type=messagebox.OKCANCEL)
                # If user cancels, return False
                if result != "ok": # Check if the result of showwarning is not 'ok'
                    return False
                # If 'ok', then allow to proceed but with a warning.
                self.log_message("Warning: No specific actions are enabled. Only main interval sleep will occur.")


            return True
        except ValueError as e:
            messagebox.showerror("Invalid Settings", str(e))
            return False

    def start_simulation(self):
        if not self.validate_inputs():
            return

        if self.is_running.get():
            messagebox.showwarning("Already Running", "Simulation is already active.")
            return

        self.is_running.set(True)
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.log_text.delete('1.0', tk.END) # Clear previous logs
        self.log_message("Simulation start request received.")
        
        # Log all enabled settings
        self.log_message(f"Initial start delay: {self.start_delay_minutes.get()} minutes.")
        self.log_message(f"Overall activity interval: {self.min_interval_seconds.get()}-{self.max_interval_seconds.get()} seconds.")
        
        if self.custom_keys_enabled.get():
            self.log_message(f"Custom Keys ENABLED (Pressing: {self.custom_keys_string.get()}) every {self.custom_key_frequency.get()} activities.")
            self.custom_keys_list = [k.strip() for k in self.custom_keys_string.get().split(',') if k.strip()]
        else:
            self.log_message("Custom Keys DISABLED.")
            self.custom_keys_list = [] # Ensure it's empty if disabled

        if self.scroll_enabled.get():
            self.log_message(f"Scroll Wheel ENABLED (Amount: {self.scroll_amount.get()}) every {self.scroll_frequency.get()} activities.")
        else:
            self.log_message("Scroll Wheel DISABLED.")

        if self.full_screen_mouse_enabled.get():
            self.log_message(f"Full Screen Mouse Movement ENABLED (every {self.full_screen_mouse_frequency.get()} activities).")
        else:
            self.log_message("Full Screen Mouse Movement DISABLED.")

        # Start the automation in a separate thread
        self.automation_thread = threading.Thread(target=self._run_automation, daemon=True)
        self.automation_thread.start()

    def stop_simulation(self):
        if not self.is_running.get():
            messagebox.showwarning("Not Running", "Simulation is not active.")
            return

        self.is_running.set(False)
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_label.config(text="Status: Stopping...", fg="red")
        self.log_message("Stop signal sent. Waiting for current action to finish...")
        # The _run_automation loop will check self.is_running and exit gracefully.

    def _run_automation(self):
        min_s = self.min_interval_seconds.get()
        max_s = self.max_interval_seconds.get()
        initial_delay_seconds = self.start_delay_minutes.get() * 60

        # Frequencies and enabled flags
        custom_key_freq = self.custom_key_frequency.get() if self.custom_keys_enabled.get() else 0
        scroll_freq = self.scroll_frequency.get() if self.scroll_enabled.get() else 0
        full_mouse_freq = self.full_screen_mouse_frequency.get() if self.full_screen_mouse_enabled.get() else 0
        
        # Get screen size once
        screen_width, screen_height = pyautogui.size()

        activity_counter = 0

        try:
            # --- Initial Delay Loop ---
            if initial_delay_seconds > 0:
                self.log_message(f"Initial delay started. Automation will begin in {self.start_delay_minutes.get()} minutes.")
                for i in range(initial_delay_seconds, 0, -1):
                    if not self.is_running.get():
                        self.master.after(0, lambda: self.status_label.config(text="Status: Stopped", fg="blue"))
                        self.master.after(0, lambda: self.log_message("Initial delay interrupted. Simulation stopped."))
                        return
                    
                    mins_remaining = i // 60
                    secs_remaining = i % 60
                    status_text = f"Status: Starting in {mins_remaining}m {secs_remaining}s..."
                    self.master.after(0, lambda text=status_text: self.status_label.config(text=text, fg="orange"))
                    time.sleep(1)

                if not self.is_running.get():
                    self.master.after(0, lambda: self.status_label.config(text="Status: Stopped", fg="blue"))
                    self.master.after(0, lambda: self.log_message("Initial delay completed but stop signal received. Simulation stopped."))
                    return

                self.log_message("Initial delay complete. Starting periodic automation.")
            
            self.master.after(0, lambda: self.status_label.config(text="Status: Running...", fg="green"))

            # --- Main Automation Loop ---
            while self.is_running.get():
                sleep_duration = random.randint(min_s, max_s)
                self.log_message(f"Sleeping for {sleep_duration} seconds until next activity cycle...")
                time.sleep(sleep_duration)

                if not self.is_running.get():
                    break # Exit loop if stop button was pressed during sleep

                activity_counter += 1
                actions_this_cycle = [] # Keep track of actions performed in this cycle

                # Action 1: Custom Key Press
                if self.custom_keys_enabled.get() and custom_key_freq > 0 and (activity_counter % custom_key_freq == 0):
                    if self.custom_keys_list: # Ensure list is not empty
                        key_to_press = random.choice(self.custom_keys_list)
                        try:
                            pyautogui.press(key_to_press)
                            self.log_message(f"Custom Key '{key_to_press}' pressed (Overall Activity #{activity_counter}).")
                            actions_this_cycle.append(True)
                        except Exception as e:
                            self.log_message(f"Error pressing custom key '{key_to_press}': {e}. Check key name validity.")
                    else:
                        self.log_message("WARNING: Custom keys enabled but list is empty. No key pressed.")
                    time.sleep(0.1) # Small delay between actions

                # Action 2: Scroll Wheel
                if self.scroll_enabled.get() and scroll_freq > 0 and (activity_counter % scroll_freq == 0):
                    scroll_amount = self.scroll_amount.get()
                    if scroll_amount != 0: # Ensure amount is not zero
                        # Randomly choose direction if amount is positive, or keep negative if specified
                        final_scroll_amount = random.choice([-scroll_amount, scroll_amount]) if scroll_amount > 0 else scroll_amount
                        pyautogui.scroll(final_scroll_amount)
                        self.log_message(f"Scrolled {final_scroll_amount} clicks (Overall Activity #{activity_counter}).")
                        actions_this_cycle.append(True)
                    else:
                        self.log_message("WARNING: Scroll amount is 0. No scroll performed.")
                    time.sleep(0.1)

                # Action 3: Full Screen Mouse Movement
                if self.full_screen_mouse_enabled.get() and full_mouse_freq > 0 and (activity_counter % full_mouse_freq == 0):
                    rand_x = random.randint(0, screen_width - 1)
                    rand_y = random.randint(0, screen_height - 1)
                    pyautogui.moveTo(rand_x, rand_y, duration=0.5) # A bit slower move
                    self.log_message(f"Mouse moved to ({rand_x}, {rand_y}) (Overall Activity #{activity_counter}).")
                    actions_this_cycle.append(True)
                    time.sleep(0.1)

                # Fallback: If no specific actions were enabled or triggered in this cycle
                if not any(actions_this_cycle):
                    self.log_message("No specific actions triggered this cycle. Performing a default 'shift' press.")
                    pyautogui.press('shift') # Default non-disruptive key
                    time.sleep(0.1)


            # Loop finished, update status
            self.master.after(0, lambda: self.status_label.config(text="Status: Stopped", fg="blue"))
            self.master.after(0, lambda: self.log_message("Simulation stopped."))

        except pyautogui.FailSafeException:
            self.master.after(0, lambda: self.is_running.set(False))
            self.master.after(0, lambda: self.start_button.config(state=tk.NORMAL))
            self.master.after(0, lambda: self.stop_button.config(state=tk.DISABLED))
            self.master.after(0, lambda: self.status_label.config(text="Status: EMERGENCY STOPPED by Failsafe!", fg="darkorange"))
            self.master.after(0, lambda: self.log_message("!!! pyautogui.FailSafeException: Simulation Emergency Stopped !!!"))
            self.master.after(0, lambda: messagebox.showwarning("EMERGENCY STOP", "PyAutoGUI Failsafe Triggered. Simulation stopped."))
        except Exception as e:
            self.master.after(0, lambda: self.is_running.set(False))
            self.master.after(0, lambda: self.start_button.config(state=tk.NORMAL))
            self.master.after(0, lambda: self.stop_button.config(state=tk.DISABLED))
            self.master.after(0, lambda: self.status_label.config(text="Status: Error", fg="red"))
            self.master.after(0, lambda: self.log_message(f"An unexpected error occurred: {e}"))
            self.master.after(0, lambda: messagebox.showerror("Error", f"An unexpected error occurred: {e}"))

# Main execution
if __name__ == "__main__":
    root = tk.Tk()
    app = ActivitySimulatorApp(root)
    root.mainloop()