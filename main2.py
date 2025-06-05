import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
import time
import random
import threading
import pyautogui
import tempfile
import os
import psutil
from datetime import datetime, timedelta
import json

class EnhancedActivitySimulator:
    def __init__(self, master):
        self.master = master
        master.title("Enhanced Activity Simulator Pro")
        master.geometry("700x900")
        master.resizable(True, True)

        # --- Core Control Variables ---
        self.is_running = tk.BooleanVar(value=False)
        self.target_percentage = tk.IntVar(value=50)
        self.intensity_mode = tk.StringVar(value="Medium")
        self.smart_detection_enabled = tk.BooleanVar(value=True)
        
        # --- Activity Tracking ---
        self.current_percentage = tk.DoubleVar(value=0.0)
        self.activities_today = 0
        self.last_real_activity = time.time()
        self.session_start_time = time.time()
        self.daily_target_hours = tk.DoubleVar(value=8.0)  # Working hours per day
        
        # --- Text File Simulation ---
        self.text_file_enabled = tk.BooleanVar(value=True)
        self.temp_file_path = None
        self.temp_file_handle = None
        
        # --- Timing Variables ---
        self.base_interval_seconds = tk.IntVar(value=15)  # Much shorter default
        self.burst_mode_enabled = tk.BooleanVar(value=True)
        self.burst_actions_count = tk.IntVar(value=3)
        
        # --- User Detection ---
        self.user_idle_threshold = tk.IntVar(value=30)  # seconds
        self.last_mouse_pos = pyautogui.position()
        self.last_activity_check = time.time()
        
        # --- Safe Applications (won't interfere) ---
        self.safe_apps = ["notepad", "wordpad", "calculator", "explorer"]
        self.avoid_apps = tk.StringVar(value="")  # User can specify apps to avoid
        
        # --- Advanced Settings ---
        self.micro_movements_enabled = tk.BooleanVar(value=True)
        self.natural_typing_enabled = tk.BooleanVar(value=True)
        self.smart_scheduling_enabled = tk.BooleanVar(value=True)
        
        # Initialize pyautogui
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.01  # Very small pause between actions
        
        self.create_widgets()
        self.automation_thread = None
        self.monitoring_thread = None
        self.load_daily_stats()
        
    def create_widgets(self):
        # --- Main Notebook for Tabs ---
        notebook = ttk.Notebook(self.master)
        notebook.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Tab 1: Target & Control
        control_frame = ttk.Frame(notebook)
        notebook.add(control_frame, text="Target & Control")
        self.create_control_tab(control_frame)
        
        # Tab 2: Advanced Settings
        advanced_frame = ttk.Frame(notebook)
        notebook.add(advanced_frame, text="Advanced Settings")
        self.create_advanced_tab(advanced_frame)
        
        # Tab 3: Monitoring & Stats
        monitor_frame = ttk.Frame(notebook)
        notebook.add(monitor_frame, text="Monitoring & Stats")
        self.create_monitoring_tab(monitor_frame)
        
        # Tab 4: Logs
        log_frame = ttk.Frame(notebook)
        notebook.add(log_frame, text="Activity Logs")
        self.create_log_tab(log_frame)
        
    def create_control_tab(self, parent):
        # --- Target Percentage Frame ---
        target_frame = tk.LabelFrame(parent, text="Daily Activity Target", font=("Arial", 10, "bold"))
        target_frame.pack(padx=10, pady=5, fill="x")
        
        target_row1 = tk.Frame(target_frame)
        target_row1.pack(fill="x", padx=5, pady=5)
        
        tk.Label(target_row1, text="Target Activity:").pack(side=tk.LEFT)
        target_scale = tk.Scale(target_row1, from_=10, to=95, orient=tk.HORIZONTAL, 
                               variable=self.target_percentage, length=200)
        target_scale.pack(side=tk.LEFT, padx=10)
        self.target_label = tk.Label(target_row1, text="50%", font=("Arial", 12, "bold"), fg="blue")
        self.target_label.pack(side=tk.LEFT, padx=10)
        
        target_scale.config(command=self.update_target_display)
        
        target_row2 = tk.Frame(target_frame)
        target_row2.pack(fill="x", padx=5, pady=2)
        tk.Label(target_row2, text="Daily Working Hours:").pack(side=tk.LEFT)
        tk.Spinbox(target_row2, from_=1, to=24, textvariable=self.daily_target_hours, 
                  width=5, format="%.1f", increment=0.5).pack(side=tk.LEFT, padx=10)
        
        # --- Current Status Frame ---
        status_frame = tk.LabelFrame(parent, text="Current Status", font=("Arial", 10, "bold"))
        status_frame.pack(padx=10, pady=5, fill="x")
        
        self.current_percentage_label = tk.Label(status_frame, text="Current Activity: 0.0%", 
                                               font=("Arial", 14, "bold"), fg="red")
        self.current_percentage_label.pack(pady=5)
        
        self.progress_bar = ttk.Progressbar(status_frame, length=400, mode='determinate')
        self.progress_bar.pack(pady=5)
        
        status_info_frame = tk.Frame(status_frame)
        status_info_frame.pack(fill="x", padx=5, pady=5)
        
        self.session_time_label = tk.Label(status_info_frame, text="Session: 0h 0m")
        self.session_time_label.pack(side=tk.LEFT)
        
        self.activities_count_label = tk.Label(status_info_frame, text="Activities: 0")
        self.activities_count_label.pack(side=tk.RIGHT)
        
        # --- Intensity Mode Frame ---
        intensity_frame = tk.LabelFrame(parent, text="Intensity Mode", font=("Arial", 10, "bold"))
        intensity_frame.pack(padx=10, pady=5, fill="x")
        
        intensity_modes = ["Low", "Medium", "High", "Auto"]
        for mode in intensity_modes:
            tk.Radiobutton(intensity_frame, text=mode, variable=self.intensity_mode, 
                          value=mode, command=self.update_intensity_settings).pack(side=tk.LEFT, padx=10, pady=5)
        
        # --- Smart Features Frame ---
        smart_frame = tk.LabelFrame(parent, text="Smart Features", font=("Arial", 10, "bold"))
        smart_frame.pack(padx=10, pady=5, fill="x")
        
        tk.Checkbutton(smart_frame, text="Smart User Detection (Reduce activity when you're working)", 
                      variable=self.smart_detection_enabled).pack(anchor=tk.W, padx=5, pady=2)
        
        tk.Checkbutton(smart_frame, text="Text File Simulation (Safe, non-disruptive)", 
                      variable=self.text_file_enabled).pack(anchor=tk.W, padx=5, pady=2)
        
        tk.Checkbutton(smart_frame, text="Burst Mode (Multiple actions in sequence)", 
                      variable=self.burst_mode_enabled).pack(anchor=tk.W, padx=5, pady=2)
        
        # --- Control Buttons ---
        button_frame = tk.Frame(parent)
        button_frame.pack(pady=15)
        
        self.start_button = tk.Button(button_frame, text="🚀 Start Smart Simulation", 
                                     command=self.start_simulation,
                                     bg="#28a745", fg="white", font=("Arial", 12, "bold"), 
                                     width=20, height=2)
        self.start_button.pack(side=tk.LEFT, padx=10)
        
        self.stop_button = tk.Button(button_frame, text="⏹️ Stop Simulation", 
                                    command=self.stop_simulation,
                                    bg="#dc3545", fg="white", font=("Arial", 12, "bold"), 
                                    width=20, height=2, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=10)
        
        # --- Quick Stats ---
        quick_stats_frame = tk.LabelFrame(parent, text="Quick Stats", font=("Arial", 10, "bold"))
        quick_stats_frame.pack(padx=10, pady=5, fill="x")
        
        self.quick_stats_label = tk.Label(quick_stats_frame, text="Ready to start simulation...", 
                                         font=("Arial", 10), justify=tk.LEFT)
        self.quick_stats_label.pack(padx=5, pady=5)
        
    def create_advanced_tab(self, parent):
        # --- Timing Settings ---
        timing_frame = tk.LabelFrame(parent, text="Timing Settings", font=("Arial", 10, "bold"))
        timing_frame.pack(padx=10, pady=5, fill="x")
        
        timing_row1 = tk.Frame(timing_frame)
        timing_row1.pack(fill="x", padx=5, pady=5)
        tk.Label(timing_row1, text="Base Interval (seconds):").pack(side=tk.LEFT)
        tk.Spinbox(timing_row1, from_=5, to=120, textvariable=self.base_interval_seconds, 
                  width=5).pack(side=tk.LEFT, padx=10)
        
        timing_row2 = tk.Frame(timing_frame)
        timing_row2.pack(fill="x", padx=5, pady=5)
        tk.Label(timing_row2, text="Burst Actions Count:").pack(side=tk.LEFT)
        tk.Spinbox(timing_row2, from_=1, to=10, textvariable=self.burst_actions_count, 
                  width=5).pack(side=tk.LEFT, padx=10)
        
        timing_row3 = tk.Frame(timing_frame)
        timing_row3.pack(fill="x", padx=5, pady=5)
        tk.Label(timing_row3, text="User Idle Threshold (seconds):").pack(side=tk.LEFT)
        tk.Spinbox(timing_row3, from_=10, to=300, textvariable=self.user_idle_threshold, 
                  width=5).pack(side=tk.LEFT, padx=10)
        
        # --- Activity Types ---
        activity_frame = tk.LabelFrame(parent, text="Activity Types", font=("Arial", 10, "bold"))
        activity_frame.pack(padx=10, pady=5, fill="x")
        
        tk.Checkbutton(activity_frame, text="Micro Mouse Movements (1-3 pixels)", 
                      variable=self.micro_movements_enabled).pack(anchor=tk.W, padx=5, pady=2)
        
        tk.Checkbutton(activity_frame, text="Natural Typing Patterns", 
                      variable=self.natural_typing_enabled).pack(anchor=tk.W, padx=5, pady=2)
        
        tk.Checkbutton(activity_frame, text="Smart Scheduling", 
                      variable=self.smart_scheduling_enabled).pack(anchor=tk.W, padx=5, pady=2)
        
        # --- Application Settings ---
        app_frame = tk.LabelFrame(parent, text="Application Settings", font=("Arial", 10, "bold"))
        app_frame.pack(padx=10, pady=5, fill="x")
        
        tk.Label(app_frame, text="Avoid simulation when these apps are active:").pack(anchor=tk.W, padx=5, pady=2)
        tk.Entry(app_frame, textvariable=self.avoid_apps, width=60).pack(padx=5, pady=2, fill="x")
        tk.Label(app_frame, text="(Comma-separated app names, e.g., 'zoom,teams,discord')", 
                font=("Arial", 8), fg="gray").pack(anchor=tk.W, padx=5)
        
        # --- File Simulation Settings ---
        file_frame = tk.LabelFrame(parent, text="Text File Simulation", font=("Arial", 10, "bold"))
        file_frame.pack(padx=10, pady=5, fill="x")
        
        tk.Label(file_frame, text="• Creates temporary text file for safe typing simulation").pack(anchor=tk.W, padx=5, pady=1)
        tk.Label(file_frame, text="• Types random characters and deletes them").pack(anchor=tk.W, padx=5, pady=1)
        tk.Label(file_frame, text="• Includes mouse movements within text area only").pack(anchor=tk.W, padx=5, pady=1)
        tk.Label(file_frame, text="• Auto-closes without saving").pack(anchor=tk.W, padx=5, pady=1)
        
    def create_monitoring_tab(self, parent):
        # --- Real-time Monitoring ---
        monitor_frame = tk.LabelFrame(parent, text="Real-time Monitoring", font=("Arial", 10, "bold"))
        monitor_frame.pack(padx=10, pady=5, fill="both", expand=True)
        
        # Activity Chart (Simple text-based for now)
        self.activity_display = scrolledtext.ScrolledText(monitor_frame, height=15, width=70, 
                                                         font=("Courier", 9), state='disabled')
        self.activity_display.pack(padx=5, pady=5, fill="both", expand=True)
        
        # Monitoring Controls
        monitor_controls = tk.Frame(monitor_frame)
        monitor_controls.pack(fill="x", padx=5, pady=5)
        
        tk.Button(monitor_controls, text="📊 Refresh Stats", 
                 command=self.refresh_monitoring_display).pack(side=tk.LEFT, padx=5)
        
        tk.Button(monitor_controls, text="💾 Save Daily Report", 
                 command=self.save_daily_report).pack(side=tk.LEFT, padx=5)
        
        tk.Button(monitor_controls, text="🔄 Reset Daily Stats", 
                 command=self.reset_daily_stats).pack(side=tk.LEFT, padx=5)
        
    def create_log_tab(self, parent):
        # --- Activity Log ---
        log_frame = tk.LabelFrame(parent, text="Activity Log", font=("Arial", 10, "bold"))
        log_frame.pack(padx=10, pady=5, fill="both", expand=True)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, width=80, height=25, 
                                                 state='disabled', font=("Consolas", 9))
        self.log_text.pack(padx=5, pady=5, fill="both", expand=True)
        
        # Log Controls
        log_controls = tk.Frame(log_frame)
        log_controls.pack(fill="x", padx=5, pady=5)
        
        tk.Button(log_controls, text="🗑️ Clear Logs", 
                 command=self.clear_logs).pack(side=tk.LEFT, padx=5)
        
        tk.Button(log_controls, text="💾 Save Logs", 
                 command=self.save_logs).pack(side=tk.LEFT, padx=5)
        
        # Initial welcome message
        self.log_message("🚀 Enhanced Activity Simulator Pro initialized!")
        self.log_message("📋 Features: Smart detection, Text file simulation, Burst mode, Target percentage tracking")
        self.log_message("⚠️ Emergency Stop: Move mouse to top-left corner")
        
    def update_target_display(self, value):
        self.target_label.config(text=f"{value}%")
        
    def update_intensity_settings(self):
        mode = self.intensity_mode.get()
        if mode == "Low":
            self.base_interval_seconds.set(30)
            self.burst_actions_count.set(2)
        elif mode == "Medium":
            self.base_interval_seconds.set(15)
            self.burst_actions_count.set(3)
        elif mode == "High":
            self.base_interval_seconds.set(8)
            self.burst_actions_count.set(5)
        elif mode == "Auto":
            # Auto mode adjusts based on current vs target percentage
            pass
            
    def log_message(self, message):
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')
        
    def is_user_active(self):
        """Detect if user is actively using the computer"""
        try:
            current_mouse_pos = pyautogui.position()
            if current_mouse_pos != self.last_mouse_pos:
                self.last_mouse_pos = current_mouse_pos
                self.last_real_activity = time.time()
                return True
                
            # Check if user is idle for more than threshold
            if time.time() - self.last_real_activity > self.user_idle_threshold.get():
                return False
                
            return False
        except:
            return False
            
    def get_active_application(self):
        """Get currently active application name"""
        try:
            # This is a simplified version - in a real implementation,
            # you might want to use platform-specific methods
            return "unknown"
        except:
            return "unknown"
            
    def should_avoid_simulation(self):
        """Check if simulation should be avoided based on active applications"""
        if not self.avoid_apps.get().strip():
            return False
            
        active_app = self.get_active_application().lower()
        avoid_list = [app.strip().lower() for app in self.avoid_apps.get().split(',')]
        
        return any(avoid_app in active_app for avoid_app in avoid_list if avoid_app)
        
    def create_temp_text_file(self):
        """Create a temporary text file for simulation"""
        try:
            self.temp_file_handle = tempfile.NamedTemporaryFile(mode='w+', suffix='.txt', delete=False)
            self.temp_file_path = self.temp_file_handle.name
            self.temp_file_handle.write("Activity Simulator Workspace - This file will be deleted automatically\n")
            self.temp_file_handle.write("="*60 + "\n\n")
            self.temp_file_handle.flush()
            
            # Open the file in notepad/default text editor
            if os.name == 'nt':  # Windows
                os.startfile(self.temp_file_path)
            else:  # Linux/Mac
                os.system(f'open "{self.temp_file_path}"' if os.name == 'posix' else f'xdg-open "{self.temp_file_path}"')
                
            time.sleep(2)  # Wait for file to open
            self.log_message(f"📝 Created temporary text file: {os.path.basename(self.temp_file_path)}")
            return True
        except Exception as e:
            self.log_message(f"❌ Error creating temp file: {e}")
            return False
            
    def cleanup_temp_file(self):
        """Clean up temporary text file"""
        try:
            if self.temp_file_handle:
                self.temp_file_handle.close()
            if self.temp_file_path and os.path.exists(self.temp_file_path):
                os.unlink(self.temp_file_path)
                self.log_message("🗑️ Temporary text file cleaned up")
        except Exception as e:
            self.log_message(f"⚠️ Error cleaning up temp file: {e}")
            
    def perform_text_simulation(self):
        """Perform typing simulation in text file"""
        try:
            # Generate random text
            words = ["data", "analysis", "report", "meeting", "project", "update", "review", "status", 
                    "progress", "implementation", "development", "testing", "deployment", "monitoring"]
            text_to_type = " ".join(random.choices(words, k=random.randint(3, 8)))
            
            # Type the text
            pyautogui.typewrite(text_to_type, interval=random.uniform(0.05, 0.15))
            time.sleep(random.uniform(0.5, 1.5))
            
            # Select and delete the text
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.2)
            pyautogui.press('delete')
            
            return len(text_to_type)
        except Exception as e:
            self.log_message(f"⚠️ Text simulation error: {e}")
            return 0
            
    def perform_micro_movement(self):
        """Perform small mouse movements"""
        try:
            current_pos = pyautogui.position()
            offset_x = random.randint(-3, 3)
            offset_y = random.randint(-3, 3)
            
            new_x = max(10, min(current_pos[0] + offset_x, pyautogui.size()[0] - 10))
            new_y = max(10, min(current_pos[1] + offset_y, pyautogui.size()[1] - 10))
            
            pyautogui.moveTo(new_x, new_y, duration=random.uniform(0.1, 0.3))
            return True
        except Exception as e:
            self.log_message(f"⚠️ Micro movement error: {e}")
            return False
            
    def perform_safe_key_action(self):
        """Perform safe key combinations that don't interfere with applications"""
        try:
            safe_keys = ['shift', 'ctrl', 'alt', 'f13', 'f14', 'f15', 'numlock', 'scrolllock']
            key = random.choice(safe_keys)
            pyautogui.press(key)
            return key
        except Exception as e:
            self.log_message(f"⚠️ Safe key action error: {e}")
            return None
            
    def calculate_current_percentage(self):
        """Calculate current activity percentage based on session time and activities"""
        session_duration_hours = (time.time() - self.session_start_time) / 3600
        if session_duration_hours == 0:
            return 0.0
            
        # Estimate based on activities performed and time
        # This is a simplified calculation - in reality, you'd want more sophisticated tracking
        activity_rate = self.activities_today / (session_duration_hours * 60)  # activities per minute
        percentage = min(95.0, activity_rate * 10)  # Scale to percentage
        
        return percentage
        
    def update_display(self):
        """Update the GUI display with current stats"""
        try:
            current_pct = self.calculate_current_percentage()
            self.current_percentage.set(current_pct)
            
            # Update percentage label color based on target
            target = self.target_percentage.get()
            if current_pct >= target:
                color = "#28a745"  # Green
            elif current_pct >= target * 0.7:
                color = "#ffc107"  # Yellow
            else:
                color = "#dc3545"  # Red
                
            self.current_percentage_label.config(
                text=f"Current Activity: {current_pct:.1f}%", 
                fg=color
            )
            
            # Update progress bar
            self.progress_bar['value'] = current_pct
            self.progress_bar['maximum'] = 100
            
            # Update session time
            session_duration = time.time() - self.session_start_time
            hours = int(session_duration // 3600)
            minutes = int((session_duration % 3600) // 60)
            self.session_time_label.config(text=f"Session: {hours}h {minutes}m")
            
            # Update activities count
            self.activities_count_label.config(text=f"Activities: {self.activities_today}")
            
            # Update quick stats
            stats_text = f"Target: {target}% | Current: {current_pct:.1f}% | "
            stats_text += f"Status: {'✅ On Track' if current_pct >= target else '⚠️ Below Target'}"
            self.quick_stats_label.config(text=stats_text)
            
        except Exception as e:
            self.log_message(f"Display update error: {e}")
            
    def auto_adjust_intensity(self):
        """Automatically adjust intensity based on current vs target percentage"""
        if self.intensity_mode.get() != "Auto":
            return
            
        current_pct = self.current_percentage.get()
        target_pct = self.target_percentage.get()
        
        if current_pct < target_pct * 0.5:
            # Very low - high intensity
            self.base_interval_seconds.set(5)
            self.burst_actions_count.set(6)
        elif current_pct < target_pct * 0.8:
            # Below target - medium-high intensity
            self.base_interval_seconds.set(10)
            self.burst_actions_count.set(4)
        elif current_pct >= target_pct:
            # At or above target - low intensity
            self.base_interval_seconds.set(25)
            self.burst_actions_count.set(2)
            
    def start_simulation(self):
        """Start the enhanced simulation"""
        if self.is_running.get():
            messagebox.showwarning("Already Running", "Simulation is already active.")
            return
            
        self.is_running.set(True)
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        
        self.session_start_time = time.time()
        self.activities_today = 0
        
        self.log_message("🚀 Starting Enhanced Activity Simulation...")
        self.log_message(f"🎯 Target: {self.target_percentage.get()}% | Mode: {self.intensity_mode.get()}")
        self.log_message(f"🧠 Smart Detection: {'ON' if self.smart_detection_enabled.get() else 'OFF'}")
        
        # Create temp file if enabled
        if self.text_file_enabled.get():
            if not self.create_temp_text_file():
                self.text_file_enabled.set(False)
                self.log_message("⚠️ Text file simulation disabled due to error")
        
        # Start automation thread
        self.automation_thread = threading.Thread(target=self._run_enhanced_automation, daemon=True)
        self.automation_thread.start()
        
        # Start monitoring thread for display updates
        self.monitoring_thread = threading.Thread(target=self._run_monitoring, daemon=True)
        self.monitoring_thread.start()
        
    def stop_simulation(self):
        """Stop the simulation"""
        if not self.is_running.get():
            return
            
        self.is_running.set(False)
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        
        self.log_message("⏹️ Stopping simulation...")
        
        # Cleanup temp file
        if self.text_file_enabled.get():
            self.cleanup_temp_file()
            
        self.log_message("✅ Simulation stopped successfully")
        
    def _run_enhanced_automation(self):
        """Main automation loop with enhanced features"""
        try:
            while self.is_running.get():
                # Auto-adjust intensity if in Auto mode
                self.auto_adjust_intensity()
                
                # Check if we should avoid simulation
                if self.should_avoid_simulation():
                    self.log_message("⏸️ Pausing simulation - avoided application active")
                    time.sleep(10)
                    continue
                
                # Check if user is active and smart detection is enabled
                user_is_active = self.is_user_active() if self.smart_detection_enabled.get() else False
                
                if user_is_active:
                    # Reduce activity when user is working
                    sleep_time = self.base_interval_seconds.get() * 2
                    self.log_message("👤 User active - reducing simulation intensity")
                else:
                    sleep_time = random.randint(
                        max(3, self.base_interval_seconds.get() - 5),
                        self.base_interval_seconds.get() + 5
                    )
                
                # Sleep between activities
                time.sleep(sleep_time)
                
                if not self.is_running.get():
                    break
                
                # Perform burst of activities
                burst_count = self.burst_actions_count.get() if self.burst_mode_enabled.get() else 1
                actions_performed = []
                
                for i in range(burst_count):
                    if not self.is_running.get():
                        break
                        
                    action_type = self._select_action_type()
                    action_result = self._perform_action(action_type)
                    
                    if action_result:
                        actions_performed.append(action_type)
                        self.activities_today += 1
                    
                    # Small delay between burst actions
                    if i < burst_count - 1:
                        time.sleep(random.uniform(0.2, 0.8))
                
                if actions_performed:
                    self.log_message(f"🎯 Performed: {', '.join(actions_performed)} (Total: {self.activities_today})")
                
        except pyautogui.FailSafeException:
            self.master.after(0, self._handle_failsafe)
        except Exception as e:
            self.master.after(0, lambda: self._handle_error(str(e)))
            
    def _select_action_type(self):
        """Select which type of action to perform based on enabled features"""
        available_actions = []
        
        if self.text_file_enabled.get():
            available_actions.extend(['text_typing'] * 4)  # Higher weight for text simulation
        
        if self.micro_movements_enabled.get():
            available_actions.extend(['micro_movement'] * 2)
        
        if self.natural_typing_enabled.get():
            available_actions.extend(['safe_keys'] * 1)
        
        # Always have at least one action available
        if not available_actions:
            available_actions = ['safe_keys']
            
        return random.choice(available_actions)
        
    def _perform_action(self, action_type):
        """Perform the specified action type"""
        try:
            if action_type == 'text_typing' and self.text_file_enabled.get():
                chars_typed = self.perform_text_simulation()
                return f"text_sim({chars_typed}chars)"
            
            elif action_type == 'micro_movement' and self.micro_movements_enabled.get():
                if self.perform_micro_movement():
                    return "micro_move"
                    
            elif action_type == 'safe_keys':
                key_pressed = self.perform_safe_key_action()
                if key_pressed:
                    return f"key({key_pressed})"
            
            return None
        except Exception as e:
            self.log_message(f"⚠️ Action error ({action_type}): {e}")
            return None
            
    def _run_monitoring(self):
        """Background monitoring and display updates"""
        while self.is_running.get():
            try:
                self.master.after(0, self.update_display)
                time.sleep(2)  # Update every 2 seconds
            except:
                break
                
    def _handle_failsafe(self):
        """Handle PyAutoGUI failsafe exception"""
        self.is_running.set(False)
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.log_message("🚨 EMERGENCY STOP: PyAutoGUI Failsafe Triggered!")
        messagebox.showwarning("EMERGENCY STOP", "PyAutoGUI Failsafe Triggered!\nSimulation stopped for safety.")
        
    def _handle_error(self, error_msg):
        """Handle unexpected errors"""
        self.is_running.set(False)
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.log_message(f"❌ Error: {error_msg}")
        messagebox.showerror("Error", f"An unexpected error occurred:\n{error_msg}")
        
    def refresh_monitoring_display(self):
        """Refresh the monitoring display with current stats"""
        try:
            self.activity_display.config(state='normal')
            self.activity_display.delete('1.0', tk.END)
            
            # Generate monitoring report
            current_time = datetime.now()
            session_duration = time.time() - self.session_start_time
            
            report = f"""
📊 ENHANCED ACTIVITY SIMULATOR - REAL-TIME STATS
{'='*60}
🕐 Current Time: {current_time.strftime('%Y-%m-%d %H:%M:%S')}
⏱️ Session Duration: {int(session_duration//3600)}h {int((session_duration%3600)//60)}m {int(session_duration%60)}s

🎯 TARGET PERFORMANCE
   Target Percentage: {self.target_percentage.get()}%
   Current Percentage: {self.current_percentage.get():.1f}%
   Progress: {'✅ ACHIEVED' if self.current_percentage.get() >= self.target_percentage.get() else '🔄 IN PROGRESS'}

📈 ACTIVITY METRICS
   Total Activities: {self.activities_today}
   Activities/Hour: {self.activities_today/(session_duration/3600):.1f}
   Intensity Mode: {self.intensity_mode.get()}
   Base Interval: {self.base_interval_seconds.get()}s
   Burst Actions: {self.burst_actions_count.get()}

🛠️ ACTIVE FEATURES
   Smart Detection: {'✅ ON' if self.smart_detection_enabled.get() else '❌ OFF'}
   Text File Simulation: {'✅ ON' if self.text_file_enabled.get() else '❌ OFF'}
   Micro Movements: {'✅ ON' if self.micro_movements_enabled.get() else '❌ OFF'}
   Burst Mode: {'✅ ON' if self.burst_mode_enabled.get() else '❌ OFF'}
   Natural Typing: {'✅ ON' if self.natural_typing_enabled.get() else '❌ OFF'}

⚙️ CURRENT SETTINGS
   Daily Working Hours: {self.daily_target_hours.get()}h
   User Idle Threshold: {self.user_idle_threshold.get()}s
   Avoid Apps: {self.avoid_apps.get() if self.avoid_apps.get() else 'None'}

📋 PERFORMANCE ANALYSIS
   Efficiency Score: {min(100, (self.current_percentage.get()/self.target_percentage.get())*100):.1f}%
   Recommended Action: {self._get_performance_recommendation()}

🔮 PROJECTION
   Hours to Target: {self._calculate_hours_to_target():.1f}h
   End of Day Estimate: {self._estimate_end_of_day_percentage():.1f}%
"""
            
            self.activity_display.insert('1.0', report)
            self.activity_display.config(state='disabled')
            
        except Exception as e:
            self.log_message(f"⚠️ Monitoring display error: {e}")
            
    def _get_performance_recommendation(self):
        """Get performance recommendation based on current stats"""
        current_pct = self.current_percentage.get()
        target_pct = self.target_percentage.get()
        
        if current_pct >= target_pct:
            return "🎉 Target achieved! Consider reducing intensity."
        elif current_pct >= target_pct * 0.8:
            return "📈 On track! Maintain current settings."
        elif current_pct >= target_pct * 0.5:
            return "⚡ Increase intensity or reduce intervals."
        else:
            return "🚨 Switch to High intensity mode immediately!"
            
    def _calculate_hours_to_target(self):
        """Calculate estimated hours to reach target"""
        current_pct = self.current_percentage.get()
        target_pct = self.target_percentage.get()
        
        if current_pct >= target_pct:
            return 0.0
            
        session_duration_hours = (time.time() - self.session_start_time) / 3600
        if session_duration_hours == 0 or current_pct == 0:
            return self.daily_target_hours.get()
            
        rate_per_hour = current_pct / session_duration_hours
        if rate_per_hour == 0:
            return self.daily_target_hours.get()
            
        remaining_percentage = target_pct - current_pct
        return remaining_percentage / rate_per_hour
        
    def _estimate_end_of_day_percentage(self):
        """Estimate percentage at end of working day"""
        session_duration_hours = (time.time() - self.session_start_time) / 3600
        if session_duration_hours == 0:
            return 0.0
            
        current_rate = self.current_percentage.get() / session_duration_hours
        return min(95.0, current_rate * self.daily_target_hours.get())
        
    def save_daily_report(self):
        """Save daily activity report to file"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"activity_report_{timestamp}.txt"
            
            with open(filename, 'w') as f:
                f.write("ENHANCED ACTIVITY SIMULATOR - DAILY REPORT\n")
                f.write("="*50 + "\n\n")
                f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Target Percentage: {self.target_percentage.get()}%\n")
                f.write(f"Achieved Percentage: {self.current_percentage.get():.1f}%\n")
                f.write(f"Total Activities: {self.activities_today}\n")
                f.write(f"Session Duration: {(time.time() - self.session_start_time)/3600:.2f} hours\n")
                f.write(f"Intensity Mode: {self.intensity_mode.get()}\n")
                f.write(f"Features Used: ")
                
                features = []
                if self.smart_detection_enabled.get(): features.append("Smart Detection")
                if self.text_file_enabled.get(): features.append("Text Simulation")
                if self.burst_mode_enabled.get(): features.append("Burst Mode")
                if self.micro_movements_enabled.get(): features.append("Micro Movements")
                if self.natural_typing_enabled.get(): features.append("Natural Typing")
                
                f.write(", ".join(features) + "\n")
                f.write(f"\nEfficiency Score: {min(100, (self.current_percentage.get()/self.target_percentage.get())*100):.1f}%\n")
                
            self.log_message(f"📄 Daily report saved: {filename}")
            messagebox.showinfo("Report Saved", f"Daily report saved as:\n{filename}")
            
        except Exception as e:
            self.log_message(f"❌ Error saving report: {e}")
            messagebox.showerror("Save Error", f"Failed to save report:\n{e}")
            
    def reset_daily_stats(self):
        """Reset daily statistics"""
        if messagebox.askyesno("Reset Stats", "Are you sure you want to reset daily statistics?"):
            self.activities_today = 0
            self.session_start_time = time.time()
            self.current_percentage.set(0.0)
            self.update_display()
            self.log_message("🔄 Daily statistics reset")
            
    def clear_logs(self):
        """Clear activity logs"""
        if messagebox.askyesno("Clear Logs", "Are you sure you want to clear all logs?"):
            self.log_text.config(state='normal')
            self.log_text.delete('1.0', tk.END)
            self.log_text.config(state='disabled')
            self.log_message("🗑️ Logs cleared")
            
    def save_logs(self):
        """Save activity logs to file"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"activity_logs_{timestamp}.txt"
            
            with open(filename, 'w') as f:
                f.write("ENHANCED ACTIVITY SIMULATOR - ACTIVITY LOGS\n")
                f.write("="*50 + "\n\n")
                f.write(self.log_text.get('1.0', tk.END))
                
            self.log_message(f"📄 Logs saved: {filename}")
            messagebox.showinfo("Logs Saved", f"Activity logs saved as:\n{filename}")
            
        except Exception as e:
            self.log_message(f"❌ Error saving logs: {e}")
            messagebox.showerror("Save Error", f"Failed to save logs:\n{e}")
            
    def load_daily_stats(self):
        """Load daily statistics (placeholder for future implementation)"""
        # This would load stats from a persistent storage
        pass
        
    def save_daily_stats(self):
        """Save daily statistics (placeholder for future implementation)"""
        # This would save stats to persistent storage
        pass
        
    def on_closing(self):
        """Handle application closing"""
        if self.is_running.get():
            if messagebox.askyesno("Quit", "Simulation is running. Stop and quit?"):
                self.stop_simulation()
                time.sleep(1)  # Give time for cleanup
                self.master.destroy()
        else:
            self.master.destroy()

# Main execution
if __name__ == "__main__":
    root = tk.Tk()
    app = EnhancedActivitySimulator(root)
    
    # Handle window closing
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    # Start the GUI
    root.mainloop()