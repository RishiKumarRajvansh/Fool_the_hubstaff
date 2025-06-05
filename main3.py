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
import subprocess
import platform

# For better user activity detection and window management
try:
    if platform.system() == "Windows":
        import win32api
        import win32gui
        import win32con
        from ctypes import Structure, windll, c_uint, sizeof, byref
        
        class LASTINPUTINFO(Structure):
            _fields_ = [('cbSize', c_uint), ('dwTime', c_uint)]
            
        def get_idle_duration():
            """Get actual system idle time in seconds"""
            lastInputInfo = LASTINPUTINFO()
            lastInputInfo.cbSize = sizeof(lastInputInfo)
            windll.user32.GetLastInputInfo(byref(lastInputInfo))
            millis = windll.kernel32.GetTickCount() - lastInputInfo.dwTime
            return millis / 1000.0
            
        def is_screen_locked():
            """Check if Windows screen is locked"""
            try:
                hwnd = win32gui.GetForegroundWindow()
                if hwnd == 0:
                    return True
                try:
                    win32gui.GetWindowText(hwnd)
                    return False
                except:
                    return True
            except:
                return True
                
        def activate_window_by_title(title_part):
            """Activate window containing title_part"""
            try:
                def enum_windows_callback(hwnd, windows):
                    if win32gui.IsWindowVisible(hwnd):
                        window_title = win32gui.GetWindowText(hwnd)
                        if title_part.lower() in window_title.lower():
                            windows.append((hwnd, window_title))
                    return True
                
                windows = []
                win32gui.EnumWindows(enum_windows_callback, windows)
                
                if windows:
                    hwnd = windows[0][0]
                    if win32gui.IsIconic(hwnd):
                        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                    win32gui.SetForegroundWindow(hwnd)
                    win32gui.BringWindowToTop(hwnd)
                    return True
                return False
            except Exception as e:
                print(f"Error activating window: {e}")
                return False
                
        def check_process_running(process):
            """Check if a process is still running"""
            try:
                if process and process.poll() is None:
                    return True
                return False
            except:
                return False
                
        def find_text_file_windows(filename):
            """Find all windows with the text file open"""
            try:
                def enum_windows_callback(hwnd, windows):
                    if win32gui.IsWindowVisible(hwnd):
                        window_title = win32gui.GetWindowText(hwnd)
                        if filename.lower() in window_title.lower() or "notepad" in window_title.lower():
                            windows.append((hwnd, window_title))
                    return True
                
                windows = []
                win32gui.EnumWindows(enum_windows_callback, windows)
                return windows
            except:
                return []
                
    else:
        def get_idle_duration():
            return 0
        def is_screen_locked():
            return False
        def activate_window_by_title(title_part):
            return False
        def check_process_running(process):
            return False
        def find_text_file_windows(filename):
            return []
            
except ImportError:
    def get_idle_duration():
        return 0
    def is_screen_locked():
        return False
    def activate_window_by_title(title_part):
        return False
    def check_process_running(process):
        return False
    def find_text_file_windows(filename):
        return []

class EnhancedActivitySimulator:
    def __init__(self, master):
        self.master = master
        master.title("Enhanced Activity Simulator Pro - File Recovery Edition")
        master.geometry("750x1000")
        master.resizable(True, True)

        # --- Core Control Variables ---
        self.is_running = tk.BooleanVar(value=False)
        self.is_paused = tk.BooleanVar(value=False)
        self.target_percentage = tk.IntVar(value=50)
        self.intensity_mode = tk.StringVar(value="Medium")
        self.smart_detection_enabled = tk.BooleanVar(value=True)
        
        # --- Auto-Pause Settings ---
        self.auto_pause_enabled = tk.BooleanVar(value=True)
        self.auto_pause_threshold = tk.IntVar(value=10)
        self.auto_resume_threshold = tk.IntVar(value=180)
        self.pause_start_time = 0
        self.pause_history = []
        
        # --- Auto-Activation Settings ---
        self.auto_activate_enabled = tk.BooleanVar(value=True)
        self.work_when_locked = tk.BooleanVar(value=True)
        self.activation_check_interval = tk.IntVar(value=30)
        self.last_activation_attempt = 0
        self.lock_screen_mode = False
        
        # --- File Recovery Settings (NEW) ---
        self.auto_file_recovery = tk.BooleanVar(value=True)
        self.file_check_interval = tk.IntVar(value=15)  # seconds
        self.max_recovery_attempts = tk.IntVar(value=3)
        self.last_file_check = 0
        self.file_recovery_count = 0
        self.backup_file_paths = []  # Keep track of created files
        
        # --- Activity Tracking ---
        self.current_percentage = tk.DoubleVar(value=0.0)
        self.activities_today = 0
        self.last_real_activity = time.time()
        self.session_start_time = time.time()
        self.daily_target_hours = tk.DoubleVar(value=8.0)
        self.total_pause_time = 0
        
        # --- Enhanced User Detection ---
        self.last_system_idle_time = 0
        self.last_mouse_pos = pyautogui.position()
        self.last_keyboard_activity = time.time()
        self.our_last_mouse_movement = time.time()
        self.user_idle_threshold = tk.IntVar(value=30)
        
        # --- Mouse Movement Settings ---
        self.mouse_movement_type = tk.StringVar(value="Full Screen")
        self.mouse_movement_distance = tk.IntVar(value=50)
        self.visible_movements = tk.BooleanVar(value=True)
        
        # --- Text File Simulation ---
        self.text_file_enabled = tk.BooleanVar(value=True)
        self.temp_file_path = None
        self.temp_file_handle = None
        self.text_editor_process = None
        self.our_window_title = None
        self.window_hwnd = None
        self.file_session_id = None  # Unique session identifier
        
        # --- Timing Variables ---
        self.base_interval_seconds = tk.IntVar(value=15)
        self.burst_mode_enabled = tk.BooleanVar(value=True)
        self.burst_actions_count = tk.IntVar(value=3)
        
        # --- Safe Applications ---
        self.safe_apps = ["notepad", "wordpad", "calculator", "explorer"]
        self.avoid_apps = tk.StringVar(value="")
        
        # --- Advanced Settings ---
        self.micro_movements_enabled = tk.BooleanVar(value=False)
        self.full_screen_movements_enabled = tk.BooleanVar(value=True)
        self.natural_typing_enabled = tk.BooleanVar(value=True)
        self.smart_scheduling_enabled = tk.BooleanVar(value=True)
        
        # Initialize pyautogui
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.01
        
        self.create_widgets()
        self.automation_thread = None
        self.monitoring_thread = None
        self.activation_thread = None
        self.file_monitor_thread = None  # NEW
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
        
        # --- File Recovery Settings Frame (NEW) ---
        filerecovery_frame = tk.LabelFrame(parent, text="File Recovery Settings", font=("Arial", 10, "bold"))
        filerecovery_frame.pack(padx=10, pady=5, fill="x")
        
        tk.Checkbutton(filerecovery_frame, text="Auto File Recovery (recreate text file if closed)", 
                      variable=self.auto_file_recovery).pack(anchor=tk.W, padx=5, pady=2)
        
        filerecovery_row1 = tk.Frame(filerecovery_frame)
        filerecovery_row1.pack(fill="x", padx=5, pady=2)
        tk.Label(filerecovery_row1, text="Check file status every:").pack(side=tk.LEFT)
        tk.Spinbox(filerecovery_row1, from_=5, to=60, textvariable=self.file_check_interval, 
                  width=5).pack(side=tk.LEFT, padx=5)
        tk.Label(filerecovery_row1, text="seconds").pack(side=tk.LEFT)
        
        filerecovery_row2 = tk.Frame(filerecovery_frame)
        filerecovery_row2.pack(fill="x", padx=5, pady=2)
        tk.Label(filerecovery_row2, text="Max recovery attempts:").pack(side=tk.LEFT)
        tk.Spinbox(filerecovery_row2, from_=1, to=10, textvariable=self.max_recovery_attempts, 
                  width=5).pack(side=tk.LEFT, padx=5)
        tk.Label(filerecovery_row2, text="per session").pack(side=tk.LEFT)
        
        # --- Auto-Activation Settings Frame ---
        autoactivation_frame = tk.LabelFrame(parent, text="Auto-Activation Settings", font=("Arial", 10, "bold"))
        autoactivation_frame.pack(padx=10, pady=5, fill="x")
        
        tk.Checkbutton(autoactivation_frame, text="Auto-Activate Text File (bring to foreground when inactive)", 
                      variable=self.auto_activate_enabled).pack(anchor=tk.W, padx=5, pady=2)
        
        tk.Checkbutton(autoactivation_frame, text="Work When Screen Locked (continue simulation in background)", 
                      variable=self.work_when_locked).pack(anchor=tk.W, padx=5, pady=2)
        
        autoactivation_row1 = tk.Frame(autoactivation_frame)
        autoactivation_row1.pack(fill="x", padx=5, pady=2)
        tk.Label(autoactivation_row1, text="Check activation every:").pack(side=tk.LEFT)
        tk.Spinbox(autoactivation_row1, from_=10, to=120, textvariable=self.activation_check_interval, 
                  width=5).pack(side=tk.LEFT, padx=5)
        tk.Label(autoactivation_row1, text="seconds").pack(side=tk.LEFT)
        
        # --- Auto-Pause Settings Frame ---
        autopause_frame = tk.LabelFrame(parent, text="Auto-Pause Settings", font=("Arial", 10, "bold"))
        autopause_frame.pack(padx=10, pady=5, fill="x")
        
        tk.Checkbutton(autopause_frame, text="Enable Auto-Pause (pause when user is active)", 
                      variable=self.auto_pause_enabled).pack(anchor=tk.W, padx=5, pady=2)
        
        autopause_row1 = tk.Frame(autopause_frame)
        autopause_row1.pack(fill="x", padx=5, pady=2)
        tk.Label(autopause_row1, text="Pause after user active for:").pack(side=tk.LEFT)
        tk.Spinbox(autopause_row1, from_=5, to=60, textvariable=self.auto_pause_threshold, 
                  width=5).pack(side=tk.LEFT, padx=5)
        tk.Label(autopause_row1, text="seconds").pack(side=tk.LEFT)
        
        autopause_row2 = tk.Frame(autopause_frame)
        autopause_row2.pack(fill="x", padx=5, pady=2)
        tk.Label(autopause_row2, text="Resume after user idle for:").pack(side=tk.LEFT)
        tk.Spinbox(autopause_row2, from_=60, to=600, textvariable=self.auto_resume_threshold, 
                  width=5).pack(side=tk.LEFT, padx=5)
        tk.Label(autopause_row2, text="seconds").pack(side=tk.LEFT)
        
        # --- Current Status Frame ---
        status_frame = tk.LabelFrame(parent, text="Current Status", font=("Arial", 10, "bold"))
        status_frame.pack(padx=10, pady=5, fill="x")
        
        self.current_percentage_label = tk.Label(status_frame, text="Current Activity: 0.0%", 
                                               font=("Arial", 14, "bold"), fg="red")
        self.current_percentage_label.pack(pady=5)
        
        self.progress_bar = ttk.Progressbar(status_frame, length=400, mode='determinate')
        self.progress_bar.pack(pady=5)
        
        # --- File Status (NEW) ---
        self.file_status_label = tk.Label(status_frame, text="File: Not Created", 
                                        font=("Arial", 10, "bold"), fg="gray")
        self.file_status_label.pack(pady=2)
        
        # --- System Status ---
        self.system_status_label = tk.Label(status_frame, text="System: Ready", 
                                          font=("Arial", 10, "bold"), fg="blue")
        self.system_status_label.pack(pady=2)
        
        # --- Pause Status ---
        self.pause_status_label = tk.Label(status_frame, text="Status: Ready", 
                                         font=("Arial", 12, "bold"), fg="blue")
        self.pause_status_label.pack(pady=3)
        
        # --- User Activity Status ---
        user_status_frame = tk.Frame(status_frame)
        user_status_frame.pack(fill="x", padx=5, pady=5)
        
        self.user_activity_label = tk.Label(user_status_frame, text="User Status: Checking...", 
                                          font=("Arial", 10, "bold"))
        self.user_activity_label.pack(side=tk.LEFT)
        
        self.idle_time_label = tk.Label(user_status_frame, text="Idle: 0s")
        self.idle_time_label.pack(side=tk.RIGHT)
        
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
        
        tk.Checkbutton(smart_frame, text="Smart User Detection (Real system idle time detection)", 
                      variable=self.smart_detection_enabled).pack(anchor=tk.W, padx=5, pady=2)
        
        tk.Checkbutton(smart_frame, text="Text File Simulation (Safe, dedicated file only)", 
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
        
        # Manual pause/resume buttons
        button_frame2 = tk.Frame(parent)
        button_frame2.pack(pady=5)
        
        self.manual_pause_button = tk.Button(button_frame2, text="⏸️ Manual Pause", 
                                           command=self.manual_pause,
                                           bg="#ffc107", fg="black", font=("Arial", 10), 
                                           width=15, state=tk.DISABLED)
        self.manual_pause_button.pack(side=tk.LEFT, padx=5)
        
        self.manual_resume_button = tk.Button(button_frame2, text="▶️ Manual Resume", 
                                            command=self.manual_resume,
                                            bg="#17a2b8", fg="white", font=("Arial", 10), 
                                            width=15, state=tk.DISABLED)
        self.manual_resume_button.pack(side=tk.LEFT, padx=5)
        
        # Test and recovery buttons (NEW)
        self.test_activation_button = tk.Button(button_frame2, text="🔄 Test Activation", 
                                              command=self.test_window_activation,
                                              bg="#6f42c1", fg="white", font=("Arial", 10), 
                                              width=15)
        self.test_activation_button.pack(side=tk.LEFT, padx=5)
        
        # File recovery button (NEW)
        button_frame3 = tk.Frame(parent)
        button_frame3.pack(pady=2)
        
        self.force_recovery_button = tk.Button(button_frame3, text="🔧 Force File Recovery", 
                                             command=self.force_file_recovery,
                                             bg="#fd7e14", fg="white", font=("Arial", 10), 
                                             width=20)
        self.force_recovery_button.pack(side=tk.LEFT, padx=5)
        
        self.check_file_button = tk.Button(button_frame3, text="📋 Check File Status", 
                                         command=self.check_file_status,
                                         bg="#20c997", fg="white", font=("Arial", 10), 
                                         width=20)
        self.check_file_button.pack(side=tk.LEFT, padx=5)
        
        # --- Quick Stats ---
        quick_stats_frame = tk.LabelFrame(parent, text="Quick Stats", font=("Arial", 10, "bold"))
        quick_stats_frame.pack(padx=10, pady=5, fill="x")
        
        self.quick_stats_label = tk.Label(quick_stats_frame, text="Ready to start simulation...", 
                                         font=("Arial", 10), justify=tk.LEFT)
        self.quick_stats_label.pack(padx=5, pady=5)

    def create_advanced_tab(self, parent):
        # --- File Recovery Settings (NEW) ---
        recovery_frame = tk.LabelFrame(parent, text="File Recovery & Monitoring", font=("Arial", 10, "bold"))
        recovery_frame.pack(padx=10, pady=5, fill="x")
        
        tk.Label(recovery_frame, text="• Automatically detects when text file is closed", 
                font=("Arial", 9)).pack(anchor=tk.W, padx=5, pady=1)
        tk.Label(recovery_frame, text="• Recreates file or reopens existing file if found", 
                font=("Arial", 9)).pack(anchor=tk.W, padx=5, pady=1)
        tk.Label(recovery_frame, text="• Monitors process status and window availability", 
                font=("Arial", 9)).pack(anchor=tk.W, padx=5, pady=1)
        tk.Label(recovery_frame, text="• Maintains backup file paths for recovery", 
                font=("Arial", 9)).pack(anchor=tk.W, padx=5, pady=1)
        tk.Label(recovery_frame, text="• Logs all recovery attempts and results", 
                font=("Arial", 9)).pack(anchor=tk.W, padx=5, pady=1)
        
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
        
        # --- Mouse Movement Settings ---
        mouse_frame = tk.LabelFrame(parent, text="Mouse Movement Settings", font=("Arial", 10, "bold"))
        mouse_frame.pack(padx=10, pady=5, fill="x")
        
        mouse_row1 = tk.Frame(mouse_frame)
        mouse_row1.pack(fill="x", padx=5, pady=5)
        tk.Label(mouse_row1, text="Movement Type:").pack(side=tk.LEFT)
        movement_types = ["Micro (3px)", "Small (25px)", "Medium (50px)", "Large (100px)", "Full Screen"]
        movement_combo = ttk.Combobox(mouse_row1, textvariable=self.mouse_movement_type, 
                                    values=movement_types, state="readonly", width=15)
        movement_combo.pack(side=tk.LEFT, padx=10)
        
        mouse_row2 = tk.Frame(mouse_frame)
        mouse_row2.pack(fill="x", padx=5, pady=5)
        tk.Label(mouse_row2, text="Max Distance (pixels):").pack(side=tk.LEFT)
        tk.Spinbox(mouse_row2, from_=5, to=500, textvariable=self.mouse_movement_distance, 
                  width=8).pack(side=tk.LEFT, padx=10)
        
        tk.Checkbutton(mouse_frame, text="Make movements visible (slower but obvious)", 
                      variable=self.visible_movements).pack(anchor=tk.W, padx=5, pady=2)
        
        # --- Activity Types ---
        activity_frame = tk.LabelFrame(parent, text="Activity Types", font=("Arial", 10, "bold"))
        activity_frame.pack(padx=10, pady=5, fill="x")
        
        tk.Checkbutton(activity_frame, text="Micro Mouse Movements (1-3 pixels)", 
                      variable=self.micro_movements_enabled).pack(anchor=tk.W, padx=5, pady=2)
        
        tk.Checkbutton(activity_frame, text="Full Screen Mouse Movements (visible)", 
                      variable=self.full_screen_movements_enabled).pack(anchor=tk.W, padx=5, pady=2)
        
        tk.Checkbutton(activity_frame, text="Natural Typing Patterns", 
                      variable=self.natural_typing_enabled).pack(anchor=tk.W, padx=5, pady=2)
        
        tk.Checkbutton(activity_frame, text="Smart Scheduling", 
                      variable=self.smart_scheduling_enabled).pack(anchor=tk.W, padx=5, pady=2)
        
        # --- Lock Screen Mode Settings ---
        lock_frame = tk.LabelFrame(parent, text="Lock Screen Mode Settings", font=("Arial", 10, "bold"))
        lock_frame.pack(padx=10, pady=5, fill="x")
        
        tk.Label(lock_frame, text="• When screen is locked, simulation continues in background").pack(anchor=tk.W, padx=5, pady=1)
        tk.Label(lock_frame, text="• Uses safe key presses and minimal mouse movements").pack(anchor=tk.W, padx=5, pady=1)
        tk.Label(lock_frame, text="• Automatically detects lock/unlock state").pack(anchor=tk.W, padx=5, pady=1)
        tk.Label(lock_frame, text="• Text file operations pause during lock screen").pack(anchor=tk.W, padx=5, pady=1)
        
        # --- Application Settings ---
        app_frame = tk.LabelFrame(parent, text="Application Settings", font=("Arial", 10, "bold"))
        app_frame.pack(padx=10, pady=5, fill="x")
        
        tk.Label(app_frame, text="Avoid simulation when these apps are active:").pack(anchor=tk.W, padx=5, pady=2)
        tk.Entry(app_frame, textvariable=self.avoid_apps, width=60).pack(padx=5, pady=2, fill="x")
        tk.Label(app_frame, text="(Comma-separated app names, e.g., 'zoom,teams,discord')", 
                font=("Arial", 8), fg="gray").pack(anchor=tk.W, padx=5)

    def create_monitoring_tab(self, parent):
        # --- Real-time Monitoring ---
        monitor_frame = tk.LabelFrame(parent, text="Real-time Monitoring & Statistics", font=("Arial", 10, "bold"))
        monitor_frame.pack(padx=10, pady=5, fill="both", expand=True)
        
        # Activity Display
        self.activity_display = scrolledtext.ScrolledText(monitor_frame, height=20, width=80, 
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
        
        tk.Button(monitor_controls, text="🖱️ Test Mouse Movement", 
                 command=self.test_mouse_movement).pack(side=tk.LEFT, padx=5)
        
        # Auto-refresh the monitoring display
        self.refresh_monitoring_display()

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
        
        tk.Button(log_controls, text="💾 Save Logs", 
                 command=self.save_logs).pack(side=tk.LEFT, padx=5)
        
        tk.Button(log_controls, text="🔄 Export Session Log", 
                 command=self.export_session_log).pack(side=tk.LEFT, padx=5)
        
        # Initial welcome message
        self.log_message("🚀 Enhanced Activity Simulator Pro - File Recovery Edition initialized!")
        self.log_message("📋 Features: Auto-recovery, Auto-activation, Lock screen support, Auto-pause/resume")
        self.log_message("⚠️ Emergency Stop: Move mouse to top-left corner")
        self.log_message("🔧 File Recovery: Automatically recreates text file if closed")
        self.log_message("🔄 Auto-activation will keep text file engaged")
        self.log_message("🔒 Lock screen mode will continue simulation in background")
        self.log_message(f"👤 Current User: RishiKumarRajvansh")
        self.log_message(f"🕐 Session Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # === NEW FILE RECOVERY METHODS ===
    
    def check_file_status(self):
        """Check current file status and display information"""
        try:
            if not self.our_window_title:
                self.log_message("📋 No text file created yet")
                messagebox.showinfo("File Status", "No text file has been created yet.\nStart simulation to create a file.")
                return
                
            # Check if file exists on disk
            file_exists = self.temp_file_path and os.path.exists(self.temp_file_path)
            
            # Check if process is running
            process_running = check_process_running(self.text_editor_process)
            
            # Check if window is available
            windows = find_text_file_windows(self.our_window_title)
            window_available = len(windows) > 0
            
            # Check if file is active
            file_active = self.is_our_text_file_active()
            
            status_report = f"""
📋 FILE STATUS REPORT
{'='*40}
File Name: {self.our_window_title}
File Path: {self.temp_file_path if self.temp_file_path else 'None'}
File Session ID: {self.file_session_id if self.file_session_id else 'None'}

FILE EXISTENCE
File Exists on Disk: {'✅ YES' if file_exists else '❌ NO'}
File Size: {os.path.getsize(self.temp_file_path) if file_exists else 'N/A'} bytes

PROCESS STATUS
Editor Process Running: {'✅ YES' if process_running else '❌ NO'}
Process ID: {self.text_editor_process.pid if process_running else 'N/A'}

WINDOW STATUS
Windows Found: {len(windows)}
Window Available: {'✅ YES' if window_available else '❌ NO'}
File Currently Active: {'✅ YES' if file_active else '❌ NO'}

RECOVERY STATUS
Auto Recovery: {'✅ ENABLED' if self.auto_file_recovery.get() else '❌ DISABLED'}
Recovery Attempts: {self.file_recovery_count}/{self.max_recovery_attempts.get()}
Last Check: {time.time() - self.last_file_check:.0f}s ago

BACKUP FILES
Total Backup Files: {len(self.backup_file_paths)}
"""
            
            for i, backup_path in enumerate(self.backup_file_paths[-3:], 1):
                exists = os.path.exists(backup_path)
                status_report += f"Backup {i}: {'✅' if exists else '❌'} {os.path.basename(backup_path)}\n"
                
            self.log_message("📋 File status check completed")
            self.log_message(f"   File exists: {'YES' if file_exists else 'NO'}")
            self.log_message(f"   Process running: {'YES' if process_running else 'NO'}")
            self.log_message(f"   Window available: {'YES' if window_available else 'NO'}")
            
            messagebox.showinfo("File Status Report", status_report)
            
        except Exception as e:
            self.log_message(f"❌ Error checking file status: {e}")
            messagebox.showerror("Status Check Error", f"Failed to check file status:\n{e}")
    
    def force_file_recovery(self):
        """Force immediate file recovery"""
        try:
            if not self.is_running.get():
                self.log_message("⚠️ Cannot force recovery - simulation not running")
                messagebox.showwarning("Not Running", "Simulation must be running to force file recovery.")
                return
                
            self.log_message("🔧 Force file recovery initiated...")
            
            # Reset recovery count for forced recovery
            old_count = self.file_recovery_count
            self.file_recovery_count = 0
            
            success = self.attempt_file_recovery()
            
            if success:
                self.log_message("✅ Force file recovery successful!")
                messagebox.showinfo("Recovery Successful", f"File recovery completed successfully!\nNew file: {self.our_window_title}")
            else:
                self.file_recovery_count = old_count  # Restore count if failed
                self.log_message("❌ Force file recovery failed!")
                messagebox.showerror("Recovery Failed", "File recovery failed. Check logs for details.")
                
        except Exception as e:
            self.log_message(f"❌ Error during force recovery: {e}")
            messagebox.showerror("Recovery Error", f"Error during forced recovery:\n{e}")
    
    def detect_file_closure(self):
        """Detect if the text file has been closed"""
        try:
            if not self.our_window_title or not self.text_file_enabled.get():
                return False
                
            # Skip check during lock screen
            if self.lock_screen_mode:
                return False
                
            # Check multiple indicators
            file_exists = self.temp_file_path and os.path.exists(self.temp_file_path)
            process_running = check_process_running(self.text_editor_process)
            windows_found = find_text_file_windows(self.our_window_title)
            
            # If file doesn't exist OR process is dead OR no windows found
            if not file_exists or not process_running or len(windows_found) == 0:
                self.log_message(f"🔍 File closure detected:")
                self.log_message(f"   File exists: {'YES' if file_exists else 'NO'}")
                self.log_message(f"   Process running: {'YES' if process_running else 'NO'}")
                self.log_message(f"   Windows found: {len(windows_found)}")
                return True
                
            return False
            
        except Exception as e:
            self.log_message(f"⚠️ Error detecting file closure: {e}")
            return False
    
    def attempt_file_recovery(self):
        """Attempt to recover or recreate the text file"""
        try:
            if self.file_recovery_count >= self.max_recovery_attempts.get():
                self.log_message(f"⚠️ Max recovery attempts ({self.max_recovery_attempts.get()}) reached")
                return False
                
            self.file_recovery_count += 1
            self.log_message(f"🔧 Attempting file recovery #{self.file_recovery_count}...")
            
            # First, try to find existing file windows
            windows = find_text_file_windows(self.our_window_title)
            if windows:
                self.log_message(f"🔍 Found existing window: {windows[0][1]}")
                # Try to activate existing window
                if activate_window_by_title(self.our_window_title):
                    self.log_message("✅ Reactivated existing window")
                    return True
            
            # Check if any backup files exist and can be reopened
            for backup_path in reversed(self.backup_file_paths):
                if os.path.exists(backup_path):
                    self.log_message(f"🔍 Found backup file: {os.path.basename(backup_path)}")
                    try:
                        if platform.system() == "Windows":
                            process = subprocess.Popen(['notepad.exe', backup_path])
                            self.text_editor_process = process
                            self.temp_file_path = backup_path
                            self.our_window_title = os.path.basename(backup_path)
                            time.sleep(2)
                            self.log_message("✅ Reopened backup file")
                            return True
                    except Exception as e:
                        self.log_message(f"⚠️ Failed to reopen backup: {e}")
                        continue
            
            # If no existing files, create a new one
            self.log_message("📝 Creating new text file...")
            self.cleanup_temp_file()  # Clean up old references
            
            if self.create_temp_text_file():
                self.log_message("✅ New text file created successfully")
                return True
            else:
                self.log_message("❌ Failed to create new text file")
                return False
                
        except Exception as e:
            self.log_message(f"❌ File recovery error: {e}")
            return False
    
    def monitor_file_status(self):
        """Monitor file status and trigger recovery if needed"""
        try:
            while self.is_running.get():
                if (self.auto_file_recovery.get() and 
                    self.text_file_enabled.get() and 
                    not self.is_paused.get() and 
                    time.time() - self.last_file_check >= self.file_check_interval.get()):
                    
                    self.last_file_check = time.time()
                    
                    if self.detect_file_closure():
                        self.log_message("🚨 File closure detected - initiating recovery...")
                        
                        # Update file status display
                        self.master.after(0, lambda: self.file_status_label.config(
                            text="File: 🔧 RECOVERING", fg="orange"))
                        
                        success = self.attempt_file_recovery()
                        
                        if success:
                            self.log_message("✅ File recovery successful")
                            self.master.after(0, lambda: self.file_status_label.config(
                                text=f"File: ✅ RECOVERED", fg="green"))
                        else:
                            self.log_message("❌ File recovery failed")
                            self.master.after(0, lambda: self.file_status_label.config(
                                text="File: ❌ RECOVERY FAILED", fg="red"))
                
                # Update file status display
                if self.our_window_title:
                    is_active = self.is_our_text_file_active()
                    if self.lock_screen_mode:
                        status = "🔒 LOCKED"
                        color = "purple"
                    elif is_active:
                        status = "🟢 ACTIVE"
                        color = "green"
                    else:
                        status = "🔴 INACTIVE"
                        color = "red"
                    
                    self.master.after(0, lambda: self.file_status_label.config(
                        text=f"File: {status} ({os.path.basename(self.our_window_title)})", fg=color))
                
                time.sleep(2)  # Check every 2 seconds
                
        except Exception as e:
            self.log_message(f"⚠️ File monitoring error: {e}")
    
    # === ENHANCED EXISTING METHODS ===
    
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
            pass
            
    def log_message(self, message):
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')
        
    def get_real_user_idle_time(self):
        """Get actual system idle time using Windows API"""
        try:
            idle_time = get_idle_duration()
            return idle_time
        except:
            # Fallback method
            current_mouse_pos = pyautogui.position()
            if current_mouse_pos != self.last_mouse_pos:
                if time.time() - self.our_last_mouse_movement > 2:
                    self.last_real_activity = time.time()
                    self.last_mouse_pos = current_mouse_pos
                    return 0
            
            return time.time() - self.last_real_activity
            
    def check_screen_lock_state(self):
        """Check and update screen lock state"""
        try:
            is_locked = is_screen_locked()
            if is_locked != self.lock_screen_mode:
                self.lock_screen_mode = is_locked
                if is_locked:
                    self.log_message("🔒 Screen locked - entering lock screen mode")
                    self.master.after(0, lambda: self.system_status_label.config(
                        text="System: 🔒 LOCKED", fg="orange"))
                else:
                    self.log_message("🔓 Screen unlocked - resuming normal mode")
                    self.master.after(0, lambda: self.system_status_label.config(
                        text="System: 🔓 UNLOCKED", fg="green"))
            
            return is_locked
        except Exception as e:
            self.log_message(f"⚠️ Error checking lock state: {e}")
            return False
            
    def check_and_activate_text_file(self):
        """Check if text file is active and activate it if needed"""
        if not self.auto_activate_enabled.get() or not self.our_window_title:
            return False
            
        try:
            # Don't try to activate during lock screen
            if self.lock_screen_mode:
                return False
                
            # Check if enough time has passed since last activation attempt
            if time.time() - self.last_activation_attempt < self.activation_check_interval.get():
                return False
                
            # Check if our text file is currently active
            if not self.is_our_text_file_active():
                self.log_message(f"🔄 Text file inactive - attempting activation: {self.our_window_title}")
                
                # Try to activate the window
                success = activate_window_by_title(self.our_window_title)
                
                if success:
                    self.log_message("✅ Text file activated successfully")
                    time.sleep(1)  # Give it time to activate
                    return True
                else:
                    self.log_message("⚠️ Failed to activate text file - checking if file was closed")
                    # If activation fails, check if file was closed
                    if self.detect_file_closure():
                        self.log_message("🔍 File appears to be closed - recovery will handle this")
                    
                self.last_activation_attempt = time.time()
                
            return False
        except Exception as e:
            self.log_message(f"⚠️ Error during activation: {e}")
            return False
            
    def test_window_activation(self):
        """Test window activation functionality"""
        if not self.our_window_title:
            self.log_message("⚠️ No text file created yet - cannot test activation")
            messagebox.showwarning("No Text File", "Please start simulation first to create a text file.")
            return
            
        self.log_message("🧪 Testing window activation...")
        
        # First check if file is still available
        if self.detect_file_closure():
            self.log_message("⚠️ File appears to be closed - testing recovery instead")
            success = self.attempt_file_recovery()
            if success:
                self.log_message("✅ File recovery test successful!")
                messagebox.showinfo("Recovery Test Successful", f"File was closed but successfully recovered:\n{self.our_window_title}")
            else:
                self.log_message("❌ File recovery test failed!")
                messagebox.showerror("Recovery Test Failed", f"File was closed and recovery failed.")
            return
        
        # Test normal activation
        success = activate_window_by_title(self.our_window_title)
        
        if success:
            self.log_message("✅ Window activation test successful!")
            messagebox.showinfo("Test Successful", f"Successfully activated window: {self.our_window_title}")
        else:
            self.log_message("❌ Window activation test failed!")
            messagebox.showerror("Test Failed", f"Failed to activate window: {self.our_window_title}")
            
    def check_auto_pause_resume(self):
        """Check if we should auto-pause or auto-resume"""
        if not self.auto_pause_enabled.get() or not self.is_running.get():
            return
            
        # Don't auto-pause during lock screen mode
        if self.lock_screen_mode and self.work_when_locked.get():
            return
            
        idle_time = self.get_real_user_idle_time()
        
        # Auto-pause logic: pause if user is active for too long
        if not self.is_paused.get() and idle_time < self.auto_pause_threshold.get():
            # User has been active, consider pausing
            if hasattr(self, 'user_active_start'):
                if time.time() - self.user_active_start > self.auto_pause_threshold.get():
                    self.auto_pause("User activity detected")
            else:
                self.user_active_start = time.time()
        elif idle_time >= self.auto_pause_threshold.get():
            # User is idle, reset the active timer
            if hasattr(self, 'user_active_start'):
                delattr(self, 'user_active_start')
            
            # Auto-resume logic: resume if user is idle for long enough
            if self.is_paused.get() and idle_time >= self.auto_resume_threshold.get():
                self.auto_resume("User idle timeout reached")
                
    def auto_pause(self, reason):
        """Automatically pause the simulation"""
        if self.is_paused.get():
            return
            
        self.is_paused.set(True)
        self.pause_start_time = time.time()
        
        # Log the pause event
        pause_event = {
            'type': 'auto_pause',
            'time': datetime.now().strftime('%H:%M:%S'),
            'reason': reason
        }
        self.pause_history.append(pause_event)
        
        self.log_message(f"⏸️ AUTO-PAUSE: {reason}")
        self.update_pause_status()
        
    def auto_resume(self, reason):
        """Automatically resume the simulation"""
        if not self.is_paused.get():
            return
            
        self.is_paused.set(False)
        
        # Calculate pause duration
        if self.pause_start_time > 0:
            pause_duration = time.time() - self.pause_start_time
            self.total_pause_time += pause_duration
            
        # Log the resume event
        resume_event = {
            'type': 'auto_resume',
            'time': datetime.now().strftime('%H:%M:%S'),
            'reason': reason,
            'pause_duration': pause_duration if self.pause_start_time > 0 else 0
        }
        self.pause_history.append(resume_event)
        
        self.log_message(f"▶️ AUTO-RESUME: {reason} (paused for {pause_duration:.0f}s)")
        self.pause_start_time = 0
        self.update_pause_status()
        
    def manual_pause(self):
        """Manually pause the simulation"""
        if not self.is_running.get() or self.is_paused.get():
            return
            
        self.is_paused.set(True)
        self.pause_start_time = time.time()
        
        pause_event = {
            'type': 'manual_pause',
            'time': datetime.now().strftime('%H:%M:%S'),
            'reason': 'User manual pause'
        }
        self.pause_history.append(pause_event)
        
        self.log_message("⏸️ MANUAL PAUSE: Simulation paused by user")
        self.update_pause_status()
        
    def manual_resume(self):
        """Manually resume the simulation"""
        if not self.is_running.get() or not self.is_paused.get():
            return
            
        self.is_paused.set(False)
        
        if self.pause_start_time > 0:
            pause_duration = time.time() - self.pause_start_time
            self.total_pause_time += pause_duration
        
        resume_event = {
            'type': 'manual_resume',
            'time': datetime.now().strftime('%H:%M:%S'),
            'reason': 'User manual resume',
            'pause_duration': pause_duration if self.pause_start_time > 0 else 0
        }
        self.pause_history.append(resume_event)
        
        self.log_message(f"▶️ MANUAL RESUME: Simulation resumed by user (paused for {pause_duration:.0f}s)")
        self.pause_start_time = 0
        self.update_pause_status()
        
    def update_pause_status(self):
        """Update the pause status display"""
        if not self.is_running.get():
            self.pause_status_label.config(text="Status: Stopped", fg="gray")
            self.manual_pause_button.config(state=tk.DISABLED)
            self.manual_resume_button.config(state=tk.DISABLED)
        elif self.is_paused.get():
            pause_duration = int(time.time() - self.pause_start_time) if self.pause_start_time > 0 else 0
            self.pause_status_label.config(text=f"Status: ⏸️ PAUSED ({pause_duration}s)", fg="orange")
            self.manual_pause_button.config(state=tk.DISABLED)
            self.manual_resume_button.config(state=tk.NORMAL)
        else:
            if self.lock_screen_mode:
                self.pause_status_label.config(text="Status: 🔒 LOCK MODE", fg="purple")
            else:
                self.pause_status_label.config(text="Status: ▶️ ACTIVE", fg="green")
            self.manual_pause_button.config(state=tk.NORMAL)
            self.manual_resume_button.config(state=tk.DISABLED)
            
    def is_user_active(self):
        """Enhanced user activity detection using system idle time"""
        try:
            idle_time = self.get_real_user_idle_time()
            threshold = self.user_idle_threshold.get()
            
            # Update the idle time display
            self.master.after(0, lambda: self.idle_time_label.config(text=f"Idle: {idle_time:.0f}s"))
            
            is_active = idle_time < threshold
            
            # Update user status display
            if is_active:
                self.master.after(0, lambda: self.user_activity_label.config(
                    text="User Status: 🟢 ACTIVE", fg="green"))
            else:
                self.master.after(0, lambda: self.user_activity_label.config(
                    text="User Status: 🔴 IDLE", fg="red"))
            
            return is_active
        except Exception as e:
            self.log_message(f"⚠️ User detection error: {e}")
            return False
            
    def get_active_window_title(self):
        """Get the title of the currently active window"""
        try:
            if platform.system() == "Windows":
                import win32gui
                hwnd = win32gui.GetForegroundWindow()
                return win32gui.GetWindowText(hwnd)
            else:
                return "unknown"
        except ImportError:
            return "unknown"
        except:
            return "unknown"
            
    def should_avoid_simulation(self):
        """Check if simulation should be avoided based on active applications"""
        if not self.avoid_apps.get().strip():
            return False
            
        # Skip this check during lock screen mode
        if self.lock_screen_mode:
            return False
            
        active_window = self.get_active_window_title().lower()
        avoid_list = [app.strip().lower() for app in self.avoid_apps.get().split(',')]
        
        return any(avoid_app in active_window for avoid_app in avoid_list if avoid_app)
        
    def create_temp_text_file(self):
        """Create a temporary text file for simulation with unique identification"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            self.file_session_id = f"Session_{timestamp}_{random.randint(1000, 9999)}"
            
            self.temp_file_handle = tempfile.NamedTemporaryFile(
                mode='w+', 
                suffix=f'_ActivitySim_{timestamp}.txt', 
                delete=False,
                prefix='ActivitySimulator_'
            )
            self.temp_file_path = self.temp_file_handle.name
            
            # Add to backup files list
            self.backup_file_paths.append(self.temp_file_path)
            
            header_content = f"""Activity Simulator Workspace - {timestamp}
{'='*60}
Enhanced Activity Simulator Pro - File Recovery Edition
User: RishiKumarRajvansh
Session Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Session ID: {self.file_session_id}
Auto-Activation: {'Enabled' if self.auto_activate_enabled.get() else 'Disabled'}
Auto-Recovery: {'Enabled' if self.auto_file_recovery.get() else 'Disabled'}
Lock Screen Mode: {'Enabled' if self.work_when_locked.get() else 'Disabled'}
DO NOT EDIT THIS FILE MANUALLY - IT WILL BE DELETED AUTOMATICALLY
Simulation ID: {timestamp}
Recovery Count: {self.file_recovery_count}
{'='*60}

Working area (content below will be modified automatically):
"""
            self.temp_file_handle.write(header_content)
            self.temp_file_handle.flush()
            
            filename_only = os.path.basename(self.temp_file_path)
            self.our_window_title = filename_only
            
            if platform.system() == "Windows":
                self.text_editor_process = subprocess.Popen(['notepad.exe', self.temp_file_path])
                self.our_window_title = filename_only
            elif platform.system() == "Darwin":
                self.text_editor_process = subprocess.Popen(['open', '-W', self.temp_file_path])
            else:
                self.text_editor_process = subprocess.Popen(['xdg-open', self.temp_file_path])
                
            time.sleep(3)
            self.log_message(f"📝 Created dedicated text file: {filename_only}")
            self.log_message(f"🔄 Auto-activation: {'Enabled' if self.auto_activate_enabled.get() else 'Disabled'}")
            self.log_message(f"🔧 Auto-recovery: {'Enabled' if self.auto_file_recovery.get() else 'Disabled'}")
            self.log_message(f"🆔 Session ID: {self.file_session_id}")
            return True
            
        except Exception as e:
            self.log_message(f"❌ Error creating temp file: {e}")
            return False
            
    def cleanup_temp_file(self):
        """Clean up temporary text file and close associated process"""
        try:
            if self.text_editor_process and self.text_editor_process.poll() is None:
                try:
                    self.text_editor_process.terminate()
                    self.text_editor_process.wait(timeout=5)
                except:
                    try:
                        self.text_editor_process.kill()
                    except:
                        pass
            
            if self.temp_file_handle:
                try:
                    self.temp_file_handle.close()
                except:
                    pass
            
            # Don't delete the file immediately - keep it as backup
            if self.temp_file_path and os.path.exists(self.temp_file_path):
                try:
                    # Keep the file as backup instead of deleting
                    self.log_message(f"💾 Keeping file as backup: {os.path.basename(self.temp_file_path)}")
                except:
                    self.log_message("⚠️ Temporary file marked for deletion on restart")
            
            self.temp_file_path = None
            self.temp_file_handle = None
            self.text_editor_process = None
            self.our_window_title = None
            self.window_hwnd = None
            
        except Exception as e:
            self.log_message(f"⚠️ Error during cleanup: {e}")
            
    def is_our_text_file_active(self):
        """Check if our specific text file window is currently active"""
        if not self.our_window_title:
            return False
            
        # During lock screen, assume it's not active for text operations
        if self.lock_screen_mode:
            return False
            
        try:
            current_window_title = self.get_active_window_title()
            if self.our_window_title in current_window_title:
                return True
            
            filename_base = os.path.splitext(self.our_window_title)[0]
            if filename_base in current_window_title:
                return True
                
            return False
        except:
            return False
            
    def perform_text_simulation(self):
        """Perform typing simulation ONLY in our dedicated text file"""
        try:
            # Skip text simulation during lock screen
            if self.lock_screen_mode:
                self.log_message("🔒 Skipping text simulation - screen locked")
                return 0
                
            # Try to activate the text file first if auto-activation is enabled
            if self.auto_activate_enabled.get():
                self.check_and_activate_text_file()
                time.sleep(0.5)  # Give activation time to complete
            
            # Check if file is still available, trigger recovery if needed
            if self.detect_file_closure():
                self.log_message("🔍 File closure detected during text simulation")
                if self.auto_file_recovery.get():
                    self.log_message("🔧 Attempting automatic recovery...")
                    if self.attempt_file_recovery():
                        self.log_message("✅ File recovered, resuming text simulation")
                        time.sleep(1)  # Give recovery time to complete
                    else:
                        self.log_message("❌ File recovery failed, skipping text simulation")
                        return 0
                else:
                    self.log_message("⚠️ Auto-recovery disabled, skipping text simulation")
                    return 0
            
            if not self.is_our_text_file_active():
                self.log_message("⚠️ Our text file not active - skipping text simulation")
                return 0
            
            words = ["analysis", "report", "meeting", "project", "update", "review", "status", 
                    "progress", "implementation", "development", "testing", "deployment", 
                    "monitoring", "evaluation", "assessment", "documentation", "requirements",
                    "specifications", "planning", "coordination", "collaboration", "optimization",
                    "synchronization", "verification", "validation", "configuration", "maintenance",
                    "integration", "automation", "enhancement", "troubleshooting", "performance"]
            
            sentence_starters = ["The", "This", "Our", "Current", "Recent", "Updated", "New", "Enhanced", "Improved"]
            connectors = ["and", "with", "for", "during", "through", "including", "regarding", "concerning", "involving"]
            
            text_parts = []
            text_parts.append(random.choice(sentence_starters))
            text_parts.append(random.choice(words))
            text_parts.append(random.choice(connectors))
            text_parts.extend(random.choices(words, k=random.randint(2, 5)))
            
            text_to_type = " ".join(text_parts) + "."
            
            # Type with more natural timing
            pyautogui.typewrite(text_to_type, interval=random.uniform(0.08, 0.18))
            time.sleep(random.uniform(1.0, 3.0))
            
            # Select and delete the text
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.3)
            pyautogui.press('delete')
            
            # Sometimes add variety
            if random.random() < 0.3:
                pyautogui.press('enter')
                time.sleep(0.2)
                pyautogui.press('backspace')
            
            self.log_message(f"📝 Text simulation: '{text_to_type[:30]}...' ({len(text_to_type)} chars)")
            return len(text_to_type)
            
        except Exception as e:
            self.log_message(f"⚠️ Text simulation error: {e}")
            return 0
            
    def get_movement_parameters(self):
        """Get movement parameters based on selected type"""
        movement_type = self.mouse_movement_type.get()
        
        # Adjust for lock screen mode - use smaller movements
        if self.lock_screen_mode:
            return {"min_dist": 1, "max_dist": 5, "duration": (0.1, 0.5)}
        
        if "Micro" in movement_type:
            return {"min_dist": 1, "max_dist": 3, "duration": (0.1, 0.3)}
        elif "Small" in movement_type:
            return {"min_dist": 10, "max_dist": 25, "duration": (0.2, 0.5)}
        elif "Medium" in movement_type:
            return {"min_dist": 25, "max_dist": 50, "duration": (0.3, 0.8)}
        elif "Large" in movement_type:
            return {"min_dist": 50, "max_dist": 100, "duration": (0.5, 1.2)}
        elif "Full Screen" in movement_type:
            screen_width, screen_height = pyautogui.size()
            return {"min_dist": 100, "max_dist": min(screen_width//2, screen_height//2), 
                   "duration": (0.8, 2.0)}
        else:
            return {"min_dist": 25, "max_dist": 50, "duration": (0.3, 0.8)}
            
    def perform_mouse_movement(self):
        """Perform mouse movement based on settings"""
        try:
            current_pos = pyautogui.position()
            screen_width, screen_height = pyautogui.size()
            
            params = self.get_movement_parameters()
            
            # During lock screen, use safer movements
            if self.lock_screen_mode:
                offset_x = random.randint(-5, 5)
                offset_y = random.randint(-5, 5)
                
                new_x = max(50, min(current_pos[0] + offset_x, screen_width - 50))
                new_y = max(50, min(current_pos[1] + offset_y, screen_height - 50))
                movement_desc = f"Lock mode movement by ({offset_x}, {offset_y})"
                duration = 0.2
            elif "Full Screen" in self.mouse_movement_type.get():
                new_x = random.randint(50, screen_width - 50)
                new_y = random.randint(50, screen_height - 50)
                movement_desc = f"Full screen to ({new_x}, {new_y})"
                duration = random.uniform(*params["duration"])
            else:
                distance = random.randint(params["min_dist"], params["max_dist"])
                
                offset_x = int(distance * random.uniform(-1, 1))
                offset_y = int(distance * random.uniform(-1, 1))
                
                new_x = max(50, min(current_pos[0] + offset_x, screen_width - 50))
                new_y = max(50, min(current_pos[1] + offset_y, screen_height - 50))
                movement_desc = f"{self.mouse_movement_type.get()} by ({offset_x}, {offset_y})"
                duration = random.uniform(*params["duration"])
            
            if self.visible_movements.get() and not self.lock_screen_mode:
                duration = max(duration, 0.5)
            
            pyautogui.moveTo(new_x, new_y, duration=duration)
            self.our_last_mouse_movement = time.time()
            
            mode_indicator = "🔒" if self.lock_screen_mode else "🖱️"
            self.log_message(f"{mode_indicator} Mouse movement: {movement_desc}, duration: {duration:.1f}s")
            return True
            
        except Exception as e:
            self.log_message(f"⚠️ Mouse movement error: {e}")
            return False
            
    def perform_micro_movement(self):
        """Perform small mouse movements (legacy function)"""
        try:
            current_pos = pyautogui.position()
            
            # Smaller movements during lock screen
            if self.lock_screen_mode:
                offset_x = random.randint(-2, 2)
                offset_y = random.randint(-2, 2)
            else:
                offset_x = random.randint(-3, 3)
                offset_y = random.randint(-3, 3)
            
            new_x = max(10, min(current_pos[0] + offset_x, pyautogui.size()[0] - 10))
            new_y = max(10, min(current_pos[1] + offset_y, pyautogui.size()[1] - 10))
            
            duration = 0.1 if self.lock_screen_mode else random.uniform(0.1, 0.3)
            pyautogui.moveTo(new_x, new_y, duration=duration)
            self.our_last_mouse_movement = time.time()
            return True
        except Exception as e:
            self.log_message(f"⚠️ Micro movement error: {e}")
            return False
            
    def perform_safe_key_action(self):
        """Perform safe key combinations that don't interfere with applications"""
        try:
            # Use even safer keys during lock screen
            if self.lock_screen_mode:
                safe_keys = ['shift', 'ctrl', 'alt', 'numlock', 'scrolllock']
            else:
                safe_keys = ['shift', 'ctrl', 'alt', 'f13', 'f14', 'f15', 'numlock', 'scrolllock']
            
            key = random.choice(safe_keys)
            pyautogui.press(key)
            return key
        except Exception as e:
            self.log_message(f"⚠️ Safe key action error: {e}")
            return None
            
    def test_mouse_movement(self):
        """Test mouse movement to see if it's working properly"""
        if self.is_running.get():
            self.log_message("⚠️ Cannot test while simulation is running")
            return
            
        self.log_message("🧪 Testing mouse movement...")
        movement_worked = self.perform_mouse_movement()
        
        if movement_worked:
            self.log_message("✅ Mouse movement test successful!")
        else:
            self.log_message("❌ Mouse movement test failed!")
            
    def calculate_current_percentage(self):
        """Calculate current activity percentage based on session time and activities"""
        # Get actual active time (excluding pause time)
        total_session_time = time.time() - self.session_start_time
        active_time = total_session_time - self.total_pause_time
        
        # If currently paused, subtract current pause duration
        if self.is_paused.get() and self.pause_start_time > 0:
            current_pause = time.time() - self.pause_start_time
            active_time -= current_pause
            
        session_duration_hours = max(0.001, active_time / 3600)  # Prevent division by zero
        
        if session_duration_hours == 0:
            return 0.0
            
        activity_rate = self.activities_today / (session_duration_hours * 60)
        percentage = min(95.0, activity_rate * 10)
        
        return percentage
        
    def update_display(self):
        """Update the GUI display with current stats"""
        try:
            current_pct = self.calculate_current_percentage()
            self.current_percentage.set(current_pct)
            
            target = self.target_percentage.get()
            if current_pct >= target:
                color = "#28a745"
            elif current_pct >= target * 0.7:
                color = "#ffc107"
            else:
                color = "#dc3545"
                
            self.current_percentage_label.config(
                text=f"Current Activity: {current_pct:.1f}%", 
                fg=color
            )
            
            self.progress_bar['value'] = current_pct
            self.progress_bar['maximum'] = 100
            
            # Update session time (excluding pause time)
            total_session_time = time.time() - self.session_start_time
            active_time = total_session_time - self.total_pause_time
            
            if self.is_paused.get() and self.pause_start_time > 0:
                current_pause = time.time() - self.pause_start_time
                active_time -= current_pause
                
            hours = int(active_time // 3600)
            minutes = int((active_time % 3600) // 60)
            total_hours = int(total_session_time // 3600)
            total_minutes = int((total_session_time % 3600) // 60)
            
            self.session_time_label.config(text=f"Active: {hours}h {minutes}m | Total: {total_hours}h {total_minutes}m")
            
            self.activities_count_label.config(text=f"Activities: {self.activities_today}")
            
            # Update pause status
            self.update_pause_status()
            
            stats_text = f"Target: {target}% | Current: {current_pct:.1f}% | "
            stats_text += f"Status: {'✅ On Track' if current_pct >= target else '⚠️ Below Target'}"
            
            if self.text_file_enabled.get() and self.our_window_title:
                if self.lock_screen_mode:
                    file_status = "🔒 Locked"
                elif self.is_our_text_file_active():
                    file_status = "🟢 Active"
                else:
                    file_status = "🔴 Inactive"
                stats_text += f" | Text File: {file_status}"
                
            if self.is_paused.get():
                stats_text += " | ⏸️ PAUSED"
            elif self.lock_screen_mode:
                stats_text += " | 🔒 LOCK MODE"
                
            # Add recovery info
            if self.file_recovery_count > 0:
                stats_text += f" | 🔧 Recovered: {self.file_recovery_count}"
            
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
            self.base_interval_seconds.set(5)
            self.burst_actions_count.set(6)
        elif current_pct < target_pct * 0.8:
            self.base_interval_seconds.set(10)
            self.burst_actions_count.set(4)
        elif current_pct >= target_pct:
            self.base_interval_seconds.set(25)
            self.burst_actions_count.set(2)
            
    def start_simulation(self):
        """Start the enhanced simulation"""
        if self.is_running.get():
            messagebox.showwarning("Already Running", "Simulation is already active.")
            return
            
        self.is_running.set(True)
        self.is_paused.set(False)
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.manual_pause_button.config(state=tk.NORMAL)
        
        self.session_start_time = time.time()
        self.activities_today = 0
        self.total_pause_time = 0
        self.pause_history = []
        self.lock_screen_mode = False
        self.file_recovery_count = 0  # Reset recovery count
        
        self.log_message("🚀 Starting Enhanced Activity Simulation with File Recovery...")
        self.log_message(f"🎯 Target: {self.target_percentage.get()}% | Mode: {self.intensity_mode.get()}")
        self.log_message(f"🧠 Smart Detection: {'Real System Idle Time' if self.smart_detection_enabled.get() else 'OFF'}")
        self.log_message(f"⏸️ Auto-Pause: {'ON' if self.auto_pause_enabled.get() else 'OFF'}")
        self.log_message(f"🔄 Auto-Activation: {'ON' if self.auto_activate_enabled.get() else 'OFF'}")
        self.log_message(f"🔧 Auto-Recovery: {'ON' if self.auto_file_recovery.get() else 'OFF'}")
        self.log_message(f"🔒 Lock Screen Mode: {'ON' if self.work_when_locked.get() else 'OFF'}")
        self.log_message(f"🖱️ Mouse Movement: {self.mouse_movement_type.get()}")
        
        if self.text_file_enabled.get():
            if not self.create_temp_text_file():
                self.text_file_enabled.set(False)
                self.log_message("⚠️ Text file simulation disabled due to error")
        
        self.automation_thread = threading.Thread(target=self._run_enhanced_automation, daemon=True)
        self.automation_thread.start()
        
        self.monitoring_thread = threading.Thread(target=self._run_monitoring, daemon=True)
        self.monitoring_thread.start()
        
        # Start activation monitoring thread
        if self.auto_activate_enabled.get():
            self.activation_thread = threading.Thread(target=self._run_activation_monitoring, daemon=True)
            self.activation_thread.start()
            
        # Start file monitoring thread (NEW)
        if self.auto_file_recovery.get():
            self.file_monitor_thread = threading.Thread(target=self.monitor_file_status, daemon=True)
            self.file_monitor_thread.start()
        
    def stop_simulation(self):
        """Stop the simulation"""
        if not self.is_running.get():
            return
            
        self.is_running.set(False)
        self.is_paused.set(False)
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.manual_pause_button.config(state=tk.DISABLED)
        self.manual_resume_button.config(state=tk.DISABLED)
        
        self.log_message("⏹️ Stopping simulation...")
        
        if self.text_file_enabled.get():
            self.cleanup_temp_file()
            
        # Final statistics
        total_session_time = time.time() - self.session_start_time
        active_time = total_session_time - self.total_pause_time
        pause_count = len([event for event in self.pause_history if event['type'] in ['auto_pause', 'manual_pause']])
        
        self.log_message(f"📊 Session Summary:")
        self.log_message(f"   Total Time: {total_session_time/60:.1f} minutes")
        self.log_message(f"   Active Time: {active_time/60:.1f} minutes")
        self.log_message(f"   Pause Time: {self.total_pause_time/60:.1f} minutes")
        self.log_message(f"   Pause Events: {pause_count}")
        self.log_message(f"   Activities: {self.activities_today}")
        self.log_message(f"   File Recovery Count: {self.file_recovery_count}")
        self.log_message(f"   Backup Files Created: {len(self.backup_file_paths)}")
        self.log_message(f"   Lock Screen Sessions: {'Yes' if self.lock_screen_mode else 'No'}")
        self.log_message("✅ Simulation stopped successfully")
        
    def _run_activation_monitoring(self):
        """Background thread to monitor and activate text file when needed"""
        try:
            while self.is_running.get():
                if self.auto_activate_enabled.get() and not self.is_paused.get():
                    # Check and activate text file if needed
                    self.check_and_activate_text_file()
                
                # Sleep for the activation check interval
                time.sleep(self.activation_check_interval.get())
        except Exception as e:
            self.log_message(f"⚠️ Activation monitoring error: {e}")
            
    def _run_enhanced_automation(self):
        """Main automation loop with enhanced features and auto-pause"""
        try:
            while self.is_running.get():
                # Check screen lock state
                self.check_screen_lock_state()
                
                # Check auto-pause/resume logic
                self.check_auto_pause_resume()
                
                # If paused, just wait and continue checking
                if self.is_paused.get():
                    time.sleep(1)
                    continue
                
                self.auto_adjust_intensity()
                
                # Skip app avoidance check during lock screen
                if not self.lock_screen_mode and self.should_avoid_simulation():
                    self.log_message("⏸️ Pausing simulation - avoided application active")
                    time.sleep(10)
                    continue
                
                # Determine user activity (but don't reduce intensity if auto-pause is enabled)
                user_is_active = False
                if self.smart_detection_enabled.get() and not self.lock_screen_mode:
                    user_is_active = self.is_user_active()
                
                if user_is_active and not self.auto_pause_enabled.get():
                    # Old behavior: reduce intensity (only if auto-pause is disabled)
                    sleep_time = self.base_interval_seconds.get() * 2
                    self.log_message("👤 User active - reducing simulation intensity")
                else:
                    # Normal sleep time
                    base_interval = self.base_interval_seconds.get()
                    
                    # Adjust timing for lock screen mode
                    if self.lock_screen_mode:
                        base_interval = max(5, base_interval // 2)  # More frequent during lock
                    
                    sleep_time = random.randint(
                        max(3, base_interval - 5),
                        base_interval + 5
                    )
                
                time.sleep(sleep_time)
                
                if not self.is_running.get() or self.is_paused.get():
                    continue
                
                burst_count = self.burst_actions_count.get() if self.burst_mode_enabled.get() else 1
                
                # Reduce burst count during lock screen
                if self.lock_screen_mode:
                    burst_count = min(burst_count, 2)
                
                actions_performed = []
                
                for i in range(burst_count):
                    if not self.is_running.get() or self.is_paused.get():
                        break
                        
                    action_type = self._select_action_type()
                    action_result = self._perform_action(action_type)
                    
                    if action_result:
                        actions_performed.append(action_result)
                        self.activities_today += 1
                    
                    if i < burst_count - 1:
                        time.sleep(random.uniform(0.2, 0.8))
                
                if actions_performed:
                    mode_indicator = "🔒" if self.lock_screen_mode else "🎯"
                    self.log_message(f"{mode_indicator} Performed: {', '.join(actions_performed)} (Total: {self.activities_today})")
                
        except pyautogui.FailSafeException:
            self.master.after(0, self._handle_failsafe)
        except Exception as e:
            self.master.after(0, lambda: self._handle_error(str(e)))
            
    def _select_action_type(self):
        """Select which type of action to perform based on enabled features"""
        available_actions = []
        
        # During lock screen, prioritize safe actions
        if self.lock_screen_mode:
            if self.micro_movements_enabled.get():
                available_actions.extend(['micro_movement'] * 4)
            available_actions.extend(['safe_keys'] * 3)
            if self.full_screen_movements_enabled.get():
                available_actions.extend(['full_mouse_movement'] * 1)
        else:
            # Normal mode - all actions available
            if self.text_file_enabled.get() and self.our_window_title:
                available_actions.extend(['text_typing'] * 4)
            
            if self.full_screen_movements_enabled.get():
                available_actions.extend(['full_mouse_movement'] * 3)
            
            if self.micro_movements_enabled.get():
                available_actions.extend(['micro_movement'] * 2)
            
            if self.natural_typing_enabled.get():
                available_actions.extend(['safe_keys'] * 1)
        
        if not available_actions:
            available_actions = ['safe_keys']
            
        return random.choice(available_actions)
        
    def _perform_action(self, action_type):
        """Perform the specified action type"""
        try:
            if action_type == 'text_typing' and self.text_file_enabled.get() and not self.lock_screen_mode:
                chars_typed = self.perform_text_simulation()
                if chars_typed > 0:
                    return f"text_sim({chars_typed}chars)"
                else:
                    return None
            
            elif action_type == 'full_mouse_movement' and self.full_screen_movements_enabled.get():
                if self.perform_mouse_movement():
                    return f"mouse_move({self.mouse_movement_type.get()})"
                    
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
                # Also auto-refresh monitoring display every 30 seconds
                if int(time.time()) % 30 == 0:
                    self.master.after(0, self.refresh_monitoring_display)
                time.sleep(2)
            except:
                break
                
    def _handle_failsafe(self):
        """Handle PyAutoGUI failsafe exception"""
        self.is_running.set(False)
        self.is_paused.set(False)
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.manual_pause_button.config(state=tk.DISABLED)
        self.manual_resume_button.config(state=tk.DISABLED)
        self.log_message("🚨 EMERGENCY STOP: PyAutoGUI Failsafe Triggered!")
        messagebox.showwarning("EMERGENCY STOP", "PyAutoGUI Failsafe Triggered!\nSimulation stopped for safety.")
        
    def _handle_error(self, error_msg):
        """Handle unexpected errors"""
        self.is_running.set(False)
        self.is_paused.set(False)
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.manual_pause_button.config(state=tk.DISABLED)
        self.manual_resume_button.config(state=tk.DISABLED)
        self.log_message(f"❌ Error: {error_msg}")
        messagebox.showerror("Error", f"An unexpected error occurred:\n{error_msg}")
        
    def refresh_monitoring_display(self):
        """Refresh the monitoring display with current stats - COMPLETE VERSION"""
        try:
            self.activity_display.config(state='normal')
            self.activity_display.delete('1.0', tk.END)
            
            current_time = datetime.now()
            total_session_time = time.time() - self.session_start_time
            active_time = total_session_time - self.total_pause_time
            
            if self.is_paused.get() and self.pause_start_time > 0:
                current_pause = time.time() - self.pause_start_time
                active_time -= current_pause
                
            idle_time = self.get_real_user_idle_time()
            
            file_status = "Not enabled"
            if self.text_file_enabled.get():
                if self.our_window_title:
                    if self.lock_screen_mode:
                        file_status = f"🔒 Locked Mode ({self.our_window_title})"
                    elif self.is_our_text_file_active():
                        file_status = f"✅ Active ({self.our_window_title})"
                    else:
                        file_status = f"⚠️ Inactive ({self.our_window_title})"
                else:
                    file_status = "❌ File not created"
            
            # Generate pause/resume history summary
            pause_events_summary = ""
            recent_events = self.pause_history[-5:] if len(self.pause_history) > 5 else self.pause_history
            for event in recent_events:
                if event['type'] == 'auto_pause':
                    pause_events_summary += f"   {event['time']} - AUTO PAUSE: {event['reason']}\n"
                elif event['type'] == 'auto_resume':
                    pause_events_summary += f"   {event['time']} - AUTO RESUME: {event['reason']}\n"
                elif event['type'] == 'manual_pause':
                    pause_events_summary += f"   {event['time']} - MANUAL PAUSE\n"
                elif event['type'] == 'manual_resume':
                    pause_events_summary += f"   {event['time']} - MANUAL RESUME (paused for {event.get('pause_duration', 0):.0f}s)\n"
            
            if not pause_events_summary:
                pause_events_summary = "   No pause/resume events yet\n"
            
            # Current status
            current_status = "🔴 Stopped"
            if self.is_running.get():
                if self.is_paused.get():
                    current_status = f"⏸️ PAUSED ({int(time.time() - self.pause_start_time) if self.pause_start_time > 0 else 0}s)"
                elif self.lock_screen_mode:
                    current_status = "🔒 LOCK MODE ACTIVE"
                else:
                    current_status = "▶️ ACTIVE"
            
            # Recovery status
            recovery_status = "❌ DISABLED"
            if self.auto_file_recovery.get():
                recovery_status = f"✅ ENABLED ({self.file_recovery_count}/{self.max_recovery_attempts.get()} attempts)"
            
            report = f"""
📊 ENHANCED ACTIVITY SIMULATOR - FILE RECOVERY EDITION
{'='*70}
🕐 Current Time: {current_time.strftime('%Y-%m-%d %H:%M:%S')} UTC
👤 User: RishiKumarRajvansh
🆔 Session ID: {self.file_session_id if self.file_session_id else 'Not assigned'}
⏱️ Session Duration: {int(total_session_time//3600)}h {int((total_session_time%3600)//60)}m {int(total_session_time%60)}s
⚡ Active Time: {int(active_time//3600)}h {int((active_time%3600)//60)}m {int(active_time%60)}s
⏸️ Pause Time: {int(self.total_pause_time//3600)}h {int((self.total_pause_time%3600)//60)}m {int(self.total_pause_time%60)}s

🔄 CURRENT STATUS
   Simulation Status: {current_status}
   Auto-Pause: {'✅ ENABLED' if self.auto_pause_enabled.get() else '❌ DISABLED'}
   Auto-Activation: {'✅ ENABLED' if self.auto_activate_enabled.get() else '❌ DISABLED'}
   Lock Screen Mode: {'✅ ENABLED' if self.work_when_locked.get() else '❌ DISABLED'}
   
🔧 FILE RECOVERY STATUS
   Auto-Recovery: {recovery_status}
   Recovery Count: {self.file_recovery_count}
   Check Interval: {self.file_check_interval.get()}s
   Last File Check: {time.time() - self.last_file_check:.0f}s ago
   Backup Files: {len(self.backup_file_paths)}
   
🔒 SYSTEM STATE
   Screen Status: {'🔒 LOCKED' if self.lock_screen_mode else '🔓 UNLOCKED'}
   Lock Mode Working: {'✅ YES' if self.work_when_locked.get() and self.lock_screen_mode else '❌ NO'}
   
👤 USER ACTIVITY DETECTION
   Current Idle Time: {idle_time:.1f}s
   User Status: {'🟢 ACTIVE' if idle_time < self.user_idle_threshold.get() else '🔴 IDLE'}
   Detection Method: {'Real System API' if platform.system() == 'Windows' else 'Fallback Method'}
   Auto-Pause Threshold: {self.auto_pause_threshold.get()}s
   Auto-Resume Threshold: {self.auto_resume_threshold.get()}s

🎯 TARGET PERFORMANCE
   Target Percentage: {self.target_percentage.get()}%
   Current Percentage: {self.current_percentage.get():.1f}%
   Progress: {'✅ ACHIEVED' if self.current_percentage.get() >= self.target_percentage.get() else '🔄 IN PROGRESS'}
   Efficiency Score: {min(100, (self.current_percentage.get()/max(1, self.target_percentage.get()))*100):.1f}%

📈 ACTIVITY METRICS
   Total Activities: {self.activities_today}
   Activities/Hour (Active): {self.activities_today/(max(0.001, active_time)/3600):.1f}
   Activities/Hour (Total): {self.activities_today/(max(0.001, total_session_time)/3600):.1f}
   Intensity Mode: {self.intensity_mode.get()}
   Base Interval: {self.base_interval_seconds.get()}s
   Burst Actions: {self.burst_actions_count.get()}

🔄 AUTO-ACTIVATION SETTINGS
   Check Interval: {self.activation_check_interval.get()}s
   Last Activation: {time.time() - self.last_activation_attempt:.0f}s ago
   
🖱️ MOUSE MOVEMENT SETTINGS
   Movement Type: {self.mouse_movement_type.get()}
   Max Distance: {self.mouse_movement_distance.get()}px
   Visible Movements: {'✅ ON' if self.visible_movements.get() else '❌ OFF'}
   Full Screen Enabled: {'✅ ON' if self.full_screen_movements_enabled.get() else '❌ OFF'}
   Micro Movements: {'✅ ON' if self.micro_movements_enabled.get() else '❌ OFF'}

🛠️ ACTIVE FEATURES
   Smart Detection: {'✅ Real System Idle Time' if self.smart_detection_enabled.get() else '❌ OFF'}
   Text File Simulation: {'✅ ON' if self.text_file_enabled.get() else '❌ OFF'}
   Text File Status: {file_status}
   Burst Mode: {'✅ ON' if self.burst_mode_enabled.get() else '❌ OFF'}
   Natural Typing: {'✅ ON' if self.natural_typing_enabled.get() else '❌ OFF'}

⏸️ PAUSE/RESUME HISTORY (Last 5 Events)
{pause_events_summary}

⚙️ CURRENT SETTINGS
   Daily Working Hours: {self.daily_target_hours.get()}h
   User Idle Threshold: {self.user_idle_threshold.get()}s
   Avoid Apps: {self.avoid_apps.get() if self.avoid_apps.get() else 'None'}

📋 PERFORMANCE ANALYSIS
   Recommended Action: {self._get_performance_recommendation()}

🔮 PROJECTION
   Hours to Target: {self._calculate_hours_to_target():.1f}h
   End of Day Estimate: {self._estimate_end_of_day_percentage():.1f}%

📊 SESSION STATISTICS
   Pause Events: {len([e for e in self.pause_history if 'pause' in e['type']])}
   Resume Events: {len([e for e in self.pause_history if 'resume' in e['type']])}
   File Recovery Events: {self.file_recovery_count}
   Efficiency: {(active_time/max(0.001, total_session_time))*100:.1f}% active time
   Reliability: {'🟢 HIGH' if self.file_recovery_count <= 2 else '🟡 MEDIUM' if self.file_recovery_count <= 5 else '🔴 LOW'}
"""
            
            self.activity_display.insert('1.0', report)
            self.activity_display.config(state='disabled')
            
        except Exception as e:
            self.log_message(f"⚠️ Monitoring display error: {e}")
            
    def _get_performance_recommendation(self):
        """Get performance recommendation based on current stats"""
        current_pct = self.current_percentage.get()
        target_pct = self.target_percentage.get()
        
        if self.file_recovery_count > 5:
            return "🔧 High recovery count - check file stability"
        elif self.lock_screen_mode:
            return "🔒 Running in lock screen mode - limited actions available"
        elif current_pct >= target_pct:
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
            
        total_session_time = time.time() - self.session_start_time
        active_time = total_session_time - self.total_pause_time
        
        if self.is_paused.get() and self.pause_start_time > 0:
            current_pause = time.time() - self.pause_start_time
            active_time -= current_pause
            
        session_duration_hours = max(0.001, active_time / 3600)
        
        if session_duration_hours == 0 or current_pct == 0:
            return self.daily_target_hours.get()
            
        rate_per_hour = current_pct / session_duration_hours
        if rate_per_hour == 0:
            return self.daily_target_hours.get()
            
        remaining_percentage = target_pct - current_pct
        return remaining_percentage / rate_per_hour
        
    def _estimate_end_of_day_percentage(self):
        """Estimate percentage at end of working day"""
        total_session_time = time.time() - self.session_start_time
        active_time = total_session_time - self.total_pause_time
        
        if self.is_paused.get() and self.pause_start_time > 0:
            current_pause = time.time() - self.pause_start_time
            active_time -= current_pause
            
        session_duration_hours = max(0.001, active_time / 3600)
        
        if session_duration_hours == 0:
            return 0.0
            
        current_rate = self.current_percentage.get() / session_duration_hours
        return min(95.0, current_rate * self.daily_target_hours.get())
        
    def save_daily_report(self):
        """Save daily activity report to file"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"activity_report_{timestamp}.txt"
            
            total_session_time = time.time() - self.session_start_time
            active_time = total_session_time - self.total_pause_time
            
            if self.is_paused.get() and self.pause_start_time > 0:
                current_pause = time.time() - self.pause_start_time
                active_time -= current_pause
            
            with open(filename, 'w') as f:
                f.write("ENHANCED ACTIVITY SIMULATOR - DAILY REPORT\n")
                f.write("="*60 + "\n\n")
                f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC\n")
                f.write(f"User: RishiKumarRajvansh\n")
                f.write(f"Session ID: {self.file_session_id}\n")
                f.write(f"Target Percentage: {self.target_percentage.get()}%\n")
                f.write(f"Achieved Percentage: {self.current_percentage.get():.1f}%\n")
                f.write(f"Total Activities: {self.activities_today}\n")
                f.write(f"Total Session Duration: {total_session_time/3600:.2f} hours\n")
                f.write(f"Active Session Duration: {active_time/3600:.2f} hours\n")
                f.write(f"Pause Duration: {self.total_pause_time/3600:.2f} hours\n")
                f.write(f"Intensity Mode: {self.intensity_mode.get()}\n")
                f.write(f"Mouse Movement Type: {self.mouse_movement_type.get()}\n")
                f.write(f"User Detection: {'Real System API' if platform.system() == 'Windows' else 'Fallback'}\n")
                f.write(f"Auto-Pause Enabled: {'Yes' if self.auto_pause_enabled.get() else 'No'}\n")
                f.write(f"Auto-Activation Enabled: {'Yes' if self.auto_activate_enabled.get() else 'No'}\n")
                f.write(f"Auto-Recovery Enabled: {'Yes' if self.auto_file_recovery.get() else 'No'}\n")
                f.write(f"Lock Screen Mode: {'Yes' if self.work_when_locked.get() else 'No'}\n")
                f.write(f"Had Lock Screen Session: {'Yes' if self.lock_screen_mode else 'No'}\n")
                f.write(f"File Recovery Count: {self.file_recovery_count}\n")
                f.write(f"Backup Files Created: {len(self.backup_file_paths)}\n")
                f.write(f"Text File Used: {self.our_window_title if self.our_window_title else 'None'}\n")
                
                features = []
                if self.smart_detection_enabled.get(): features.append("Smart Detection")
                if self.text_file_enabled.get(): features.append("Text Simulation")
                if self.burst_mode_enabled.get(): features.append("Burst Mode")
                if self.full_screen_movements_enabled.get(): features.append("Full Screen Movements")
                if self.micro_movements_enabled.get(): features.append("Micro Movements")
                if self.natural_typing_enabled.get(): features.append("Natural Typing")
                if self.auto_pause_enabled.get(): features.append("Auto-Pause")
                if self.auto_activate_enabled.get(): features.append("Auto-Activation")
                if self.auto_file_recovery.get(): features.append("Auto-Recovery")
                if self.work_when_locked.get(): features.append("Lock Screen Mode")
                
                f.write(f"Features Used: {', '.join(features)}\n")
                f.write(f"\nEfficiency Score: {min(100, (self.current_percentage.get()/max(1, self.target_percentage.get()))*100):.1f}%\n")
                f.write(f"Session Efficiency: {(active_time/max(0.001, total_session_time))*100:.1f}% active time\n")
                f.write(f"Reliability Score: {'HIGH' if self.file_recovery_count <= 2 else 'MEDIUM' if self.file_recovery_count <= 5 else 'LOW'}\n")
                
                # Add pause/resume history
                f.write(f"\nPause/Resume Events: {len(self.pause_history)}\n")
                for event in self.pause_history:
                    f.write(f"  {event['time']} - {event['type'].replace('_', ' ').title()}: {event['reason']}\n")
                
                # Add backup file list
                f.write(f"\nBackup Files Created:\n")
                for i, backup_path in enumerate(self.backup_file_paths, 1):
                    exists = "EXISTS" if os.path.exists(backup_path) else "DELETED"
                    f.write(f"  {i}. {os.path.basename(backup_path)} - {exists}\n")
                
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
            self.total_pause_time = 0
            self.pause_history = []
            self.pause_start_time = 0
            self.lock_screen_mode = False
            self.file_recovery_count = 0
            self.backup_file_paths = []
            self.file_session_id = None
            self.update_display()
            self.refresh_monitoring_display()
            self.log_message("🔄 Daily statistics reset (including recovery stats)")
            
    def export_session_log(self):
        """Export current session logs to a file"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"session_log_{timestamp}.txt"
            
            total_session_time = time.time() - self.session_start_time
            active_time = total_session_time - self.total_pause_time
            
            if self.is_paused.get() and self.pause_start_time > 0:
                current_pause = time.time() - self.pause_start_time
                active_time -= current_pause
            
            with open(filename, 'w') as f:
                f.write("ENHANCED ACTIVITY SIMULATOR - SESSION LOG\n")
                f.write("="*60 + "\n\n")
                f.write(f"User: RishiKumarRajvansh\n")
                f.write(f"Session ID: {self.file_session_id}\n")
                f.write(f"Session Start: {datetime.fromtimestamp(self.session_start_time).strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Export Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC\n")
                f.write(f"Total Session Duration: {total_session_time/3600:.2f} hours\n")
                f.write(f"Active Session Duration: {active_time/3600:.2f} hours\n")
                f.write(f"Auto-Pause Features: {'Enabled' if self.auto_pause_enabled.get() else 'Disabled'}\n")
                f.write(f"Auto-Activation Features: {'Enabled' if self.auto_activate_enabled.get() else 'Disabled'}\n")
                f.write(f"Auto-Recovery Features: {'Enabled' if self.auto_file_recovery.get() else 'Disabled'}\n")
                f.write(f"Lock Screen Mode: {'Enabled' if self.work_when_locked.get() else 'Disabled'}\n")
                f.write(f"Pause Events: {len([e for e in self.pause_history if 'pause' in e['type']])}\n")
                f.write(f"Recovery Events: {self.file_recovery_count}\n\n")
                f.write("ACTIVITY LOG:\n")
                f.write("-" * 50 + "\n")
                f.write(self.log_text.get('1.0', tk.END))
                
            self.log_message(f"📄 Session log exported: {filename}")
            messagebox.showinfo("Log Exported", f"Session log exported as:\n{filename}")
            
        except Exception as e:
            self.log_message(f"❌ Error exporting log: {e}")
            messagebox.showerror("Export Error", f"Failed to export log:\n{e}")
            
    def save_logs(self):
        """Save activity logs to file (permanent save)"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"activity_logs_permanent_{timestamp}.txt"
            
            total_session_time = time.time() - self.session_start_time
            active_time = total_session_time - self.total_pause_time
            
            if self.is_paused.get() and self.pause_start_time > 0:
                current_pause = time.time() - self.pause_start_time
                active_time -= current_pause
            
            with open(filename, 'w') as f:
                f.write("ENHANCED ACTIVITY SIMULATOR - PERMANENT ACTIVITY LOGS\n")
                f.write("="*70 + "\n\n")
                f.write(f"User: RishiKumarRajvansh\n")
                f.write(f"Session ID: {self.file_session_id}\n")
                f.write(f"Log Generation Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC\n")
                f.write(f"Session Start: {datetime.fromtimestamp(self.session_start_time).strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total Activities: {self.activities_today}\n")
                f.write(f"Current Percentage: {self.current_percentage.get():.1f}%\n")
                f.write(f"Target Percentage: {self.target_percentage.get()}%\n")
                f.write(f"Total Session Time: {total_session_time/60:.1f} minutes\n")
                f.write(f"Active Time: {active_time/60:.1f} minutes\n")
                f.write(f"Auto-Pause Enabled: {'Yes' if self.auto_pause_enabled.get() else 'No'}\n")
                f.write(f"Auto-Activation Enabled: {'Yes' if self.auto_activate_enabled.get() else 'No'}\n")
                f.write(f"Auto-Recovery Enabled: {'Yes' if self.auto_file_recovery.get() else 'No'}\n")
                f.write(f"Lock Screen Mode: {'Yes' if self.work_when_locked.get() else 'No'}\n")
                f.write(f"Mouse Movement Type: {self.mouse_movement_type.get()}\n")
                f.write(f"File Recovery Count: {self.file_recovery_count}\n")
                f.write(f"Backup Files: {len(self.backup_file_paths)}\n\n")
                f.write("DETAILED ACTIVITY LOG:\n")
                f.write("-" * 60 + "\n")
                f.write(self.log_text.get('1.0', tk.END))
                
            self.log_message(f"📄 Permanent logs saved: {filename}")
            messagebox.showinfo("Logs Saved", f"Permanent activity logs saved as:\n{filename}")
            
        except Exception as e:
            self.log_message(f"❌ Error saving logs: {e}")
            messagebox.showerror("Save Error", f"Failed to save logs:\n{e}")
            
    def load_daily_stats(self):
        """Load daily statistics (placeholder for future implementation)"""
        pass
        
    def save_daily_stats(self):
        """Save daily statistics (placeholder for future implementation)"""
        pass
        
    def on_closing(self):
        """Handle application closing"""
        if self.is_running.get():
            if messagebox.askyesno("Quit", "Simulation is running. Stop and quit?"):
                self.stop_simulation()
                time.sleep(1)
                self.master.destroy()
        else:
            if self.text_file_enabled.get():
                self.cleanup_temp_file()
            self.master.destroy()

# Main execution
if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = EnhancedActivitySimulator(root)
        
        root.protocol("WM_DELETE_WINDOW", app.on_closing)
        
        root.mainloop()
    except Exception as e:
        print(f"Failed to start application: {e}")
        input("Press Enter to exit...")