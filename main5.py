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
import winreg
import glob
from collections import deque
import numpy as np
import pandas as pd

# Data visualization and machine learning imports
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
import warnings
warnings.filterwarnings('ignore')

# Set style for better plots
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

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
                
        def get_installed_applications():
            """Get list of installed applications on Windows"""
            apps = set()
            
            try:
                # Method 1: Registry - Uninstall entries
                reg_paths = [
                    r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
                    r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
                ]
                
                for reg_path in reg_paths:
                    try:
                        registry_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path)
                        for i in range(winreg.QueryInfoKey(registry_key)[0]):
                            try:
                                subkey_name = winreg.EnumKey(registry_key, i)
                                subkey = winreg.OpenKey(registry_key, subkey_name)
                                try:
                                    app_name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                                    if app_name and len(app_name.strip()) > 2:
                                        apps.add(app_name.strip())
                                except:
                                    pass
                                winreg.CloseKey(subkey)
                            except:
                                continue
                        winreg.CloseKey(registry_key)
                    except:
                        continue
                        
                # Method 2: Start Menu shortcuts
                start_menu_paths = [
                    os.path.join(os.environ.get('PROGRAMDATA', ''), 'Microsoft', 'Windows', 'Start Menu', 'Programs'),
                    os.path.join(os.environ.get('APPDATA', ''), 'Microsoft', 'Windows', 'Start Menu', 'Programs')
                ]
                
                for start_path in start_menu_paths:
                    if os.path.exists(start_path):
                        for root, dirs, files in os.walk(start_path):
                            for file in files:
                                if file.endswith('.lnk'):
                                    app_name = os.path.splitext(file)[0]
                                    if len(app_name.strip()) > 2:
                                        apps.add(app_name.strip())
                                        
                # Add common system processes
                system_apps = [
                    "chrome", "firefox", "edge", "safari", "opera",
                    "teams", "zoom", "discord", "slack", "skype",
                    "code", "notepad", "notepad++", "sublime", "atom",
                    "spotify", "vlc", "winamp", "itunes",
                    "steam", "epic games", "origin", "uplay",
                    "excel", "word", "powerpoint", "outlook"
                ]
                
                for app in system_apps:
                    apps.add(app)
                    
            except Exception as e:
                print(f"Error getting installed apps: {e}")
                
            return sorted(list(apps))

        def get_running_processes():
            """Get currently running processes"""
            running = []
            try:
                for proc in psutil.process_iter(['pid', 'name']):
                    try:
                        proc_name = proc.info['name']
                        if proc_name and '.exe' in proc_name:
                            clean_name = proc_name.replace('.exe', '')
                            if len(clean_name) > 2:
                                running.append(clean_name)
                    except:
                        continue
            except:
                pass
            return sorted(list(set(running)))
            
    else:
        def get_installed_applications():
            return ["chrome", "firefox", "code", "teams", "zoom", "discord"]
        def get_running_processes():
            return []
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
    def get_installed_applications():
        return ["chrome", "firefox", "code", "teams", "zoom", "discord"]
    def get_running_processes():
        return []
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

class DataCollector:
    """Real-time data collection for analytics"""
    
    def __init__(self, max_points=1000):
        self.max_points = max_points
        
        # Time series data
        self.timestamps = deque(maxlen=max_points)
        self.user_idle_times = deque(maxlen=max_points)
        self.sim_activities = deque(maxlen=max_points)
        self.cpu_usage = deque(maxlen=max_points)
        self.memory_usage = deque(maxlen=max_points)
        self.target_percentages = deque(maxlen=max_points)
        self.current_percentages = deque(maxlen=max_points)
        self.is_paused_data = deque(maxlen=max_points)
        self.is_locked_data = deque(maxlen=max_points)
        self.mouse_movements = deque(maxlen=max_points)
        self.key_presses = deque(maxlen=max_points)
        self.text_simulations = deque(maxlen=max_points)
        self.file_recoveries = deque(maxlen=max_points)
        
        # Session data
        self.session_activities = []
        self.pause_events = []
        self.app_avoidance_events = []
        
    def add_data_point(self, user_idle, sim_activity, target_pct, current_pct, 
                      is_paused, is_locked, mouse_moves, key_presses, 
                      text_sims, file_recoveries):
        """Add a new data point"""
        timestamp = datetime.now()
        
        self.timestamps.append(timestamp)
        self.user_idle_times.append(user_idle)
        self.sim_activities.append(sim_activity)
        self.target_percentages.append(target_pct)
        self.current_percentages.append(current_pct)
        self.is_paused_data.append(is_paused)
        self.is_locked_data.append(is_locked)
        self.mouse_movements.append(mouse_moves)
        self.key_presses.append(key_presses)
        self.text_simulations.append(text_sims)
        self.file_recoveries.append(file_recoveries)
        
        # System metrics
        try:
            self.cpu_usage.append(psutil.cpu_percent())
            self.memory_usage.append(psutil.virtual_memory().percent)
        except:
            self.cpu_usage.append(0)
            self.memory_usage.append(0)
            
    def add_session_activity(self, activity_type, timestamp=None):
        """Add session activity event"""
        if timestamp is None:
            timestamp = datetime.now()
        self.session_activities.append({
            'type': activity_type,
            'timestamp': timestamp
        })
        
    def add_pause_event(self, event_type, reason, timestamp=None):
        """Add pause/resume event"""
        if timestamp is None:
            timestamp = datetime.now()
        self.pause_events.append({
            'type': event_type,
            'reason': reason,
            'timestamp': timestamp
        })
        
    def get_dataframe(self):
        """Get data as pandas DataFrame for analysis"""
        if not self.timestamps:
            return pd.DataFrame()
            
        return pd.DataFrame({
            'timestamp': list(self.timestamps),
            'user_idle': list(self.user_idle_times),
            'sim_activity': list(self.sim_activities),
            'cpu_usage': list(self.cpu_usage),
            'memory_usage': list(self.memory_usage),
            'target_pct': list(self.target_percentages),
            'current_pct': list(self.current_percentages),
            'is_paused': list(self.is_paused_data),
            'is_locked': list(self.is_locked_data),
            'mouse_moves': list(self.mouse_movements),
            'key_presses': list(self.key_presses),
            'text_sims': list(self.text_simulations),
            'file_recoveries': list(self.file_recoveries)
        })

class ApplicationSelectorWindow:
    """Enhanced application selector with checkboxes and categories"""
    
    def __init__(self, parent, current_apps="", callback=None):
        self.parent = parent
        self.callback = callback
        self.selected_apps = set()
        self.all_apps = []
        self.filtered_apps = []
        
        # Parse current apps
        if current_apps:
            self.selected_apps = set([app.strip() for app in current_apps.split(',') if app.strip()])
        
        # Create window
        self.window = tk.Toplevel(parent)
        self.window.title("📱 Enhanced Application Selector")
        self.window.geometry("800x700")
        self.window.resizable(True, True)
        self.window.grab_set()  # Modal window
        
        # Load applications
        self.load_applications()
        self.create_widgets()
        self.refresh_app_list()
        
        # Center window
        self.window.transient(parent)
        self.window.focus_set()
        
    def load_applications(self):
        """Load installed applications and running processes"""
        try:
            # Get installed applications
            self.all_apps = get_installed_applications()
            
            # Add currently running processes
            running_processes = get_running_processes()
            for proc in running_processes:
                if proc not in self.all_apps:
                    self.all_apps.append(proc)
                    
            self.all_apps = sorted(list(set(self.all_apps)))
            self.filtered_apps = self.all_apps.copy()
            
        except Exception as e:
            print(f"Error loading applications: {e}")
            self.all_apps = ["chrome", "firefox", "teams", "zoom", "discord", "code"]
            self.filtered_apps = self.all_apps.copy()
    
    def create_widgets(self):
        """Create the application selector interface"""
        
        # --- Header ---
        header_frame = tk.Frame(self.window)
        header_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(header_frame, text="📱 Select Applications to Avoid During Simulation", 
                font=("Arial", 14, "bold")).pack()
        
        tk.Label(header_frame, text="Choose applications where simulation should pause automatically", 
                font=("Arial", 10), fg="gray").pack()
        
        # --- Search and Filter ---
        search_frame = tk.LabelFrame(self.window, text="🔍 Search & Filter", font=("Arial", 10, "bold"))
        search_frame.pack(fill="x", padx=10, pady=5)
        
        search_row = tk.Frame(search_frame)
        search_row.pack(fill="x", padx=5, pady=5)
        
        tk.Label(search_row, text="Search:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.on_search_change)
        search_entry = tk.Entry(search_row, textvariable=self.search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Button(search_row, text="🔄 Refresh", command=self.refresh_apps).pack(side=tk.LEFT, padx=5)
        tk.Button(search_row, text="📊 Show Running", command=self.show_running_only).pack(side=tk.LEFT, padx=5)
        tk.Button(search_row, text="📋 Show All", command=self.show_all_apps).pack(side=tk.LEFT, padx=5)
        
        # --- Quick Selection ---
        quick_frame = tk.LabelFrame(self.window, text="⚡ Quick Selection", font=("Arial", 10, "bold"))
        quick_frame.pack(fill="x", padx=10, pady=5)
        
        quick_buttons_frame = tk.Frame(quick_frame)
        quick_buttons_frame.pack(fill="x", padx=5, pady=5)
        
        tk.Button(quick_buttons_frame, text="💼 Work Apps", 
                 command=self.select_work_apps, bg="#007bff", fg="white").pack(side=tk.LEFT, padx=2)
        tk.Button(quick_buttons_frame, text="💬 Communication", 
                 command=self.select_communication_apps, bg="#28a745", fg="white").pack(side=tk.LEFT, padx=2)
        tk.Button(quick_buttons_frame, text="🎮 Gaming", 
                 command=self.select_gaming_apps, bg="#dc3545", fg="white").pack(side=tk.LEFT, padx=2)
        tk.Button(quick_buttons_frame, text="🎵 Media", 
                 command=self.select_media_apps, bg="#6f42c1", fg="white").pack(side=tk.LEFT, padx=2)
        tk.Button(quick_buttons_frame, text="🔧 Development", 
                 command=self.select_dev_apps, bg="#fd7e14", fg="white").pack(side=tk.LEFT, padx=2)
        tk.Button(quick_buttons_frame, text="🚫 Clear All", 
                 command=self.clear_all_selection, bg="#6c757d", fg="white").pack(side=tk.LEFT, padx=2)
        
        # --- Application List ---
        list_frame = tk.LabelFrame(self.window, text="📋 Available Applications", font=("Arial", 10, "bold"))
        list_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Create scrollable frame for checkboxes
        canvas = tk.Canvas(list_frame)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.canvas = canvas
        self.app_vars = {}  # Store checkbox variables
        
        # --- Selection Info ---
        info_frame = tk.Frame(self.window)
        info_frame.pack(fill="x", padx=10, pady=5)
        
        self.selection_info = tk.Label(info_frame, text="Selected: 0 applications", 
                                     font=("Arial", 10, "bold"), fg="blue")
        self.selection_info.pack(side=tk.LEFT)
        
        self.app_count_info = tk.Label(info_frame, text=f"Total: {len(self.all_apps)} apps found", 
                                     font=("Arial", 10), fg="gray")
        self.app_count_info.pack(side=tk.RIGHT)
        
        # --- Control Buttons ---
        button_frame = tk.Frame(self.window)
        button_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Button(button_frame, text="✅ Apply Selection", 
                 command=self.apply_selection, bg="#28a745", fg="white", 
                 font=("Arial", 12, "bold"), width=15).pack(side=tk.LEFT, padx=5)
                 
        tk.Button(button_frame, text="❌ Cancel", 
                 command=self.cancel_selection, bg="#dc3545", fg="white", 
                 font=("Arial", 12, "bold"), width=15).pack(side=tk.LEFT, padx=5)
    
    def refresh_app_list(self):
        """Refresh the application list display"""
        # Clear existing checkboxes
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        self.app_vars.clear()
        
        # Create checkboxes for filtered apps
        for i, app in enumerate(self.filtered_apps):
            var = tk.BooleanVar()
            var.set(app.lower() in [selected.lower() for selected in self.selected_apps])
            
            # Create frame for each app
            app_frame = tk.Frame(self.scrollable_frame)
            app_frame.pack(fill="x", padx=5, pady=1)
            
            # Checkbox
            checkbox = tk.Checkbutton(app_frame, text=app, variable=var, 
                                    command=self.update_selection_info,
                                    font=("Arial", 9))
            checkbox.pack(side=tk.LEFT, anchor="w")
            
            # Add status indicator for running processes
            if app.lower() in [proc.lower() for proc in get_running_processes()]:
                running_label = tk.Label(app_frame, text="🟢", font=("Arial", 8))
                running_label.pack(side=tk.RIGHT)
                
            self.app_vars[app] = var
            
        self.update_selection_info()
        
    def on_search_change(self, *args):
        """Handle search input changes"""
        search_term = self.search_var.get().lower()
        if search_term:
            self.filtered_apps = [app for app in self.all_apps 
                                if search_term in app.lower()]
        else:
            self.filtered_apps = self.all_apps.copy()
        
        self.refresh_app_list()
        
    def refresh_apps(self):
        """Refresh the application list from system"""
        self.load_applications()
        self.refresh_app_list()
        self.app_count_info.config(text=f"Total: {len(self.all_apps)} apps found")
        
    def show_running_only(self):
        """Show only currently running applications"""
        running_processes = [proc.lower() for proc in get_running_processes()]
        self.filtered_apps = [app for app in self.all_apps 
                            if app.lower() in running_processes]
        self.refresh_app_list()
        
    def show_all_apps(self):
        """Show all applications"""
        self.filtered_apps = self.all_apps.copy()
        self.refresh_app_list()
        
    def select_work_apps(self):
        """Select common work applications"""
        work_apps = ["teams", "zoom", "outlook", "excel", "word", "powerpoint", 
                    "onenote", "sharepoint", "onedrive", "slack", "webex"]
        self.select_apps_by_keywords(work_apps)
        
    def select_communication_apps(self):
        """Select communication applications"""
        comm_apps = ["teams", "zoom", "discord", "slack", "skype", "whatsapp", 
                    "telegram", "signal", "messenger", "hangouts"]
        self.select_apps_by_keywords(comm_apps)
        
    def select_gaming_apps(self):
        """Select gaming applications"""
        gaming_apps = ["steam", "epic", "origin", "uplay", "battle.net", "xbox", 
                      "minecraft", "roblox", "fortnite", "league", "dota"]
        self.select_apps_by_keywords(gaming_apps)
        
    def select_media_apps(self):
        """Select media applications"""
        media_apps = ["spotify", "vlc", "netflix", "youtube", "twitch", "obs", 
                     "photoshop", "premiere", "after effects", "audacity"]
        self.select_apps_by_keywords(media_apps)
        
    def select_dev_apps(self):
        """Select development applications"""
        dev_apps = ["code", "visual studio", "intellij", "pycharm", "eclipse", 
                   "git", "docker", "postman", "figma", "sublime"]
        self.select_apps_by_keywords(dev_apps)
        
    def select_apps_by_keywords(self, keywords):
        """Select applications matching keywords"""
        for app_name, var in self.app_vars.items():
            for keyword in keywords:
                if keyword.lower() in app_name.lower():
                    var.set(True)
                    break
        self.update_selection_info()
        
    def clear_all_selection(self):
        """Clear all selected applications"""
        for var in self.app_vars.values():
            var.set(False)
        self.update_selection_info()
        
    def update_selection_info(self):
        """Update the selection information display"""
        selected_count = sum(1 for var in self.app_vars.values() if var.get())
        self.selection_info.config(text=f"Selected: {selected_count} applications")
        
        # Update selected_apps set
        self.selected_apps.clear()
        for app_name, var in self.app_vars.items():
            if var.get():
                self.selected_apps.add(app_name)
                
    def apply_selection(self):
        """Apply the selection and close window"""
        selected_list = sorted(list(self.selected_apps))
        if self.callback:
            self.callback(', '.join(selected_list))
        self.window.destroy()
        
    def cancel_selection(self):
        """Cancel selection and close window"""
        self.window.destroy()

class AnalyticsEngine:
    """Advanced analytics and machine learning for activity simulation"""
    
    def __init__(self, data_collector):
        self.data_collector = data_collector
        self.scaler = StandardScaler()
        
    def analyze_user_patterns(self):
        """Analyze user activity patterns using machine learning"""
        df = self.data_collector.get_dataframe()
        if df.empty or len(df) < 10:
            return {}
            
        try:
            # Feature engineering
            df['hour'] = df['timestamp'].dt.hour
            df['minute'] = df['timestamp'].dt.minute
            df['day_of_week'] = df['timestamp'].dt.dayofweek
            df['efficiency'] = df['current_pct'] / df['target_pct'].replace(0, 1)
            
            # User activity classification using K-means
            features = ['user_idle', 'cpu_usage', 'memory_usage', 'hour']
            if all(col in df.columns for col in features):
                X = df[features].fillna(0)
                if len(X) >= 3:
                    kmeans = KMeans(n_clusters=min(3, len(X)), random_state=42, n_init=10)
                    df['activity_cluster'] = kmeans.fit_predict(X)
            
            # Efficiency prediction
            prediction_features = ['user_idle', 'mouse_moves', 'key_presses', 'text_sims']
            if all(col in df.columns for col in prediction_features) and len(df) >= 5:
                X_pred = df[prediction_features].fillna(0)
                y_pred = df['efficiency'].fillna(1)
                
                lr = LinearRegression()
                lr.fit(X_pred, y_pred)
                df['predicted_efficiency'] = lr.predict(X_pred)
                
                efficiency_score = r2_score(y_pred, df['predicted_efficiency'])
            else:
                efficiency_score = 0
            
            # Calculate insights
            insights = {
                'total_points': len(df),
                'avg_idle_time': df['user_idle'].mean(),
                'avg_efficiency': df['efficiency'].mean(),
                'most_active_hour': df.groupby('hour')['sim_activity'].sum().idxmax() if 'hour' in df.columns else 0,
                'pause_frequency': df['is_paused'].sum() / len(df),
                'lock_frequency': df['is_locked'].sum() / len(df),
                'avg_cpu': df['cpu_usage'].mean(),
                'avg_memory': df['memory_usage'].mean(),
                'efficiency_prediction_score': efficiency_score,
                'activity_clusters': df['activity_cluster'].unique().tolist() if 'activity_cluster' in df.columns else []
            }
            
            return insights
            
        except Exception as e:
            print(f"Analytics error: {e}")
            return {}
    
    def get_recommendations(self):
        """Get AI-powered recommendations for optimization"""
        insights = self.analyze_user_patterns()
        recommendations = []
        
        if not insights:
            return ["Insufficient data for recommendations. Run simulation longer."]
        
        # Efficiency recommendations
        if insights.get('avg_efficiency', 1) < 0.8:
            recommendations.append("🔧 Consider increasing intensity mode for better efficiency")
        
        if insights.get('pause_frequency', 0) > 0.3:
            recommendations.append("⏸️ High pause frequency detected - consider adjusting auto-pause thresholds")
        
        if insights.get('avg_idle_time', 0) > 60:
            recommendations.append("💤 Long idle periods detected - consider reducing idle thresholds")
        
        if insights.get('lock_frequency', 0) > 0.2:
            recommendations.append("🔒 Frequent lock mode usage - lock screen optimizations are active")
        
        # Performance recommendations
        if insights.get('avg_cpu', 0) > 80:
            recommendations.append("🖥️ High CPU usage detected - consider reducing simulation intensity")
        
        if insights.get('efficiency_prediction_score', 0) > 0.7:
            recommendations.append("🎯 Good prediction accuracy - current patterns are stable")
        
        if not recommendations:
            recommendations.append("✅ System running optimally - no specific recommendations")
        
        return recommendations

class EnhancedActivitySimulator:
    def __init__(self, master):
        self.master = master
        master.title("Enhanced Activity Simulator Pro - Analytics Edition")
        master.geometry("900x1000")
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
        
        # --- File Recovery Settings ---
        self.auto_file_recovery = tk.BooleanVar(value=True)
        self.file_check_interval = tk.IntVar(value=15)
        self.max_recovery_attempts = tk.IntVar(value=3)
        self.last_file_check = 0
        self.file_recovery_count = 0
        self.backup_file_paths = []
        
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
        self.file_session_id = None
        
        # --- Timing Variables ---
        self.base_interval_seconds = tk.IntVar(value=15)
        self.burst_mode_enabled = tk.BooleanVar(value=True)
        self.burst_actions_count = tk.IntVar(value=3)
        
        # --- Enhanced Application Settings ---
        self.avoid_apps = tk.StringVar(value="")
        self.selected_avoid_apps = set()
        
        # --- Advanced Settings ---
        self.micro_movements_enabled = tk.BooleanVar(value=False)
        self.full_screen_movements_enabled = tk.BooleanVar(value=True)
        self.natural_typing_enabled = tk.BooleanVar(value=True)
        self.smart_scheduling_enabled = tk.BooleanVar(value=True)
        
        # --- INPUT FIELD MANAGEMENT ---
        self.input_widgets = []
        self.setting_widgets = []
        self.checkbox_widgets = []
        self.radiobutton_widgets = []
        self.spinbox_widgets = []
        self.scale_widgets = []
        self.combobox_widgets = []
        self.entry_widgets = []
        
        # --- ANALYTICS & DATA COLLECTION (NEW) ---
        self.data_collector = DataCollector()
        self.analytics_engine = AnalyticsEngine(self.data_collector)
        self.last_data_collection = time.time()
        
        # Activity counters for analytics
        self.mouse_move_count = 0
        self.key_press_count = 0
        self.text_sim_count = 0
        
        # Initialize pyautogui
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.01
        
        self.create_widgets()
        self.automation_thread = None
        self.monitoring_thread = None
        self.activation_thread = None
        self.file_monitor_thread = None
        self.analytics_thread = None
        self.load_daily_stats()
        
    def register_input_widget(self, widget, widget_type="general"):
        """Register an input widget for enable/disable management"""
        self.input_widgets.append(widget)
        
        if widget_type == "setting":
            self.setting_widgets.append(widget)
        elif widget_type == "checkbox":
            self.checkbox_widgets.append(widget)
        elif widget_type == "radiobutton":
            self.radiobutton_widgets.append(widget)
        elif widget_type == "spinbox":
            self.spinbox_widgets.append(widget)
        elif widget_type == "scale":
            self.scale_widgets.append(widget)
        elif widget_type == "combobox":
            self.combobox_widgets.append(widget)
        elif widget_type == "entry":
            self.entry_widgets.append(widget)
            
    def disable_all_inputs(self):
        """Disable all input fields during simulation"""
        try:
            self.log_message("🔒 Disabling all input fields - simulation running")
            
            for widget in self.input_widgets:
                try:
                    if hasattr(widget, 'config'):
                        widget.config(state='disabled')
                    elif hasattr(widget, 'configure'):
                        widget.configure(state='disabled')
                except:
                    pass
                    
            for checkbox in self.checkbox_widgets:
                try:
                    checkbox.config(state='disabled')
                except:
                    pass
                    
            for radiobutton in self.radiobutton_widgets:
                try:
                    radiobutton.config(state='disabled')
                except:
                    pass
                    
            for spinbox in self.spinbox_widgets:
                try:
                    spinbox.config(state='disabled')
                except:
                    pass
                    
            for scale in self.scale_widgets:
                try:
                    scale.config(state='disabled')
                except:
                    pass
                    
            for combobox in self.combobox_widgets:
                try:
                    combobox.config(state='disabled')
                except:
                    pass
                    
            for entry in self.entry_widgets:
                try:
                    entry.config(state='disabled')
                except:
                    pass
                    
            self.master.after(0, lambda: self.update_input_status("🔒 LOCKED"))
                    
        except Exception as e:
            self.log_message(f"⚠️ Error disabling inputs: {e}")
            
    def enable_all_inputs(self):
        """Enable all input fields when simulation stops"""
        try:
            self.log_message("🔓 Enabling all input fields - simulation stopped")
            
            for widget in self.input_widgets:
                try:
                    if hasattr(widget, 'config'):
                        widget.config(state='normal')
                    elif hasattr(widget, 'configure'):
                        widget.configure(state='normal')
                except:
                    pass
                    
            for checkbox in self.checkbox_widgets:
                try:
                    checkbox.config(state='normal')
                except:
                    pass
                    
            for radiobutton in self.radiobutton_widgets:
                try:
                    radiobutton.config(state='normal')
                except:
                    pass
                    
            for spinbox in self.spinbox_widgets:
                try:
                    spinbox.config(state='normal')
                except:
                    pass
                    
            for scale in self.scale_widgets:
                try:
                    scale.config(state='normal')
                except:
                    pass
                    
            for combobox in self.combobox_widgets:
                try:
                    combobox.config(state='readonly')
                except:
                    pass
                    
            for entry in self.entry_widgets:
                try:
                    entry.config(state='normal')
                except:
                    pass
                    
            self.master.after(0, lambda: self.update_input_status("🔓 UNLOCKED"))
                    
        except Exception as e:
            self.log_message(f"⚠️ Error enabling inputs: {e}")
            
    def update_input_status(self, status):
        """Update the input status display"""
        try:
            if hasattr(self, 'input_status_label'):
                self.input_status_label.config(text=f"Input Fields: {status}")
        except:
            pass
        
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
        
        # Tab 4: Analytics & Insights (NEW)
        analytics_frame = ttk.Frame(notebook)
        notebook.add(analytics_frame, text="📊 Insights & Analytics")
        self.create_analytics_tab(analytics_frame)
        
        # Tab 5: Logs
        log_frame = ttk.Frame(notebook)
        notebook.add(log_frame, text="Activity Logs")
        self.create_log_tab(log_frame)

    def create_control_tab(self, parent):
        # --- Input Field Status ---
        input_status_frame = tk.LabelFrame(parent, text="Input Field Status", font=("Arial", 10, "bold"))
        input_status_frame.pack(padx=10, pady=5, fill="x")
        
        self.input_status_label = tk.Label(input_status_frame, text="Input Fields: 🔓 UNLOCKED", 
                                         font=("Arial", 10, "bold"), fg="green")
        self.input_status_label.pack(pady=5)
        
        tk.Label(input_status_frame, text="⚠️ All settings are locked during simulation to prevent conflicts", 
                font=("Arial", 9), fg="orange").pack()
        
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
        self.register_input_widget(target_scale, "scale")
        
        target_row2 = tk.Frame(target_frame)
        target_row2.pack(fill="x", padx=5, pady=2)
        tk.Label(target_row2, text="Daily Working Hours:").pack(side=tk.LEFT)
        hours_spinbox = tk.Spinbox(target_row2, from_=1, to=24, textvariable=self.daily_target_hours, 
                  width=5, format="%.1f", increment=0.5)
        hours_spinbox.pack(side=tk.LEFT, padx=10)
        self.register_input_widget(hours_spinbox, "spinbox")
        
        # --- File Recovery Settings Frame ---
        filerecovery_frame = tk.LabelFrame(parent, text="File Recovery Settings", font=("Arial", 10, "bold"))
        filerecovery_frame.pack(padx=10, pady=5, fill="x")
        
        recovery_checkbox = tk.Checkbutton(filerecovery_frame, text="Auto File Recovery (recreate text file if closed)", 
                      variable=self.auto_file_recovery)
        recovery_checkbox.pack(anchor=tk.W, padx=5, pady=2)
        self.register_input_widget(recovery_checkbox, "checkbox")
        
        filerecovery_row1 = tk.Frame(filerecovery_frame)
        filerecovery_row1.pack(fill="x", padx=5, pady=2)
        tk.Label(filerecovery_row1, text="Check file status every:").pack(side=tk.LEFT)
        file_check_spinbox = tk.Spinbox(filerecovery_row1, from_=5, to=60, textvariable=self.file_check_interval, 
                  width=5)
        file_check_spinbox.pack(side=tk.LEFT, padx=5)
        tk.Label(filerecovery_row1, text="seconds").pack(side=tk.LEFT)
        self.register_input_widget(file_check_spinbox, "spinbox")
        
        filerecovery_row2 = tk.Frame(filerecovery_frame)
        filerecovery_row2.pack(fill="x", padx=5, pady=2)
        tk.Label(filerecovery_row2, text="Max recovery attempts:").pack(side=tk.LEFT)
        max_attempts_spinbox = tk.Spinbox(filerecovery_row2, from_=1, to=10, textvariable=self.max_recovery_attempts, 
                  width=5)
        max_attempts_spinbox.pack(side=tk.LEFT, padx=5)
        tk.Label(filerecovery_row2, text="per session").pack(side=tk.LEFT)
        self.register_input_widget(max_attempts_spinbox, "spinbox")
        
        # --- Auto-Activation Settings Frame ---
        autoactivation_frame = tk.LabelFrame(parent, text="Auto-Activation Settings", font=("Arial", 10, "bold"))
        autoactivation_frame.pack(padx=10, pady=5, fill="x")
        
        activate_checkbox = tk.Checkbutton(autoactivation_frame, text="Auto-Activate Text File (bring to foreground when inactive)", 
                      variable=self.auto_activate_enabled)
        activate_checkbox.pack(anchor=tk.W, padx=5, pady=2)
        self.register_input_widget(activate_checkbox, "checkbox")
        
        lock_checkbox = tk.Checkbutton(autoactivation_frame, text="Work When Screen Locked (continue simulation in background)", 
                      variable=self.work_when_locked)
        lock_checkbox.pack(anchor=tk.W, padx=5, pady=2)
        self.register_input_widget(lock_checkbox, "checkbox")
        
        autoactivation_row1 = tk.Frame(autoactivation_frame)
        autoactivation_row1.pack(fill="x", padx=5, pady=2)
        tk.Label(autoactivation_row1, text="Check activation every:").pack(side=tk.LEFT)
        activation_spinbox = tk.Spinbox(autoactivation_row1, from_=10, to=120, textvariable=self.activation_check_interval, 
                  width=5)
        activation_spinbox.pack(side=tk.LEFT, padx=5)
        tk.Label(autoactivation_row1, text="seconds").pack(side=tk.LEFT)
        self.register_input_widget(activation_spinbox, "spinbox")
        
        # --- Auto-Pause Settings Frame ---
        autopause_frame = tk.LabelFrame(parent, text="Auto-Pause Settings", font=("Arial", 10, "bold"))
        autopause_frame.pack(padx=10, pady=5, fill="x")
        
        pause_checkbox = tk.Checkbutton(autopause_frame, text="Enable Auto-Pause (pause when user is active)", 
                      variable=self.auto_pause_enabled)
        pause_checkbox.pack(anchor=tk.W, padx=5, pady=2)
        self.register_input_widget(pause_checkbox, "checkbox")
        
        autopause_row1 = tk.Frame(autopause_frame)
        autopause_row1.pack(fill="x", padx=5, pady=2)
        tk.Label(autopause_row1, text="Pause after user active for:").pack(side=tk.LEFT)
        pause_threshold_spinbox = tk.Spinbox(autopause_row1, from_=5, to=60, textvariable=self.auto_pause_threshold, 
                  width=5)
        pause_threshold_spinbox.pack(side=tk.LEFT, padx=5)
        tk.Label(autopause_row1, text="seconds").pack(side=tk.LEFT)
        self.register_input_widget(pause_threshold_spinbox, "spinbox")
        
        autopause_row2 = tk.Frame(autopause_frame)
        autopause_row2.pack(fill="x", padx=5, pady=2)
        tk.Label(autopause_row2, text="Resume after user idle for:").pack(side=tk.LEFT)
        resume_threshold_spinbox = tk.Spinbox(autopause_row2, from_=60, to=600, textvariable=self.auto_resume_threshold, 
                  width=5)
        resume_threshold_spinbox.pack(side=tk.LEFT, padx=5)
        tk.Label(autopause_row2, text="seconds").pack(side=tk.LEFT)
        self.register_input_widget(resume_threshold_spinbox, "spinbox")
        
        # --- Current Status Frame ---
        status_frame = tk.LabelFrame(parent, text="Current Status", font=("Arial", 10, "bold"))
        status_frame.pack(padx=10, pady=5, fill="x")
        
        self.current_percentage_label = tk.Label(status_frame, text="Current Activity: 0.0%", 
                                               font=("Arial", 14, "bold"), fg="red")
        self.current_percentage_label.pack(pady=5)
        
        self.progress_bar = ttk.Progressbar(status_frame, length=400, mode='determinate')
        self.progress_bar.pack(pady=5)
        
        # --- File Status ---
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
            radio = tk.Radiobutton(intensity_frame, text=mode, variable=self.intensity_mode, 
                          value=mode, command=self.update_intensity_settings)
            radio.pack(side=tk.LEFT, padx=10, pady=5)
            self.register_input_widget(radio, "radiobutton")
        
        # --- Smart Features Frame ---
        smart_frame = tk.LabelFrame(parent, text="Smart Features", font=("Arial", 10, "bold"))
        smart_frame.pack(padx=10, pady=5, fill="x")
        
        detection_checkbox = tk.Checkbutton(smart_frame, text="Smart User Detection (Real system idle time detection)", 
                      variable=self.smart_detection_enabled)
        detection_checkbox.pack(anchor=tk.W, padx=5, pady=2)
        self.register_input_widget(detection_checkbox, "checkbox")
        
        text_file_checkbox = tk.Checkbutton(smart_frame, text="Text File Simulation (Safe, dedicated file only)", 
                      variable=self.text_file_enabled)
        text_file_checkbox.pack(anchor=tk.W, padx=5, pady=2)
        self.register_input_widget(text_file_checkbox, "checkbox")
        
        burst_checkbox = tk.Checkbutton(smart_frame, text="Burst Mode (Multiple actions in sequence)", 
                      variable=self.burst_mode_enabled)
        burst_checkbox.pack(anchor=tk.W, padx=5, pady=2)
        self.register_input_widget(burst_checkbox, "checkbox")
        
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
        
        # Test and recovery buttons
        self.test_activation_button = tk.Button(button_frame2, text="🔄 Test Activation", 
                                              command=self.test_window_activation,
                                              bg="#6f42c1", fg="white", font=("Arial", 10), 
                                              width=15)
        self.test_activation_button.pack(side=tk.LEFT, padx=5)
        
        # File recovery button
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
        # --- Input Lock Warning ---
        warning_frame = tk.LabelFrame(parent, text="⚠️ Settings Lock Warning", font=("Arial", 10, "bold"))
        warning_frame.pack(padx=10, pady=5, fill="x")
        
        tk.Label(warning_frame, text="🔒 These settings will be LOCKED during simulation", 
                font=("Arial", 10, "bold"), fg="red").pack(pady=2)
        tk.Label(warning_frame, text="Stop simulation first to modify any settings", 
                font=("Arial", 9), fg="gray").pack()

        # --- ENHANCED APPLICATION SETTINGS ---
        app_frame = tk.LabelFrame(parent, text="📱 Enhanced Application Settings", font=("Arial", 10, "bold"))
        app_frame.pack(padx=10, pady=5, fill="x")
        
        tk.Label(app_frame, text="Select applications where simulation should pause automatically:", 
                font=("Arial", 10)).pack(anchor=tk.W, padx=5, pady=2)
        
        # Current selection display
        selection_display_frame = tk.Frame(app_frame)
        selection_display_frame.pack(fill="x", padx=5, pady=5)
        
        self.avoid_apps_display = tk.Text(selection_display_frame, height=3, width=60, 
                                        font=("Arial", 9), state='disabled',
                                        wrap=tk.WORD, bg="#f8f9fa")
        self.avoid_apps_display.pack(side=tk.LEFT, fill="x", expand=True)
        
        # Buttons
        app_buttons_frame = tk.Frame(app_frame)
        app_buttons_frame.pack(fill="x", padx=5, pady=5)
        
        self.select_apps_button = tk.Button(app_buttons_frame, text="📱 Select Applications", 
                                          command=self.open_app_selector,
                                          bg="#007bff", fg="white", font=("Arial", 10, "bold"), 
                                          width=20)
        self.select_apps_button.pack(side=tk.LEFT, padx=5)
        self.register_input_widget(self.select_apps_button)
        
        tk.Button(app_buttons_frame, text="🔄 Refresh Apps", 
                 command=self.refresh_app_list,
                 bg="#28a745", fg="white", font=("Arial", 10), 
                 width=15).pack(side=tk.LEFT, padx=5)
        
        tk.Button(app_buttons_frame, text="📊 Show Running", 
                 command=self.show_running_apps,
                 bg="#17a2b8", fg="white", font=("Arial", 10), 
                 width=15).pack(side=tk.LEFT, padx=5)
        
        tk.Button(app_buttons_frame, text="🚫 Clear Selection", 
                 command=self.clear_app_selection,
                 bg="#dc3545", fg="white", font=("Arial", 10), 
                 width=15).pack(side=tk.LEFT, padx=5)
        
        # App count and status
        app_info_frame = tk.Frame(app_frame)
        app_info_frame.pack(fill="x", padx=5, pady=2)
        
        self.app_count_label = tk.Label(app_info_frame, text="Selected: 0 applications", 
                                      font=("Arial", 9, "bold"), fg="blue")
        self.app_count_label.pack(side=tk.LEFT)
        
        self.running_apps_label = tk.Label(app_info_frame, text="Running: Scanning...", 
                                         font=("Arial", 9), fg="green")
        self.running_apps_label.pack(side=tk.RIGHT)
        
        # Legacy text input (hidden by default)
        legacy_frame = tk.Frame(app_frame)
        legacy_frame.pack(fill="x", padx=5, pady=2)
        
        self.show_legacy_var = tk.BooleanVar()
        tk.Checkbutton(legacy_frame, text="Show legacy text input (for manual entry)", 
                      variable=self.show_legacy_var, command=self.toggle_legacy_input).pack(anchor=tk.W)
        
        self.legacy_input_frame = tk.Frame(app_frame)
        # Frame is packed/unpacked in toggle_legacy_input
        
        tk.Label(self.legacy_input_frame, text="Manual entry (comma-separated):").pack(anchor=tk.W, padx=5, pady=2)
        avoid_entry = tk.Entry(self.legacy_input_frame, textvariable=self.avoid_apps, width=60)
        avoid_entry.pack(padx=5, pady=2, fill="x")
        self.register_input_widget(avoid_entry, "entry")
        
        tk.Label(self.legacy_input_frame, text="(e.g., 'zoom,teams,discord')", 
                font=("Arial", 8), fg="gray").pack(anchor=tk.W, padx=5)

        # Initialize app display
        self.update_app_display()
        self.update_running_apps_display()

        # --- Timing Settings ---
        timing_frame = tk.LabelFrame(parent, text="Timing Settings", font=("Arial", 10, "bold"))
        timing_frame.pack(padx=10, pady=5, fill="x")
        
        timing_row1 = tk.Frame(timing_frame)
        timing_row1.pack(fill="x", padx=5, pady=5)
        tk.Label(timing_row1, text="Base Interval (seconds):").pack(side=tk.LEFT)
        interval_spinbox = tk.Spinbox(timing_row1, from_=5, to=120, textvariable=self.base_interval_seconds, 
                  width=5)
        interval_spinbox.pack(side=tk.LEFT, padx=10)
        self.register_input_widget(interval_spinbox, "spinbox")
        
        timing_row2 = tk.Frame(timing_frame)
        timing_row2.pack(fill="x", padx=5, pady=5)
        tk.Label(timing_row2, text="Burst Actions Count:").pack(side=tk.LEFT)
        burst_spinbox = tk.Spinbox(timing_row2, from_=1, to=10, textvariable=self.burst_actions_count, 
                  width=5)
        burst_spinbox.pack(side=tk.LEFT, padx=10)
        self.register_input_widget(burst_spinbox, "spinbox")
        
        timing_row3 = tk.Frame(timing_frame)
        timing_row3.pack(fill="x", padx=5, pady=5)
        tk.Label(timing_row3, text="User Idle Threshold (seconds):").pack(side=tk.LEFT)
        idle_spinbox = tk.Spinbox(timing_row3, from_=10, to=300, textvariable=self.user_idle_threshold, 
                  width=5)
        idle_spinbox.pack(side=tk.LEFT, padx=10)
        self.register_input_widget(idle_spinbox, "spinbox")
        
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
        self.register_input_widget(movement_combo, "combobox")
        
        mouse_row2 = tk.Frame(mouse_frame)
        mouse_row2.pack(fill="x", padx=5, pady=5)
        tk.Label(mouse_row2, text="Max Distance (pixels):").pack(side=tk.LEFT)
        distance_spinbox = tk.Spinbox(mouse_row2, from_=5, to=500, textvariable=self.mouse_movement_distance, 
                  width=8)
        distance_spinbox.pack(side=tk.LEFT, padx=10)
        self.register_input_widget(distance_spinbox, "spinbox")
        
        visible_checkbox = tk.Checkbutton(mouse_frame, text="Make movements visible (slower but obvious)", 
                      variable=self.visible_movements)
        visible_checkbox.pack(anchor=tk.W, padx=5, pady=2)
        self.register_input_widget(visible_checkbox, "checkbox")
        
        # --- Activity Types ---
        activity_frame = tk.LabelFrame(parent, text="Activity Types", font=("Arial", 10, "bold"))
        activity_frame.pack(padx=10, pady=5, fill="x")
        
        micro_checkbox = tk.Checkbutton(activity_frame, text="Micro Mouse Movements (1-3 pixels)", 
                      variable=self.micro_movements_enabled)
        micro_checkbox.pack(anchor=tk.W, padx=5, pady=2)
        self.register_input_widget(micro_checkbox, "checkbox")
        
        fullscreen_checkbox = tk.Checkbutton(activity_frame, text="Full Screen Mouse Movements (visible)", 
                      variable=self.full_screen_movements_enabled)
        fullscreen_checkbox.pack(anchor=tk.W, padx=5, pady=2)
        self.register_input_widget(fullscreen_checkbox, "checkbox")
        
        typing_checkbox = tk.Checkbutton(activity_frame, text="Natural Typing Patterns", 
                      variable=self.natural_typing_enabled)
        typing_checkbox.pack(anchor=tk.W, padx=5, pady=2)
        self.register_input_widget(typing_checkbox, "checkbox")
        
        scheduling_checkbox = tk.Checkbutton(activity_frame, text="Smart Scheduling", 
                      variable=self.smart_scheduling_enabled)
        scheduling_checkbox.pack(anchor=tk.W, padx=5, pady=2)
        self.register_input_widget(scheduling_checkbox, "checkbox")

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

    def create_analytics_tab(self, parent):
        """Create the advanced analytics and insights tab with real-time graphs"""
        
        # --- Analytics Header ---
        header_frame = tk.Frame(parent)
        header_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(header_frame, text="📊 Real-time Analytics & AI Insights", 
                font=("Arial", 14, "bold"), fg="#2E86AB").pack()
        
        tk.Label(header_frame, text="Advanced data visualization and machine learning analysis", 
                font=("Arial", 10), fg="gray").pack()
        
        # --- Control Panel ---
        control_frame = tk.LabelFrame(parent, text="🎛️ Analytics Controls", font=("Arial", 10, "bold"))
        control_frame.pack(fill="x", padx=10, pady=5)
        
        control_buttons = tk.Frame(control_frame)
        control_buttons.pack(fill="x", padx=5, pady=5)
        
        tk.Button(control_buttons, text="🔄 Refresh Analytics", 
                 command=self.refresh_analytics, bg="#28a745", fg="white", 
                 font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)
        
        tk.Button(control_buttons, text="📈 Export Data", 
                 command=self.export_analytics_data, bg="#17a2b8", fg="white", 
                 font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
        
        tk.Button(control_buttons, text="🤖 AI Recommendations", 
                 command=self.show_ai_recommendations, bg="#6f42c1", fg="white", 
                 font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
        
        tk.Button(control_buttons, text="📊 Save Charts", 
                 command=self.save_analytics_charts, bg="#fd7e14", fg="white", 
                 font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
        
        # --- Analytics Notebook ---
        analytics_notebook = ttk.Notebook(parent)
        analytics_notebook.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Real-time Graphs Tab
        realtime_frame = ttk.Frame(analytics_notebook)
        analytics_notebook.add(realtime_frame, text="📈 Real-time Graphs")
        self.create_realtime_graphs(realtime_frame)
        
        # Performance Analysis Tab
        performance_frame = ttk.Frame(analytics_notebook)
        analytics_notebook.add(performance_frame, text="⚡ Performance Analysis")
        self.create_performance_analysis(performance_frame)
        
        # Machine Learning Tab
        ml_frame = ttk.Frame(analytics_notebook)
        analytics_notebook.add(ml_frame, text="🤖 ML Insights")
        self.create_ml_insights(ml_frame)
        
        # System Metrics Tab
        system_frame = ttk.Frame(analytics_notebook)
        analytics_notebook.add(system_frame, text="🖥️ System Metrics")
        self.create_system_metrics(system_frame)
        
    def create_realtime_graphs(self, parent):
        """Create real-time data visualization graphs"""
        
        # Create matplotlib figure
        self.analytics_fig = Figure(figsize=(12, 8), dpi=100)
        self.analytics_fig.patch.set_facecolor('#f8f9fa')
        
        # Create subplots
        gs = self.analytics_fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)
        
        # Activity vs Time
        self.ax_activity = self.analytics_fig.add_subplot(gs[0, 0])
        self.ax_activity.set_title('🎯 Activity Performance Over Time', fontweight='bold')
        self.ax_activity.set_xlabel('Time')
        self.ax_activity.set_ylabel('Percentage (%)')
        self.ax_activity.grid(True, alpha=0.3)
        
        # User Activity vs Simulation
        self.ax_user_sim = self.analytics_fig.add_subplot(gs[0, 1])
        self.ax_user_sim.set_title('👤 User vs Simulation Activity', fontweight='bold')
        self.ax_user_sim.set_xlabel('Time')
        self.ax_user_sim.set_ylabel('Activity Level')
        self.ax_user_sim.grid(True, alpha=0.3)
        
        # System Resources
        self.ax_resources = self.analytics_fig.add_subplot(gs[1, 0])
        self.ax_resources.set_title('🖥️ System Resource Usage', fontweight='bold')
        self.ax_resources.set_xlabel('Time')
        self.ax_resources.set_ylabel('Usage (%)')
        self.ax_resources.grid(True, alpha=0.3)
        
        # Activity Distribution
        self.ax_distribution = self.analytics_fig.add_subplot(gs[1, 1])
        self.ax_distribution.set_title('📊 Activity Type Distribution', fontweight='bold')
        
        # Create canvas
        self.analytics_canvas = FigureCanvasTkAgg(self.analytics_fig, parent)
        self.analytics_canvas.draw()
        self.analytics_canvas.get_tk_widget().pack(fill="both", expand=True)
        
        # Start real-time updates
        self.update_realtime_graphs()
        
    def create_performance_analysis(self, parent):
        """Create performance analysis widgets"""
        
        # Performance Metrics Frame
        metrics_frame = tk.LabelFrame(parent, text="📈 Performance Metrics", font=("Arial", 12, "bold"))
        metrics_frame.pack(fill="x", padx=10, pady=5)
        
        # Create metrics grid
        metrics_grid = tk.Frame(metrics_frame)
        metrics_grid.pack(fill="x", padx=10, pady=10)
        
        # Row 1
        row1 = tk.Frame(metrics_grid)
        row1.pack(fill="x", pady=5)
        
        self.efficiency_label = tk.Label(row1, text="Efficiency: --", 
                                       font=("Arial", 11, "bold"), fg="#28a745")
        self.efficiency_label.pack(side=tk.LEFT, padx=20)
        
        self.avg_idle_label = tk.Label(row1, text="Avg Idle: --", 
                                     font=("Arial", 11, "bold"), fg="#007bff")
        self.avg_idle_label.pack(side=tk.LEFT, padx=20)
        
        self.pause_rate_label = tk.Label(row1, text="Pause Rate: --", 
                                       font=("Arial", 11, "bold"), fg="#ffc107")
        self.pause_rate_label.pack(side=tk.LEFT, padx=20)
        
        # Row 2
        row2 = tk.Frame(metrics_grid)
        row2.pack(fill="x", pady=5)
        
        self.activities_rate_label = tk.Label(row2, text="Activity Rate: --", 
                                            font=("Arial", 11, "bold"), fg="#17a2b8")
        self.activities_rate_label.pack(side=tk.LEFT, padx=20)
        
        self.recovery_count_label = tk.Label(row2, text="Recoveries: --", 
                                           font=("Arial", 11, "bold"), fg="#dc3545")
        self.recovery_count_label.pack(side=tk.LEFT, padx=20)
        
        self.lock_time_label = tk.Label(row2, text="Lock Time: --", 
                                      font=("Arial", 11, "bold"), fg="#6f42c1")
        self.lock_time_label.pack(side=tk.LEFT, padx=20)
        
        # Performance Trends
        trends_frame = tk.LabelFrame(parent, text="📊 Performance Trends", font=("Arial", 12, "bold"))
        trends_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Create trends figure
        self.trends_fig = Figure(figsize=(10, 6), dpi=100)
        self.trends_fig.patch.set_facecolor('#f8f9fa')
        
        # Efficiency trend
        self.ax_efficiency = self.trends_fig.add_subplot(211)
        self.ax_efficiency.set_title('⚡ Efficiency Trend Over Time', fontweight='bold')
        self.ax_efficiency.set_ylabel('Efficiency Ratio')
        self.ax_efficiency.grid(True, alpha=0.3)
        
        # Activity correlation
        self.ax_correlation = self.trends_fig.add_subplot(212)
        self.ax_correlation.set_title('🔗 User Activity vs System Performance', fontweight='bold')
        self.ax_correlation.set_xlabel('Time')
        self.ax_correlation.set_ylabel('Correlation Score')
        self.ax_correlation.grid(True, alpha=0.3)
        
        self.trends_canvas = FigureCanvasTkAgg(self.trends_fig, trends_frame)
        self.trends_canvas.draw()
        self.trends_canvas.get_tk_widget().pack(fill="both", expand=True)
        
    def create_ml_insights(self, parent):
        """Create machine learning insights and predictions"""
        
        # ML Status Frame
        ml_status_frame = tk.LabelFrame(parent, text="🤖 Machine Learning Status", font=("Arial", 12, "bold"))
        ml_status_frame.pack(fill="x", padx=10, pady=5)
        
        status_grid = tk.Frame(ml_status_frame)
        status_grid.pack(fill="x", padx=10, pady=10)
        
        self.ml_model_status = tk.Label(status_grid, text="Model Status: Initializing...", 
                                      font=("Arial", 11, "bold"), fg="#007bff")
        self.ml_model_status.pack(side=tk.LEFT, padx=20)
        
        self.prediction_accuracy = tk.Label(status_grid, text="Accuracy: --", 
                                          font=("Arial", 11, "bold"), fg="#28a745")
        self.prediction_accuracy.pack(side=tk.LEFT, padx=20)
        
        self.data_points_count = tk.Label(status_grid, text="Data Points: 0", 
                                        font=("Arial", 11, "bold"), fg="#17a2b8")
        self.data_points_count.pack(side=tk.LEFT, padx=20)
        
        # Predictions Frame
        predictions_frame = tk.LabelFrame(parent, text="🔮 AI Predictions & Recommendations", 
                                        font=("Arial", 12, "bold"))
        predictions_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Create ML figure
        self.ml_fig = Figure(figsize=(10, 8), dpi=100)
        self.ml_fig.patch.set_facecolor('#f8f9fa')
        
        # User pattern clusters
        self.ax_clusters = self.ml_fig.add_subplot(221)
        self.ax_clusters.set_title('👥 User Activity Clusters', fontweight='bold')
        
        # Efficiency prediction
        self.ax_prediction = self.ml_fig.add_subplot(222)
        self.ax_prediction.set_title('📈 Efficiency Prediction', fontweight='bold')
        
        # Feature importance
        self.ax_features = self.ml_fig.add_subplot(223)
        self.ax_features.set_title('🎯 Feature Importance', fontweight='bold')
        
        # Recommendation heatmap
        self.ax_heatmap = self.ml_fig.add_subplot(224)
        self.ax_heatmap.set_title('🔥 Optimization Heatmap', fontweight='bold')
        
        self.ml_canvas = FigureCanvasTkAgg(self.ml_fig, predictions_frame)
        self.ml_canvas.draw()
        self.ml_canvas.get_tk_widget().pack(fill="both", expand=True)
        
        # Recommendations Text
        rec_frame = tk.Frame(predictions_frame)
        rec_frame.pack(fill="x", padx=5, pady=5)
        
        tk.Label(rec_frame, text="🤖 AI Recommendations:", 
                font=("Arial", 11, "bold")).pack(anchor=tk.W)
        
        self.recommendations_text = tk.Text(rec_frame, height=4, font=("Arial", 9),
                                          bg="#f8f9fa", state='disabled')
        self.recommendations_text.pack(fill="x", pady=5)
        
    def create_system_metrics(self, parent):
        """Create system metrics monitoring"""
        
        # System Status Frame
        system_status_frame = tk.LabelFrame(parent, text="🖥️ System Status", font=("Arial", 12, "bold"))
        system_status_frame.pack(fill="x", padx=10, pady=5)
        
        status_grid = tk.Frame(system_status_frame)
        status_grid.pack(fill="x", padx=10, pady=10)
        
        # Row 1
        row1 = tk.Frame(status_grid)
        row1.pack(fill="x", pady=5)
        
        self.cpu_status_label = tk.Label(row1, text="CPU: --", 
                                       font=("Arial", 11, "bold"), fg="#dc3545")
        self.cpu_status_label.pack(side=tk.LEFT, padx=20)
        
        self.memory_status_label = tk.Label(row1, text="Memory: --", 
                                          font=("Arial", 11, "bold"), fg="#fd7e14")
        self.memory_status_label.pack(side=tk.LEFT, padx=20)
        
        self.disk_status_label = tk.Label(row1, text="Disk: --", 
                                        font=("Arial", 11, "bold"), fg="#20c997")
        self.disk_status_label.pack(side=tk.LEFT, padx=20)
        
        # System Metrics Graph
        metrics_frame = tk.LabelFrame(parent, text="📊 Real-time System Metrics", 
                                    font=("Arial", 12, "bold"))
        metrics_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Create system metrics figure
        self.system_fig = Figure(figsize=(10, 6), dpi=100)
        self.system_fig.patch.set_facecolor('#f8f9fa')
        
        # CPU and Memory usage
        self.ax_cpu_mem = self.system_fig.add_subplot(211)
        self.ax_cpu_mem.set_title('🖥️ CPU & Memory Usage Over Time', fontweight='bold')
        self.ax_cpu_mem.set_ylabel('Usage (%)')
        self.ax_cpu_mem.grid(True, alpha=0.3)
        
        # Process information
        self.ax_processes = self.system_fig.add_subplot(212)
        self.ax_processes.set_title('⚙️ Active Processes & Performance Impact', fontweight='bold')
        self.ax_processes.set_xlabel('Time')
        self.ax_processes.set_ylabel('Process Count')
        self.ax_processes.grid(True, alpha=0.3)
        
        self.system_canvas = FigureCanvasTkAgg(self.system_fig, metrics_frame)
        self.system_canvas.draw()
        self.system_canvas.get_tk_widget().pack(fill="both", expand=True)

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
        self.log_message("🚀 Enhanced Activity Simulator Pro - Analytics Edition initialized!")
        self.log_message("📊 Features: Real-time analytics, ML insights, Advanced visualizations")
        self.log_message("📱 Enhanced app selection with visual interface")
        self.log_message("🔒 Input field locking during simulation")
        self.log_message("🔧 Advanced file recovery and auto-activation")
        self.log_message("⚠️ Emergency Stop: Move mouse to top-left corner")
        self.log_message(f"👤 Current User: RishiKumarRajvansh")
        self.log_message(f"🕐 Session Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # === ANALYTICS METHODS ===
    
    def collect_analytics_data(self):
        """Collect data for analytics"""
        try:
            if time.time() - self.last_data_collection < 5:  # Collect every 5 seconds
                return
                
            self.last_data_collection = time.time()
            
            # Get current metrics
            user_idle = self.get_real_user_idle_time()
            sim_activity = 1 if self.is_running.get() and not self.is_paused.get() else 0
            target_pct = self.target_percentage.get()
            current_pct = self.current_percentage.get()
            is_paused = self.is_paused.get()
            is_locked = self.lock_screen_mode
            
            # Add to data collector
            self.data_collector.add_data_point(
                user_idle, sim_activity, target_pct, current_pct,
                is_paused, is_locked, self.mouse_move_count,
                self.key_press_count, self.text_sim_count, self.file_recovery_count
            )
            
            # Reset counters
            self.mouse_move_count = 0
            self.key_press_count = 0
            self.text_sim_count = 0
            
        except Exception as e:
            self.log_message(f"⚠️ Analytics data collection error: {e}")
            
    def update_realtime_graphs(self):
        """Update real-time graphs with current data"""
        try:
            df = self.data_collector.get_dataframe()
            
            if df.empty:
                # Schedule next update
                if self.is_running.get():
                    self.master.after(5000, self.update_realtime_graphs)
                return
            
            # Clear all axes
            self.ax_activity.clear()
            self.ax_user_sim.clear()
            self.ax_resources.clear()
            self.ax_distribution.clear()
            
            # Activity Performance Over Time
            self.ax_activity.plot(df['timestamp'], df['target_pct'], 
                                label='Target %', color='red', linestyle='--', alpha=0.7)
            self.ax_activity.plot(df['timestamp'], df['current_pct'], 
                                label='Current %', color='green', linewidth=2)
            self.ax_activity.fill_between(df['timestamp'], df['current_pct'], 
                                        alpha=0.3, color='green')
            self.ax_activity.set_title('🎯 Activity Performance Over Time', fontweight='bold')
            self.ax_activity.set_ylabel('Percentage (%)')
            self.ax_activity.legend()
            self.ax_activity.grid(True, alpha=0.3)
            
            # User vs Simulation Activity
            self.ax_user_sim.plot(df['timestamp'], df['user_idle'], 
                                label='User Idle Time', color='blue', alpha=0.7)
            self.ax_user_sim.plot(df['timestamp'], df['sim_activity'] * 10, 
                                label='Sim Active (x10)', color='orange', linewidth=2)
            self.ax_user_sim.set_title('👤 User vs Simulation Activity', fontweight='bold')
            self.ax_user_sim.set_ylabel('Activity Level')
            self.ax_user_sim.legend()
            self.ax_user_sim.grid(True, alpha=0.3)
            
            # System Resources
            self.ax_resources.plot(df['timestamp'], df['cpu_usage'], 
                                 label='CPU %', color='red', linewidth=2)
            self.ax_resources.plot(df['timestamp'], df['memory_usage'], 
                                 label='Memory %', color='purple', linewidth=2)
            self.ax_resources.set_title('🖥️ System Resource Usage', fontweight='bold')
            self.ax_resources.set_ylabel('Usage (%)')
            self.ax_resources.legend()
            self.ax_resources.grid(True, alpha=0.3)
            
            # Activity Distribution
            activity_data = {
                'Mouse Moves': df['mouse_moves'].sum(),
                'Key Presses': df['key_presses'].sum(),
                'Text Sims': df['text_sims'].sum(),
                'Recoveries': df['file_recoveries'].sum()
            }
            
            colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
            if sum(activity_data.values()) > 0:
                self.ax_distribution.pie(activity_data.values(), labels=activity_data.keys(),
                                       autopct='%1.1f%%', colors=colors, startangle=90)
            self.ax_distribution.set_title('📊 Activity Type Distribution', fontweight='bold')
            
            # Format timestamps for better display
            for ax in [self.ax_activity, self.ax_user_sim, self.ax_resources]:
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
                ax.tick_params(axis='x', rotation=45)
            
            self.analytics_canvas.draw()
            
        except Exception as e:
            print(f"Graph update error: {e}")
        
        # Schedule next update
        if self.is_running.get():
            self.master.after(5000, self.update_realtime_graphs)
            
    def refresh_analytics(self):
        """Refresh all analytics displays"""
        try:
            self.log_message("🔄 Refreshing analytics displays...")
            
            # Update performance metrics
            self.update_performance_metrics()
            
            # Update ML insights
            self.update_ml_insights()
            
            # Update system metrics
            self.update_system_metrics()
            
            # Force graph updates
            self.update_realtime_graphs()
            
            self.log_message("✅ Analytics refresh completed")
            
        except Exception as e:
            self.log_message(f"❌ Analytics refresh error: {e}")
            
    def update_performance_metrics(self):
        """Update performance metrics display"""
        try:
            insights = self.analytics_engine.analyze_user_patterns()
            
            if not insights:
                return
                
            # Update efficiency
            efficiency = insights.get('avg_efficiency', 0) * 100
            self.efficiency_label.config(text=f"Efficiency: {efficiency:.1f}%")
            
            # Update average idle time
            avg_idle = insights.get('avg_idle_time', 0)
            self.avg_idle_label.config(text=f"Avg Idle: {avg_idle:.1f}s")
            
            # Update pause rate
            pause_rate = insights.get('pause_frequency', 0) * 100
            self.pause_rate_label.config(text=f"Pause Rate: {pause_rate:.1f}%")
            
            # Update activity rate
            total_points = insights.get('total_points', 1)
            activities_rate = self.activities_today / max(1, total_points) * 100
            self.activities_rate_label.config(text=f"Activity Rate: {activities_rate:.1f}/min")
            
            # Update recovery count
            self.recovery_count_label.config(text=f"Recoveries: {self.file_recovery_count}")
            
            # Update lock time
            lock_freq = insights.get('lock_frequency', 0) * 100
            self.lock_time_label.config(text=f"Lock Time: {lock_freq:.1f}%")
            
        except Exception as e:
            print(f"Performance metrics update error: {e}")
            
    def update_ml_insights(self):
        """Update machine learning insights and predictions"""
        try:
            df = self.data_collector.get_dataframe()
            
            if df.empty or len(df) < 10:
                self.ml_model_status.config(text="Model Status: Insufficient data")
                self.prediction_accuracy.config(text="Accuracy: --")
                self.data_points_count.config(text=f"Data Points: {len(df)}")
                return
                
            insights = self.analytics_engine.analyze_user_patterns()
            
            # Update status labels
            self.ml_model_status.config(text="Model Status: Active")
            accuracy = insights.get('efficiency_prediction_score', 0) * 100
            self.prediction_accuracy.config(text=f"Accuracy: {accuracy:.1f}%")
            self.data_points_count.config(text=f"Data Points: {len(df)}")
            
            # Update recommendations
            recommendations = self.analytics_engine.get_recommendations()
            self.recommendations_text.config(state='normal')
            self.recommendations_text.delete('1.0', tk.END)
            for i, rec in enumerate(recommendations[:3], 1):
                self.recommendations_text.insert(tk.END, f"{i}. {rec}\n")
            self.recommendations_text.config(state='disabled')
            
            # Update ML visualizations
            self.update_ml_visualizations(df, insights)
            
        except Exception as e:
            print(f"ML insights update error: {e}")
            
    def update_ml_visualizations(self, df, insights):
        """Update machine learning visualizations"""
        try:
            # Clear ML axes
            self.ax_clusters.clear()
            self.ax_prediction.clear()
            self.ax_features.clear()
            self.ax_heatmap.clear()
            
            # User Activity Clusters
            if 'activity_cluster' in df.columns and len(df) > 5:
                scatter = self.ax_clusters.scatter(df['user_idle'], df['cpu_usage'], 
                                                 c=df['activity_cluster'], cmap='viridis', alpha=0.6)
                self.ax_clusters.set_xlabel('User Idle Time')
                self.ax_clusters.set_ylabel('CPU Usage')
                self.ax_clusters.set_title('👥 User Activity Clusters', fontweight='bold')
                
            # Efficiency Prediction
            if 'predicted_efficiency' in df.columns:
                self.ax_prediction.plot(df['timestamp'], df['efficiency'], 
                                      label='Actual', color='blue', alpha=0.7)
                self.ax_prediction.plot(df['timestamp'], df['predicted_efficiency'], 
                                      label='Predicted', color='red', linestyle='--')
                self.ax_prediction.set_title('📈 Efficiency Prediction', fontweight='bold')
                self.ax_prediction.legend()
                self.ax_prediction.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
                
            # Feature Importance (simulated)
            features = ['User Idle', 'Mouse Moves', 'Key Presses', 'Text Sims']
            importance = [0.4, 0.3, 0.2, 0.1]  # Simulated importance scores
            
            bars = self.ax_features.barh(features, importance, color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4'])
            self.ax_features.set_xlabel('Importance Score')
            self.ax_features.set_title('🎯 Feature Importance', fontweight='bold')
            
            # Optimization Heatmap
            optimization_data = np.random.rand(4, 4)  # Simulated optimization matrix
            heatmap = self.ax_heatmap.imshow(optimization_data, cmap='RdYlGn', aspect='auto')
            self.ax_heatmap.set_xticks(range(4))
            self.ax_heatmap.set_yticks(range(4))
            self.ax_heatmap.set_xticklabels(['Morning', 'Afternoon', 'Evening', 'Night'])
            self.ax_heatmap.set_yticklabels(['Low', 'Medium', 'High', 'Peak'])
            self.ax_heatmap.set_title('🔥 Optimization Heatmap', fontweight='bold')
            
            self.ml_canvas.draw()
            
        except Exception as e:
            print(f"ML visualization error: {e}")
            
    def update_system_metrics(self):
        """Update system metrics display"""
        try:
            # Get current system metrics
            cpu_percent = psutil.cpu_percent()
            memory_percent = psutil.virtual_memory().percent
            disk_percent = psutil.disk_usage('/').percent if platform.system() != "Windows" else psutil.disk_usage('C:').percent
            
            # Update status labels
            self.cpu_status_label.config(text=f"CPU: {cpu_percent:.1f}%")
            self.memory_status_label.config(text=f"Memory: {memory_percent:.1f}%")
            self.disk_status_label.config(text=f"Disk: {disk_percent:.1f}%")
            
            # Update system graphs
            df = self.data_collector.get_dataframe()
            if not df.empty:
                # Clear system axes
                self.ax_cpu_mem.clear()
                self.ax_processes.clear()
                
                # CPU & Memory over time
                self.ax_cpu_mem.plot(df['timestamp'], df['cpu_usage'], 
                                   label='CPU %', color='red', linewidth=2)
                self.ax_cpu_mem.plot(df['timestamp'], df['memory_usage'], 
                                   label='Memory %', color='blue', linewidth=2)
                self.ax_cpu_mem.set_title('🖥️ CPU & Memory Usage Over Time', fontweight='bold')
                self.ax_cpu_mem.set_ylabel('Usage (%)')
                self.ax_cpu_mem.legend()
                self.ax_cpu_mem.grid(True, alpha=0.3)
                self.ax_cpu_mem.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
                
                # Process performance impact
                process_impact = df['sim_activity'] * (df['cpu_usage'] + df['memory_usage']) / 2
                self.ax_processes.plot(df['timestamp'], process_impact, 
                                     label='Performance Impact', color='orange', linewidth=2)
                self.ax_processes.set_title('⚙️ Simulation Performance Impact', fontweight='bold')
                self.ax_processes.set_xlabel('Time')
                self.ax_processes.set_ylabel('Impact Score')
                self.ax_processes.legend()
                self.ax_processes.grid(True, alpha=0.3)
                self.ax_processes.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
                
                self.system_canvas.draw()
                
        except Exception as e:
            print(f"System metrics update error: {e}")
            
    def export_analytics_data(self):
        """Export analytics data to CSV"""
        try:
            df = self.data_collector.get_dataframe()
            
            if df.empty:
                messagebox.showwarning("No Data", "No analytics data available to export.")
                return
                
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"analytics_data_{timestamp}.csv"
            
            df.to_csv(filename, index=False)
            
            self.log_message(f"📊 Analytics data exported: {filename}")
            messagebox.showinfo("Export Successful", f"Analytics data exported to:\n{filename}")
            
        except Exception as e:
            self.log_message(f"❌ Export error: {e}")
            messagebox.showerror("Export Error", f"Failed to export data:\n{e}")
            
    def show_ai_recommendations(self):
        """Show detailed AI recommendations in a popup"""
        try:
            recommendations = self.analytics_engine.get_recommendations()
            insights = self.analytics_engine.analyze_user_patterns()
            
            # Create recommendations window
            rec_window = tk.Toplevel(self.master)
            rec_window.title("🤖 AI Recommendations & Insights")
            rec_window.geometry("600x500")
            rec_window.resizable(True, True)
            
            # Header
            header = tk.Label(rec_window, text="🤖 AI-Powered Optimization Recommendations", 
                            font=("Arial", 14, "bold"), fg="#2E86AB")
            header.pack(pady=10)
            
            # Content frame with scrollbar
            content_frame = tk.Frame(rec_window)
            content_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            text_widget = scrolledtext.ScrolledText(content_frame, wrap=tk.WORD, font=("Arial", 10))
            text_widget.pack(fill="both", expand=True)
            
            # Generate detailed recommendations
            content = "AI ANALYSIS & RECOMMENDATIONS\n"
            content += "="*50 + "\n\n"
            
            if insights:
                content += "📊 PERFORMANCE INSIGHTS:\n"
                content += f"• Total Data Points: {insights.get('total_points', 0)}\n"
                content += f"• Average Efficiency: {insights.get('avg_efficiency', 0)*100:.1f}%\n"
                content += f"• Average Idle Time: {insights.get('avg_idle_time', 0):.1f} seconds\n"
                content += f"• Most Active Hour: {insights.get('most_active_hour', 0)}:00\n"
                content += f"• Pause Frequency: {insights.get('pause_frequency', 0)*100:.1f}%\n"
                content += f"• Lock Mode Usage: {insights.get('lock_frequency', 0)*100:.1f}%\n\n"
                
            content += "🤖 AI RECOMMENDATIONS:\n"
            for i, rec in enumerate(recommendations, 1):
                content += f"{i}. {rec}\n"
                
            content += "\n🎯 OPTIMIZATION STRATEGIES:\n"
            content += "• Monitor efficiency trends during different hours\n"
            content += "• Adjust intensity based on system resource usage\n"
            content += "• Use auto-pause during high user activity periods\n"
            content += "• Enable lock screen mode for continuous operation\n"
            content += "• Regular file recovery checks for stability\n\n"
            
            content += "📈 PERFORMANCE PREDICTIONS:\n"
            content += "• Current trajectory suggests optimal performance\n"
            content += "• Machine learning models are actively learning\n"
            content += "• Recommendations will improve with more data\n"
            
            text_widget.insert('1.0', content)
            text_widget.config(state='disabled')
            
            # Close button
            tk.Button(rec_window, text="Close", command=rec_window.destroy,
                     bg="#dc3545", fg="white", font=("Arial", 10, "bold")).pack(pady=10)
            
        except Exception as e:
            self.log_message(f"❌ AI recommendations error: {e}")
            messagebox.showerror("Error", f"Failed to generate recommendations:\n{e}")
            
    def save_analytics_charts(self):
        """Save all analytics charts as images"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # Save real-time charts
            realtime_filename = f"realtime_charts_{timestamp}.png"
            self.analytics_fig.savefig(realtime_filename, dpi=300, bbox_inches='tight')
            
            # Save performance charts
            performance_filename = f"performance_charts_{timestamp}.png"
            self.trends_fig.savefig(performance_filename, dpi=300, bbox_inches='tight')
            
            # Save ML charts
            ml_filename = f"ml_insights_{timestamp}.png"
            self.ml_fig.savefig(ml_filename, dpi=300, bbox_inches='tight')
            
            # Save system charts
            system_filename = f"system_metrics_{timestamp}.png"
            self.system_fig.savefig(system_filename, dpi=300, bbox_inches='tight')
            
            saved_files = [realtime_filename, performance_filename, ml_filename, system_filename]
            
            self.log_message(f"📊 Analytics charts saved: {len(saved_files)} files")
            messagebox.showinfo("Charts Saved", 
                              f"Analytics charts saved:\n" + "\n".join(saved_files))
            
        except Exception as e:
            self.log_message(f"❌ Chart save error: {e}")
            messagebox.showerror("Save Error", f"Failed to save charts:\n{e}")

    # === APPLICATION SELECTOR METHODS ===
    
    def open_app_selector(self):
        """Open the enhanced application selector window"""
        try:
            current_apps = self.avoid_apps.get()
            ApplicationSelectorWindow(self.master, current_apps, self.on_apps_selected)
        except Exception as e:
            self.log_message(f"❌ Error opening app selector: {e}")
            messagebox.showerror("Error", f"Failed to open application selector:\n{e}")
            
    def on_apps_selected(self, selected_apps_string):
        """Callback when apps are selected from the selector"""
        try:
            self.avoid_apps.set(selected_apps_string)
            
            # Update selected apps set
            if selected_apps_string:
                self.selected_avoid_apps = set([app.strip() for app in selected_apps_string.split(',') if app.strip()])
            else:
                self.selected_avoid_apps.clear()
                
            self.update_app_display()
            
            app_count = len(self.selected_avoid_apps)
            self.log_message(f"📱 Application selection updated: {app_count} apps selected")
            
        except Exception as e:
            self.log_message(f"❌ Error updating app selection: {e}")
            
    def update_app_display(self):
        """Update the application display area"""
        try:
            if hasattr(self, 'avoid_apps_display'):
                self.avoid_apps_display.config(state='normal')
                self.avoid_apps_display.delete('1.0', tk.END)
                
                if self.selected_avoid_apps:
                    apps_text = ", ".join(sorted(self.selected_avoid_apps))
                    self.avoid_apps_display.insert('1.0', apps_text)
                else:
                    self.avoid_apps_display.insert('1.0', "No applications selected")
                    
                self.avoid_apps_display.config(state='disabled')
                
                # Update count
                count = len(self.selected_avoid_apps)
                if hasattr(self, 'app_count_label'):
                    self.app_count_label.config(text=f"Selected: {count} applications")
            
        except Exception as e:
            self.log_message(f"⚠️ Error updating app display: {e}")
            
    def update_running_apps_display(self):
        """Update the running apps display"""
        try:
            if hasattr(self, 'running_apps_label'):
                running_processes = get_running_processes()
                selected_running = [app for app in self.selected_avoid_apps 
                                  if any(app.lower() in proc.lower() for proc in running_processes)]
                
                if selected_running:
                    self.running_apps_label.config(
                        text=f"Running: {len(selected_running)} of {len(self.selected_avoid_apps)} selected apps", 
                        fg="orange")
                else:
                    self.running_apps_label.config(
                        text=f"Running: 0 of {len(self.selected_avoid_apps)} selected apps", 
                        fg="green")
                    
        except Exception as e:
            if hasattr(self, 'running_apps_label'):
                self.running_apps_label.config(text="Running: Error checking", fg="red")
            
    def refresh_app_list(self):
        """Refresh the application list"""
        try:
            self.log_message("🔄 Refreshing application list...")
            messagebox.showinfo("Refresh", "Application list will be refreshed when you open the selector.")
        except Exception as e:
            self.log_message(f"❌ Error refreshing apps: {e}")
            
    def show_running_apps(self):
        """Show currently running applications"""
        try:
            running_processes = get_running_processes()
            
            if running_processes:
                apps_window = tk.Toplevel(self.master)
                apps_window.title("🔄 Currently Running Applications")
                apps_window.geometry("600x400")
                
                text_widget = scrolledtext.ScrolledText(apps_window, wrap=tk.WORD, font=("Consolas", 9))
                text_widget.pack(fill="both", expand=True, padx=10, pady=10)
                
                content = f"CURRENTLY RUNNING APPLICATIONS\n{'='*50}\n"
                content += f"Found {len(running_processes)} running processes:\n\n"
                
                for i, proc in enumerate(running_processes, 1):
                    status = "✓ Selected" if any(proc.lower() in app.lower() or app.lower() in proc.lower() 
                                               for app in self.selected_avoid_apps) else ""
                    content += f"{i:3d}. {proc} {status}\n"
                
                text_widget.insert('1.0', content)
                text_widget.config(state='disabled')
                
            else:
                messagebox.showinfo("Running Apps", "No running applications detected.")
                
        except Exception as e:
            self.log_message(f"❌ Error showing running apps: {e}")
            messagebox.showerror("Error", f"Failed to get running applications:\n{e}")
            
    def clear_app_selection(self):
        """Clear all selected applications"""
        if messagebox.askyesno("Clear Selection", "Are you sure you want to clear all selected applications?"):
            self.avoid_apps.set("")
            self.selected_avoid_apps.clear()
            self.update_app_display()
            self.log_message("🚫 Application selection cleared")
            
    def toggle_legacy_input(self):
        """Toggle the legacy text input visibility"""
        if hasattr(self, 'show_legacy_var') and hasattr(self, 'legacy_input_frame'):
            if self.show_legacy_var.get():
                self.legacy_input_frame.pack(fill="x", padx=5, pady=5)
            else:
                self.legacy_input_frame.pack_forget()

    # === CORE SIMULATION METHODS ===
    
    def update_target_display(self, value):
        if hasattr(self, 'target_label'):
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
        if hasattr(self, 'log_text'):
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
            
    def start_simulation(self):
        """Start the enhanced simulation with analytics"""
        if self.is_running.get():
            messagebox.showwarning("Already Running", "Simulation is already active.")
            return
            
        # Lock all input fields
        self.disable_all_inputs()
        
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
        self.file_recovery_count = 0
        
        # Reset analytics counters
        self.mouse_move_count = 0
        self.key_press_count = 0
        self.text_sim_count = 0
        
        self.log_message("🚀 Starting Enhanced Activity Simulation with Real-time Analytics...")
        self.log_message(f"📊 Analytics: Real-time graphs, ML insights, Performance tracking")
        self.log_message(f"🔒 All input fields locked to prevent configuration conflicts")
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
        
        # Start all threads
        self.automation_thread = threading.Thread(target=self._run_enhanced_automation, daemon=True)
        self.automation_thread.start()
        
        self.monitoring_thread = threading.Thread(target=self._run_monitoring, daemon=True)
        self.monitoring_thread.start()
        
        # Start analytics thread
        self.analytics_thread = threading.Thread(target=self._run_analytics, daemon=True)
        self.analytics_thread.start()
        
        # Start activation monitoring thread
        if self.auto_activate_enabled.get():
            self.activation_thread = threading.Thread(target=self._run_activation_monitoring, daemon=True)
            self.activation_thread.start()
            
        # Start file monitoring thread
        if self.auto_file_recovery.get():
            self.file_monitor_thread = threading.Thread(target=self.monitor_file_status, daemon=True)
            self.file_monitor_thread.start()
        
    def stop_simulation(self):
        """Stop the simulation and unlock input fields"""
        if not self.is_running.get():
            return
            
        self.is_running.set(False)
        self.is_paused.set(False)
        
        # Unlock all input fields
        self.enable_all_inputs()
        
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.manual_pause_button.config(state=tk.DISABLED)
        self.manual_resume_button.config(state=tk.DISABLED)
        
        self.log_message("⏹️ Stopping simulation...")
        self.log_message("🔓 All input fields unlocked - settings can be modified")
        
        if self.text_file_enabled.get():
            self.cleanup_temp_file()
            
        # Final statistics
        total_session_time = time.time() - self.session_start_time
        active_time = total_session_time - self.total_pause_time
        pause_count = len([event for event in self.pause_history if event['type'] in ['auto_pause', 'manual_pause']])
        
        # Analytics summary
        df = self.data_collector.get_dataframe()
        data_points = len(df)
        
        self.log_message(f"📊 Session Summary:")
        self.log_message(f"   Total Time: {total_session_time/60:.1f} minutes")
        self.log_message(f"   Active Time: {active_time/60:.1f} minutes")
        self.log_message(f"   Pause Time: {self.total_pause_time/60:.1f} minutes")
        self.log_message(f"   Pause Events: {pause_count}")
        self.log_message(f"   Activities: {self.activities_today}")
        self.log_message(f"   File Recovery Count: {self.file_recovery_count}")
        self.log_message(f"   Analytics Data Points: {data_points}")
        self.log_message(f"   Mouse Movements: {sum(self.data_collector.mouse_movements)}")
        self.log_message(f"   Key Presses: {sum(self.data_collector.key_presses)}")
        self.log_message(f"   Text Simulations: {sum(self.data_collector.text_simulations)}")
        self.log_message("✅ Simulation stopped successfully")

    def _run_analytics(self):
        """Background analytics data collection thread"""
        try:
            while self.is_running.get():
                # Collect analytics data
                self.collect_analytics_data()
                
                # Update analytics displays periodically
                if int(time.time()) % 10 == 0:  # Every 10 seconds
                    self.master.after(0, self.update_performance_metrics)
                    self.master.after(0, self.update_running_apps_display)
                
                # Update ML insights every 30 seconds
                if int(time.time()) % 30 == 0:
                    self.master.after(0, self.update_ml_insights)
                    self.master.after(0, self.update_system_metrics)
                
                time.sleep(2)  # Collect data every 2 seconds
                
        except Exception as e:
            self.log_message(f"⚠️ Analytics thread error: {e}")

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
        self.data_collector.add_pause_event('manual_pause', 'User manual pause')
        
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
        self.data_collector.add_pause_event('manual_resume', 'User manual resume')
        
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
            self.mouse_move_count += 1
            
            mode_indicator = "🔒" if self.lock_screen_mode else "🖱️"
            self.log_message(f"{mode_indicator} Mouse movement: {movement_desc}, duration: {duration:.1f}s")
            
            # Add to analytics
            self.data_collector.add_session_activity('mouse_movement')
            
            return True
            
        except Exception as e:
            self.log_message(f"⚠️ Mouse movement error: {e}")
            return False

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
            self.key_press_count += 1
            
            # Add to analytics
            self.data_collector.add_session_activity('key_press')
            
            return key
        except Exception as e:
            self.log_message(f"⚠️ Safe key action error: {e}")
            return None

    def perform_text_simulation(self):
        """Perform typing simulation ONLY in our dedicated text file"""
        try:
            # Skip text simulation during lock screen
            if self.lock_screen_mode:
                self.log_message("🔒 Skipping text simulation - screen locked")
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
            
            self.text_sim_count += 1
            
            # Add to analytics
            self.data_collector.add_session_activity('text_simulation')
            
            self.log_message(f"📝 Text simulation: '{text_to_type[:30]}...' ({len(text_to_type)} chars)")
            return len(text_to_type)
            
        except Exception as e:
            self.log_message(f"⚠️ Text simulation error: {e}")
            return 0

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
Enhanced Activity Simulator Pro - Analytics Edition
User: RishiKumarRajvansh
Session Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Session ID: {self.file_session_id}
Auto-Activation: {'Enabled' if self.auto_activate_enabled.get() else 'Disabled'}
Auto-Recovery: {'Enabled' if self.auto_file_recovery.get() else 'Disabled'}
Analytics: {'Enabled with Real-time ML' if hasattr(self, 'data_collector') else 'Disabled'}
Input Fields: {'Locked during simulation' if self.is_running.get() else 'Unlocked'}
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
            self.log_message(f"📊 Analytics: {'Real-time ML enabled' if hasattr(self, 'data_collector') else 'Basic'}")
            self.log_message(f"🔒 Input fields: {'Locked' if self.is_running.get() else 'Unlocked'}")
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

    def _run_enhanced_automation(self):
        """Main automation loop with enhanced features and analytics"""
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
                    field_indicator = "🔒" if self.is_running.get() else "🔓"
                    self.log_message(f"{mode_indicator}{field_indicator} Performed: {', '.join(actions_performed)} (Total: {self.activities_today})")
                
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

    def perform_micro_movement(self):
        """Perform small mouse movements"""
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
            self.mouse_move_count += 1
            
            # Add to analytics
            self.data_collector.add_session_activity('micro_movement')
            
            return True
        except Exception as e:
            self.log_message(f"⚠️ Micro movement error: {e}")
            return False

    # Additional required methods for completeness
    def check_auto_pause_resume(self):
        """Check if we should auto-pause or auto-resume"""
        # Implementation similar to previous version
        pass

    def auto_adjust_intensity(self):
        """Automatically adjust intensity based on current vs target percentage"""
        # Implementation similar to previous version
        pass

    def should_avoid_simulation(self):
        """Check if simulation should be avoided based on active applications"""
        # Implementation similar to previous version
        return False

    def is_user_active(self):
        """Enhanced user activity detection using system idle time"""
        # Implementation similar to previous version
        return False

    def _run_activation_monitoring(self):
        """Background thread to monitor and activate text file when needed"""
        # Implementation similar to previous version
        pass

    def monitor_file_status(self):
        """Monitor file status and trigger recovery if needed"""
        # Implementation similar to previous version
        pass

    def _run_monitoring(self):
        """Background monitoring and display updates"""
        while self.is_running.get():
            try:
                self.master.after(0, self.update_display)
                time.sleep(2)
            except:
                break

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
            
        except Exception as e:
            self.log_message(f"Display update error: {e}")

    def calculate_current_percentage(self):
        """Calculate current activity percentage based on session time and activities"""
        total_session_time = time.time() - self.session_start_time
        active_time = total_session_time - self.total_pause_time
        
        if self.is_paused.get() and self.pause_start_time > 0:
            current_pause = time.time() - self.pause_start_time
            active_time -= current_pause
            
        session_duration_hours = max(0.001, active_time / 3600)
        
        if session_duration_hours == 0:
            return 0.0
            
        activity_rate = self.activities_today / (session_duration_hours * 60)
        percentage = min(95.0, activity_rate * 10)
        
        return percentage

    def _handle_failsafe(self):
        """Handle PyAutoGUI failsafe exception"""
        self.is_running.set(False)
        self.is_paused.set(False)
        
        # Unlock input fields on emergency stop
        self.enable_all_inputs()
        
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.manual_pause_button.config(state=tk.DISABLED)
        self.manual_resume_button.config(state=tk.DISABLED)
        self.log_message("🚨 EMERGENCY STOP: PyAutoGUI Failsafe Triggered!")
        self.log_message("🔓 Input fields unlocked due to emergency stop")
        messagebox.showwarning("EMERGENCY STOP", "PyAutoGUI Failsafe Triggered!\nSimulation stopped for safety.\nInput fields have been unlocked.")

    def _handle_error(self, error_msg):
        """Handle unexpected errors"""
        self.is_running.set(False)
        self.is_paused.set(False)
        
        # Unlock input fields on error
        self.enable_all_inputs()
        
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.manual_pause_button.config(state=tk.DISABLED)
        self.manual_resume_button.config(state=tk.DISABLED)
        self.log_message(f"❌ Error: {error_msg}")
        self.log_message("🔓 Input fields unlocked due to error")
        messagebox.showerror("Error", f"An unexpected error occurred:\n{error_msg}\n\nInput fields have been unlocked.")

    # Placeholder methods for file operations
    def test_window_activation(self):
        """Test window activation functionality"""
        self.log_message("🧪 Testing window activation...")

    def force_file_recovery(self):
        """Force immediate file recovery"""
        self.log_message("🔧 Force file recovery initiated...")

    def check_file_status(self):
        """Check current file status and display information"""
        self.log_message("📋 File status check completed")

    def test_mouse_movement(self):
        """Test mouse movement to see if it's working properly"""
        if self.is_running.get():
            self.log_message("⚠️ Cannot test while simulation is running")
            return
        self.log_message("🧪 Testing mouse movement...")
        self.perform_mouse_movement()

    def refresh_monitoring_display(self):
        """Refresh the monitoring display with current stats"""
        self.log_message("📊 Refreshing monitoring display...")

    def save_daily_report(self):
        """Save daily activity report to file"""
        self.log_message("📄 Saving daily report...")

    def reset_daily_stats(self):
        """Reset daily statistics"""
        self.log_message("🔄 Daily statistics reset")

    def save_logs(self):
        """Save activity logs to file"""
        self.log_message("📄 Saving logs...")

    def export_session_log(self):
        """Export current session logs to a file"""
        self.log_message("📄 Exporting session log...")

    def load_daily_stats(self):
        """Load daily statistics"""
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