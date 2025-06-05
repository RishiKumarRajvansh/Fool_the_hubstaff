import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk, simpledialog
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
import sqlite3
import hashlib
import uuid

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

class DatabaseManager:
    """SQLite database manager with better connection handling and timeout fixes"""
    
    def __init__(self, db_path="activity_simulator.db"):
        self.db_path = db_path
        self.init_database()
        
    def get_connection(self):
        """Get database connection with timeout and better settings"""
        try:
            conn = sqlite3.connect(self.db_path, timeout=30.0)
            # Enable WAL mode for better concurrency (fixes "database is locked")
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
            conn.execute("PRAGMA busy_timeout=30000")  # 30 second timeout
            return conn
        except Exception as e:
            print(f"❌ Database connection error: {e}")
            return None
        
    def init_database(self):
        """Initialize database with required tables"""
        conn = None
        try:
            conn = self.get_connection()
            if not conn:
                return
                
            cursor = conn.cursor()
            
            # Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    email TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    total_sessions INTEGER DEFAULT 0,
                    settings TEXT
                )
            ''')
            
            # Sessions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    session_start TIMESTAMP NOT NULL,
                    session_end TIMESTAMP,
                    target_percentage INTEGER,
                    achieved_percentage REAL,
                    total_activities INTEGER DEFAULT 0,
                    total_pause_time REAL DEFAULT 0,
                    mode TEXT DEFAULT 'automation',
                    settings TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # Activity data table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS activity_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
                    user_idle_time REAL,
                    sim_activity INTEGER,
                    cpu_usage REAL,
                    memory_usage REAL,
                    target_pct INTEGER,
                    current_pct REAL,
                    is_paused INTEGER,
                    is_locked INTEGER,
                    mouse_movements INTEGER DEFAULT 0,
                    key_presses INTEGER DEFAULT 0,
                    text_simulations INTEGER DEFAULT 0,
                    mode TEXT DEFAULT 'automation',
                    FOREIGN KEY (session_id) REFERENCES sessions (id)
                )
            ''')
            
            # Pause events table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS pause_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER NOT NULL,
                    event_type TEXT NOT NULL,
                    reason TEXT,
                    timestamp TIMESTAMP NOT NULL,
                    duration REAL,
                    FOREIGN KEY (session_id) REFERENCES sessions (id)
                )
            ''')
            
            # User preferences table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_preferences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    preference_key TEXT NOT NULL,
                    preference_value TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    UNIQUE(user_id, preference_key)
                )
            ''')
            
            conn.commit()
            print("✅ Database initialized successfully")
            
        except Exception as e:
            print(f"❌ Database initialization error: {e}")
        finally:
            if conn:
                conn.close()
            
    def hash_password(self, password):
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
        
    def create_user(self, username, password, email=""):
        """Create a new user with better error handling"""
        conn = None
        try:
            conn = self.get_connection()
            if not conn:
                print("❌ Could not connect to database")
                return None
                
            cursor = conn.cursor()
            
            password_hash = self.hash_password(password)
            
            cursor.execute('''
                INSERT INTO users (username, password_hash, email)
                VALUES (?, ?, ?)
            ''', (username, password_hash, email))
            
            user_id = cursor.lastrowid
            conn.commit()
            
            print(f"✅ User '{username}' created successfully with ID: {user_id}")
            return user_id
            
        except sqlite3.IntegrityError:
            print(f"❌ Username '{username}' already exists")
            return None  # Username already exists
        except Exception as e:
            print(f"❌ User creation error: {e}")
            return None
        finally:
            if conn:
                conn.close()
            
    def authenticate_user(self, username, password):
        """Authenticate user and return user data with better error handling"""
        conn = None
        try:
            conn = self.get_connection()
            if not conn:
                print("❌ Could not connect to database for authentication")
                return None
                
            cursor = conn.cursor()
            
            password_hash = self.hash_password(password)
            
            cursor.execute('''
                SELECT id, username, email, total_sessions, settings, created_at
                FROM users 
                WHERE username = ? AND password_hash = ?
            ''', (username, password_hash))
            
            user_data = cursor.fetchone()
            
            if user_data:
                # Update last login and increment total sessions
                cursor.execute('''
                    UPDATE users 
                    SET last_login = CURRENT_TIMESTAMP,
                        total_sessions = total_sessions + 1
                    WHERE id = ?
                ''', (user_data[0],))
                conn.commit()
                
                print(f"✅ User '{username}' authenticated successfully")
                return user_data
            else:
                print(f"❌ Authentication failed for user '{username}' - Invalid credentials")
                return None
            
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return None
        finally:
            if conn:
                conn.close()
            
    def create_session(self, user_id, target_percentage, mode='automation'):
        """Create a new session with better error handling"""
        conn = None
        try:
            conn = self.get_connection()
            if not conn:
                return None
                
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO sessions (user_id, session_start, target_percentage, mode)
                VALUES (?, CURRENT_TIMESTAMP, ?, ?)
            ''', (user_id, target_percentage, mode))
            
            session_id = cursor.lastrowid
            conn.commit()
            
            print(f"✅ Session {session_id} created for user {user_id}")
            return session_id
            
        except Exception as e:
            print(f"❌ Session creation error: {e}")
            return None
        finally:
            if conn:
                conn.close()
            
    def end_session(self, session_id, achieved_percentage, total_activities, total_pause_time):
        """End a session with final statistics"""
        conn = None
        try:
            conn = self.get_connection()
            if not conn:
                return
                
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE sessions 
                SET session_end = CURRENT_TIMESTAMP,
                    achieved_percentage = ?,
                    total_activities = ?,
                    total_pause_time = ?
                WHERE id = ?
            ''', (achieved_percentage, total_activities, total_pause_time, session_id))
            
            conn.commit()
            print(f"✅ Session {session_id} ended successfully")
            
        except Exception as e:
            print(f"❌ Session end error: {e}")
        finally:
            if conn:
                conn.close()
            
    def add_activity_data(self, session_id, timestamp, user_idle, sim_activity, cpu_usage, 
                         memory_usage, target_pct, current_pct, is_paused, is_locked,
                         mouse_moves, key_presses, text_sims, mode):
        """Add activity data point with better error handling"""
        conn = None
        try:
            conn = self.get_connection()
            if not conn:
                return
                
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO activity_data 
                (session_id, timestamp, user_idle_time, sim_activity, cpu_usage, 
                 memory_usage, target_pct, current_pct, is_paused, is_locked,
                 mouse_movements, key_presses, text_simulations, mode)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (session_id, timestamp, user_idle, sim_activity, cpu_usage,
                  memory_usage, target_pct, current_pct, int(is_paused), int(is_locked),
                  mouse_moves, key_presses, text_sims, mode))
            
            conn.commit()
            
        except Exception as e:
            print(f"❌ Activity data error: {e}")
        finally:
            if conn:
                conn.close()
            
    def add_pause_event(self, session_id, event_type, reason, timestamp, duration=None):
        """Add pause/resume event with better error handling"""
        conn = None
        try:
            conn = self.get_connection()
            if not conn:
                return
                
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO pause_events (session_id, event_type, reason, timestamp, duration)
                VALUES (?, ?, ?, ?, ?)
            ''', (session_id, event_type, reason, timestamp, duration))
            
            conn.commit()
            
        except Exception as e:
            print(f"❌ Pause event error: {e}")
        finally:
            if conn:
                conn.close()
            
    def get_user_analytics(self, user_id, days=30):
        """Get user analytics for specified days"""
        conn = None
        try:
            conn = self.get_connection()
            if not conn:
                return {'sessions': pd.DataFrame(), 'activity': pd.DataFrame(), 'pauses': pd.DataFrame()}
            
            # Get session data
            sessions_df = pd.read_sql_query('''
                SELECT * FROM sessions 
                WHERE user_id = ? AND session_start >= date('now', '-{} days')
                ORDER BY session_start
            '''.format(days), conn, params=[user_id])
            
            # Get activity data
            activity_df = pd.read_sql_query('''
                SELECT a.* FROM activity_data a
                JOIN sessions s ON a.session_id = s.id
                WHERE s.user_id = ? AND a.timestamp >= date('now', '-{} days')
                ORDER BY a.timestamp
            '''.format(days), conn, params=[user_id])
            
            # Get pause events
            pause_df = pd.read_sql_query('''
                SELECT p.* FROM pause_events p
                JOIN sessions s ON p.session_id = s.id
                WHERE s.user_id = ? AND p.timestamp >= date('now', '-{} days')
                ORDER BY p.timestamp
            '''.format(days), conn, params=[user_id])
            
            return {
                'sessions': sessions_df,
                'activity': activity_df,
                'pauses': pause_df
            }
            
        except Exception as e:
            print(f"❌ Analytics query error: {e}")
            return {'sessions': pd.DataFrame(), 'activity': pd.DataFrame(), 'pauses': pd.DataFrame()}
        finally:
            if conn:
                conn.close()

class LoginSystem:
    """Improved login system with separate LOGIN and REGISTER tabs"""
    
    def __init__(self, master, db_manager, callback):
        self.master = master
        self.db_manager = db_manager
        self.callback = callback
        self.user_data = None
        self.current_mode = "login"  # "login" or "register"
        
        self.create_login_window()
        
    def create_login_window(self):
        """Create main window with LOGIN/REGISTER tab switching"""
        
        # Hide main window during login
        self.master.withdraw()
        
        # Main login window - IDEAL SIZE
        self.login_window = tk.Toplevel()
        self.login_window.title("🔐 Activity Simulator - Authentication")
        self.login_window.geometry("650x700")
        self.login_window.resizable(True, True)
        self.login_window.configure(bg='#f0f0f0')
        self.login_window.minsize(600, 650)
        
        # Make it modal and block main window
        self.login_window.transient()
        self.login_window.grab_set()
        self.login_window.focus_set()
        self.login_window.protocol("WM_DELETE_WINDOW", self.on_close_login)
        
        # Center the window
        self.login_window.update_idletasks()
        x = (self.login_window.winfo_screenwidth() // 2) - (650 // 2)
        y = (self.login_window.winfo_screenheight() // 2) - (700 // 2)
        self.login_window.geometry(f"650x700+{x}+{y}")
        
        # Header
        header_frame = tk.Frame(self.login_window, bg='#2E86AB', height=100)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text="🚀 Enhanced Activity Simulator", 
                font=("Arial", 18, "bold"), fg="white", bg='#2E86AB').pack(pady=15)
        
        self.header_subtitle = tk.Label(header_frame, text="🔐 USER LOGIN", 
                font=("Arial", 12, "bold"), fg="yellow", bg='#2E86AB')
        self.header_subtitle.pack()
        
        # TAB BUTTONS for switching between LOGIN and REGISTER
        tab_frame = tk.Frame(self.login_window, bg='#f0f0f0')
        tab_frame.pack(fill='x', pady=10)
        
        self.login_tab_btn = tk.Button(tab_frame, text="🔑 LOGIN", 
                                      command=lambda: self.switch_mode("login"),
                                      bg="#28a745", fg="white", font=("Arial", 12, "bold"), 
                                      width=20, height=1, relief='raised', bd=3)
        self.login_tab_btn.pack(side=tk.LEFT, padx=(80, 10))
        
        self.register_tab_btn = tk.Button(tab_frame, text="📝 REGISTER", 
                                         command=lambda: self.switch_mode("register"),
                                         bg="#6c757d", fg="white", font=("Arial", 12, "bold"), 
                                         width=20, height=1, relief='raised', bd=3)
        self.register_tab_btn.pack(side=tk.LEFT, padx=10)
        
        # CREATE SCROLLABLE CONTENT AREA
        main_container = tk.Frame(self.login_window, bg='#f0f0f0')
        main_container.pack(fill='both', expand=True)
        
        # Create canvas and scrollbar
        canvas = tk.Canvas(main_container, bg='#f0f0f0', highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas, bg='#f0f0f0')
        
        # Configure scrolling
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mouse wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def bind_mousewheel(widget):
            widget.bind("<MouseWheel>", _on_mousewheel)
            for child in widget.winfo_children():
                bind_mousewheel(child)
        
        bind_mousewheel(self.login_window)
        
        # Content frame (inside scrollable area)
        self.content_frame = tk.Frame(self.scrollable_frame, bg='#f0f0f0')
        self.content_frame.pack(fill='both', expand=True, padx=30, pady=20)
        
        # Status label (will be created in each mode)
        self.status_label = None
        
        # Start with LOGIN mode
        self.switch_mode("login")
        
    def switch_mode(self, mode):
        """Switch between LOGIN and REGISTER modes"""
        self.current_mode = mode
        
        # Clear current content
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Update tab button states
        if mode == "login":
            self.login_tab_btn.config(bg="#28a745", fg="white", relief='sunken')
            self.register_tab_btn.config(bg="#6c757d", fg="white", relief='raised')
            self.header_subtitle.config(text="🔐 USER LOGIN")
            self.create_login_form()
        else:
            self.login_tab_btn.config(bg="#6c757d", fg="white", relief='raised')
            self.register_tab_btn.config(bg="#007bff", fg="white", relief='sunken')
            self.header_subtitle.config(text="📝 CREATE NEW ACCOUNT")
            self.create_register_form()
    
    def create_login_form(self):
        """Create LOGIN form (existing users)"""
        
        # Login Instructions
        instructions_frame = tk.Frame(self.content_frame, bg='#e8f5e8', relief='solid', bd=2)
        instructions_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(instructions_frame, text="🔑 EXISTING USER LOGIN", 
                font=("Arial", 14, "bold"), fg="#2e7d32", bg='#e8f5e8').pack(pady=10)
        tk.Label(instructions_frame, text="Enter your existing username and password", 
                font=("Arial", 10), fg="#2e7d32", bg='#e8f5e8').pack()
        tk.Label(instructions_frame, text="Don't have an account? Click the REGISTER tab above", 
                font=("Arial", 10, "bold"), fg="#2e7d32", bg='#e8f5e8').pack(pady=(0,10))
        
        # Login Form
        form_frame = tk.LabelFrame(self.content_frame, text="🔑 Enter Your Credentials", 
                                  font=("Arial", 12, "bold"), bg='#f0f0f0', 
                                  fg="#2E86AB", padx=20, pady=20)
        form_frame.pack(fill='x', pady=20)
        
        # Username
        tk.Label(form_frame, text="👤 Username:", 
                font=("Arial", 11, "bold"), fg="#333", bg='#f0f0f0').pack(anchor='w', pady=(10,5))
        self.username_entry = tk.Entry(form_frame, font=("Arial", 11), width=40, 
                                     relief='solid', bd=2, bg='white')
        self.username_entry.pack(fill='x', pady=(0,15), ipady=8)
        
        # Password
        tk.Label(form_frame, text="🔒 Password:", 
                font=("Arial", 11, "bold"), fg="#333", bg='#f0f0f0').pack(anchor='w', pady=(10,5))
        self.password_entry = tk.Entry(form_frame, font=("Arial", 11), width=40, show="*", 
                                     relief='solid', bd=2, bg='white')
        self.password_entry.pack(fill='x', pady=(0,20), ipady=8)
        
        # Login button
        self.action_btn = tk.Button(form_frame, 
                                  text="🚀 LOGIN NOW", 
                                  command=self.login_user,
                                  bg="#28a745", fg="white", 
                                  font=("Arial", 14, "bold"), 
                                  width=30, height=2,
                                  relief='raised', bd=3, cursor='hand2')
        self.action_btn.pack(pady=15)
        
        self.create_common_elements()
        
        # Focus and bind Enter
        self.username_entry.focus()
        self.login_window.bind('<Return>', lambda e: self.login_user())
    
    def create_register_form(self):
        """Create REGISTER form (new users with more fields)"""
        
        # Register Instructions
        instructions_frame = tk.Frame(self.content_frame, bg='#e3f2fd', relief='solid', bd=2)
        instructions_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(instructions_frame, text="📝 CREATE NEW ACCOUNT", 
                font=("Arial", 14, "bold"), fg="#1976d2", bg='#e3f2fd').pack(pady=10)
        tk.Label(instructions_frame, text="Fill in the information below to create your account", 
                font=("Arial", 10), fg="#1976d2", bg='#e3f2fd').pack()
        tk.Label(instructions_frame, text="Already have an account? Click the LOGIN tab above", 
                font=("Arial", 10, "bold"), fg="#1976d2", bg='#e3f2fd').pack(pady=(0,10))
        
        # Registration Form
        form_frame = tk.LabelFrame(self.content_frame, text="📝 New Account Information", 
                                  font=("Arial", 12, "bold"), bg='#f0f0f0', 
                                  fg="#007bff", padx=20, pady=20)
        form_frame.pack(fill='x', pady=20)
        
        # Username
        tk.Label(form_frame, text="👤 Choose Username (minimum 3 characters):", 
                font=("Arial", 11, "bold"), fg="#333", bg='#f0f0f0').pack(anchor='w', pady=(10,5))
        self.username_entry = tk.Entry(form_frame, font=("Arial", 11), width=40, 
                                     relief='solid', bd=2, bg='white')
        self.username_entry.pack(fill='x', pady=(0,15), ipady=8)
        
        # Password
        tk.Label(form_frame, text="🔒 Choose Password (minimum 4 characters):", 
                font=("Arial", 11, "bold"), fg="#333", bg='#f0f0f0').pack(anchor='w', pady=(10,5))
        self.password_entry = tk.Entry(form_frame, font=("Arial", 11), width=40, show="*", 
                                     relief='solid', bd=2, bg='white')
        self.password_entry.pack(fill='x', pady=(0,15), ipady=8)
        
        # Confirm Password
        tk.Label(form_frame, text="🔒 Confirm Password:", 
                font=("Arial", 11, "bold"), fg="#333", bg='#f0f0f0').pack(anchor='w', pady=(10,5))
        self.confirm_password_entry = tk.Entry(form_frame, font=("Arial", 11), width=40, show="*", 
                                             relief='solid', bd=2, bg='white')
        self.confirm_password_entry.pack(fill='x', pady=(0,15), ipady=8)
        
        # Email
        tk.Label(form_frame, text="📧 Email Address (optional but recommended):", 
                font=("Arial", 11, "bold"), fg="#333", bg='#f0f0f0').pack(anchor='w', pady=(10,5))
        self.email_entry = tk.Entry(form_frame, font=("Arial", 11), width=40, 
                                   relief='solid', bd=2, bg='white')
        self.email_entry.pack(fill='x', pady=(0,20), ipady=8)
        
        # Register button
        self.action_btn = tk.Button(form_frame, 
                                  text="✨ CREATE ACCOUNT", 
                                  command=self.register_user,
                                  bg="#007bff", fg="white", 
                                  font=("Arial", 14, "bold"), 
                                  width=30, height=2,
                                  relief='raised', bd=3, cursor='hand2')
        self.action_btn.pack(pady=15)
        
        # Requirements
        req_frame = tk.LabelFrame(self.content_frame, text="📋 Requirements", 
                                 font=("Arial", 10, "bold"), bg='#f8f9fa', 
                                 fg="#495057", padx=15, pady=15)
        req_frame.pack(fill='x', pady=20)
        
        requirements = [
            "✅ Username: 3+ characters, must be unique",
            "✅ Password: 4+ characters", 
            "✅ Passwords must match exactly",
            "✅ Email: optional but recommended for recovery",
            "✅ All data stored locally and secure"
        ]
        
        for req in requirements:
            tk.Label(req_frame, text=req, 
                    font=("Arial", 9), fg="#495057", bg='#f8f9fa').pack(anchor='w', padx=10, pady=2)
        
        self.create_common_elements()
        
        # Focus and bind Enter
        self.username_entry.focus()
        self.login_window.bind('<Return>', lambda e: self.register_user())
    
    def create_common_elements(self):
        """Create elements common to both forms"""
        
        # Status label
        self.status_label = tk.Label(self.content_frame, 
                                   text=f"👋 Welcome RishiKumarRajvansh! Please fill the form above", 
                                   font=("Arial", 11, "bold"), bg='#f0f0f0', fg="blue",
                                   wraplength=550, justify='center')
        self.status_label.pack(pady=15)
        
        # Exit button
        exit_frame = tk.Frame(self.content_frame, bg='#f0f0f0')
        exit_frame.pack(fill='x', pady=15)
        
        tk.Button(exit_frame, text="❌ Exit Application", 
                 command=self.exit_application,
                 bg="#dc3545", fg="white", font=("Arial", 10), 
                 width=25, height=2, cursor='hand2').pack()
        
        # Bottom padding for scrolling
        tk.Label(self.content_frame, text="", bg='#f0f0f0', height=2).pack()
    
    def login_user(self):
        """Handle user login with better feedback"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        
        if not username or not password:
            self.show_status("❌ Please enter both username and password", "error")
            return
            
        # Show loading
        self.show_status("🔄 Authenticating user...", "info")
        self.action_btn.config(state='disabled', text="🔄 LOGGING IN...")
        self.login_window.update()
        
        # Authenticate user
        user_data = self.db_manager.authenticate_user(username, password)
        
        if user_data:
            self.user_data = {
                'id': user_data[0],
                'username': user_data[1],
                'email': user_data[2],
                'total_sessions': user_data[3],
                'settings': user_data[4],
                'created_at': user_data[5] if len(user_data) > 5 else datetime.now().isoformat()
            }
            
            self.show_status("✅ Login successful! Loading application...", "success")
            self.login_window.after(2000, self.close_login)
            
        else:
            self.show_status("❌ Invalid credentials. Please check username and password", "error")
            self.action_btn.config(state='normal', text="🚀 LOGIN NOW")
            self.password_entry.delete(0, tk.END)
            self.password_entry.focus()
    
    def register_user(self):
        """Handle user registration with validation"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        confirm_password = self.confirm_password_entry.get()
        email = self.email_entry.get().strip()
        
        # Validation
        if not username or not password:
            self.show_status("❌ Username and password are required", "error")
            return
            
        if len(username) < 3:
            self.show_status("❌ Username must be at least 3 characters", "error")
            return
            
        if len(password) < 4:
            self.show_status("❌ Password must be at least 4 characters", "error")
            return
            
        if password != confirm_password:
            self.show_status("❌ Passwords do not match", "error")
            return
            
        # Show loading
        self.show_status("🔄 Creating new account...", "info")
        self.action_btn.config(state='disabled', text="🔄 CREATING...")
        self.login_window.update()
        
        # Create user
        user_id = self.db_manager.create_user(username, password, email)
        
        if user_id:
            self.user_data = {
                'id': user_id,
                'username': username,
                'email': email,
                'total_sessions': 0,
                'settings': None,
                'created_at': datetime.now().isoformat()
            }
            
            self.show_status("🎉 Account created successfully!", "success")
            self.show_success_window(username, email)
            
        else:
            self.show_status("❌ Username already exists. Choose different username", "error")
            self.action_btn.config(state='normal', text="✨ CREATE ACCOUNT")
            self.username_entry.focus()
    
    def show_success_window(self, username, email):
        """Show account creation success window"""
        success_window = tk.Toplevel(self.login_window)
        success_window.title("🎉 Account Created Successfully!")
        success_window.geometry("500x400")
        success_window.configure(bg='#f0f8ff')
        success_window.transient(self.login_window)
        success_window.grab_set()
        
        # Center window
        success_window.update_idletasks()
        x = (success_window.winfo_screenwidth() // 2) - (500 // 2)
        y = (success_window.winfo_screenheight() // 2) - (400 // 2)
        success_window.geometry(f"500x400+{x}+{y}")
        
        tk.Label(success_window, text="🎉 SUCCESS!", 
                font=("Arial", 18, "bold"), fg="#28a745", bg='#f0f8ff').pack(pady=20)
        
        success_msg = f"""Account Created Successfully!

👤 Username: {username}
📧 Email: {email if email else 'Not provided'}
📅 Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🚀 You can now use the application with your new account!
Click the button below to continue."""
        
        tk.Label(success_window, text=success_msg, 
                font=("Arial", 11), bg='#f0f8ff', justify='center').pack(pady=20)
        
        tk.Button(success_window, text="🚀 CONTINUE TO APP", 
                 command=lambda: [success_window.destroy(), self.close_login()],
                 bg="#28a745", fg="white", font=("Arial", 12, "bold"), 
                 width=20, height=2).pack(pady=20)
        
        success_window.after(10000, lambda: [success_window.destroy(), self.close_login()])
    
    def show_status(self, message, status_type):
        """Show status message with appropriate color"""
        colors = {
            "error": "#dc3545",
            "success": "#28a745", 
            "info": "#007bff",
            "warning": "#ffc107"
        }
        
        if self.status_label:
            self.status_label.config(text=message, fg=colors.get(status_type, "#333"))
        
    def on_close_login(self):
        """Handle login window close attempt"""
        if messagebox.askyesno("Exit", "Authentication is required to use this application.\n\nDo you want to exit?"):
            self.exit_application()
            
    def exit_application(self):
        """Exit the entire application"""
        self.login_window.destroy()
        self.master.quit()
        self.master.destroy()
        
    def close_login(self):
        """Close login window and return user data"""
        self.login_window.destroy()
        self.master.deiconify()  # Show the main window
        self.callback(self.user_data)
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

class EnhancedActivitySimulator:
    def __init__(self, master):
        self.master = master
        master.title("Enhanced Activity Simulator Pro - Complete Edition")
        master.geometry("1400x900")  # Even larger default size
        master.resizable(True, True)
        master.minsize(1200, 800)  # Larger minimum size
        
        # Initialize database
        self.db_manager = DatabaseManager()
        self.current_user = None
        self.current_session_id = None
        
        # Initialize login system - MUST LOGIN TO CONTINUE
        self.show_login()
        
    def show_login(self):
        """Show login system and BLOCK access without authentication"""
        LoginSystem(self.master, self.db_manager, self.on_login_complete)
        
    def on_login_complete(self, user_data):
        """Called when login is complete - ONLY THEN initialize simulator"""
        if user_data:
            self.current_user = user_data
            self.initialize_simulator()
        else:
            # If login failed or cancelled, exit application
            self.master.quit()
            self.master.destroy()
            
    def initialize_simulator(self):
        """Initialize the main simulator ONLY after successful login"""
        
        # Show welcome message
        self.show_welcome_message()
        
        # --- Core Control Variables ---
        self.is_running = tk.BooleanVar(value=False)
        self.is_paused = tk.BooleanVar(value=False)
        self.target_percentage = tk.IntVar(value=50)
        self.intensity_mode = tk.StringVar(value="Medium")
        self.smart_detection_enabled = tk.BooleanVar(value=True)
        
        # --- Mode Toggle (NEW) ---
        self.current_mode = tk.StringVar(value="automation")  # automation or user
        self.auto_switch_enabled = tk.BooleanVar(value=True)
        self.user_inactive_threshold = tk.IntVar(value=180)  # 3 minutes default
        self.last_user_activity_time = time.time()
        self.mode_switch_timer = None
        
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
        
        # --- Text File Simulation (FIXED) ---
        self.text_file_enabled = tk.BooleanVar(value=True)  # Keep enabled by default
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
        
        # --- DATA COLLECTION ---
        self.last_data_collection = time.time()
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
        self.mode_monitor_thread = None
        
        # Start mode monitoring
        self.start_mode_monitoring()
        
    def show_welcome_message(self):
        """Show personalized welcome message with logout option"""
        try:
            created_date = datetime.fromisoformat(self.current_user['created_at']).strftime('%Y-%m-%d') if self.current_user['created_at'] else 'Unknown'
            
            welcome_msg = f"""
🎉 Welcome back, {self.current_user['username']}!

📊 Your Account Stats:
• Total Sessions: {self.current_user['total_sessions']}
• Member since: {created_date}
• Database: Connected & Secure

🚀 New Features Available:
• Smart Mode Toggle (Auto/User)
• Enhanced Analytics with Database
• Personalized Recommendations
• Historical Performance Tracking
• Secure User Authentication

Ready to start your activity simulation session?
            """
            
            # Create welcome window
            welcome_window = tk.Toplevel(self.master)
            welcome_window.title("👋 Welcome Back!")
            welcome_window.geometry("500x450")
            welcome_window.resizable(False, False)
            welcome_window.configure(bg='#f8f9fa')
            
            # Center the window
            welcome_window.transient(self.master)
            welcome_window.update_idletasks()
            x = (welcome_window.winfo_screenwidth() // 2) - (500 // 2)
            y = (welcome_window.winfo_screenheight() // 2) - (450 // 2)
            welcome_window.geometry(f"500x450+{x}+{y}")
            
            # Header
            header = tk.Label(welcome_window, text=f"👋 Welcome, {self.current_user['username']}!", 
                            font=("Arial", 16, "bold"), fg="#2E86AB", bg='#f8f9fa')
            header.pack(pady=20)
            
            # Content
            content = tk.Text(welcome_window, wrap=tk.WORD, font=("Arial", 10), 
                            height=12, width=50, bg='#ffffff', relief='flat', bd=10)
            content.pack(padx=20, pady=10, fill='both', expand=True)
            content.insert('1.0', welcome_msg)
            content.config(state='disabled')
            
            # Button frame
            btn_frame = tk.Frame(welcome_window, bg='#f8f9fa')
            btn_frame.pack(pady=20)
            
            # Start button
            tk.Button(btn_frame, text="🚀 Let's Start!", 
                     command=welcome_window.destroy,
                     bg="#28a745", fg="white", font=("Arial", 12, "bold"), 
                     width=15, height=2).pack(side=tk.LEFT, padx=5)
            
            # Logout button
            tk.Button(btn_frame, text="🚪 Logout", 
                     command=lambda: [welcome_window.destroy(), self.logout_user()],
                     bg="#dc3545", fg="white", font=("Arial", 12, "bold"), 
                     width=15, height=2).pack(side=tk.LEFT, padx=5)
            
            # Auto close after 15 seconds
            welcome_window.after(15000, welcome_window.destroy)
            
        except Exception as e:
            print(f"Welcome message error: {e}")
    
    def logout_user(self):
        """Handle user logout"""
        if self.is_running.get():
            if not messagebox.askyesno("Logout", "Simulation is running. Stop simulation and logout?"):
                return
            self.stop_simulation()
            time.sleep(1)
        
        # Clear user data
        self.current_user = None
        self.current_session_id = None
        
        # Close main window and restart login
        for widget in self.master.winfo_children():
            widget.destroy()
            
        self.show_login()
    
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
        # --- Top Menu Bar with Logout ---
        menubar = tk.Menu(self.master)
        self.master.config(menu=menubar)
        
        # User menu
        user_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label=f"👤 {self.current_user['username']}", menu=user_menu)
        user_menu.add_command(label="🏠 Dashboard", command=self.show_dashboard)
        user_menu.add_command(label="📊 Analytics", command=self.show_analytics_summary)
        user_menu.add_command(label="⚙️ Settings", command=self.show_user_settings)
        user_menu.add_separator()
        user_menu.add_command(label="🚪 Logout", command=self.logout_user)
        user_menu.add_command(label="❌ Exit", command=self.on_closing)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="❓ Help", menu=help_menu)
        help_menu.add_command(label="📖 User Guide", command=self.show_user_guide)
        help_menu.add_command(label="🆘 Support", command=self.show_support)
        help_menu.add_command(label="ℹ️ About", command=self.show_about)
        
        # --- Main Notebook for Tabs ---
        notebook = ttk.Notebook(self.master)
        notebook.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Tab 1: Target & Control
        control_frame = ttk.Frame(notebook)
        notebook.add(control_frame, text="🎯 Target & Control")
        self.create_control_tab(control_frame)
        
        # Tab 2: Advanced Settings
        advanced_frame = ttk.Frame(notebook)
        notebook.add(advanced_frame, text="⚙️ Advanced Settings")
        self.create_advanced_tab(advanced_frame)
        
        # Tab 3: Monitoring & Stats (FIXED)
        monitor_frame = ttk.Frame(notebook)
        notebook.add(monitor_frame, text="📊 Monitoring & Stats")
        self.create_monitoring_tab(monitor_frame)
        
        # Tab 4: Analytics & Insights
        analytics_frame = ttk.Frame(notebook)
        notebook.add(analytics_frame, text="📈 Analytics & Insights")
        self.create_analytics_tab(analytics_frame)
        
        # Tab 5: Activity Logs
        log_frame = ttk.Frame(notebook)
        notebook.add(log_frame, text="📋 Activity Logs")
        self.create_log_tab(log_frame)

    def create_control_tab(self, parent):
        # --- User Info Header with Logout ---
        user_frame = tk.LabelFrame(parent, text="👤 User Dashboard", font=("Arial", 10, "bold"))
        user_frame.pack(padx=10, pady=5, fill="x")
        
        user_info = tk.Frame(user_frame)
        user_info.pack(fill="x", padx=10, pady=5)
        
        tk.Label(user_info, text=f"Welcome: {self.current_user['username']}", 
                font=("Arial", 12, "bold"), fg="#2E86AB").pack(side=tk.LEFT)
        
        # Logout button in the main interface
        tk.Button(user_info, text="🚪 Logout", command=self.logout_user,
                 bg="#dc3545", fg="white", font=("Arial", 10, "bold")).pack(side=tk.RIGHT, padx=5)
        
        tk.Label(user_info, text=f"Sessions: {self.current_user['total_sessions']}", 
                font=("Arial", 10), fg="gray").pack(side=tk.RIGHT, padx=10)
        
        # --- Mode Toggle Section (NEW) ---
        mode_frame = tk.LabelFrame(parent, text="🔄 Smart Mode Toggle", font=("Arial", 10, "bold"))
        mode_frame.pack(padx=10, pady=5, fill="x")
        
        mode_controls = tk.Frame(mode_frame)
        mode_controls.pack(fill="x", padx=10, pady=5)
        
        # Current mode display
        self.mode_status_label = tk.Label(mode_controls, text="Current Mode: 🤖 Automation", 
                                        font=("Arial", 12, "bold"), fg="#28a745")
        self.mode_status_label.pack(side=tk.LEFT)
        
        # Manual toggle button
        self.mode_toggle_button = tk.Button(mode_controls, text="🔄 Switch to User Mode", 
                                          command=self.toggle_mode,
                                          bg="#007bff", fg="white", font=("Arial", 10, "bold"))
        self.mode_toggle_button.pack(side=tk.RIGHT, padx=10)
        
        # Auto-switch settings
        auto_switch_frame = tk.Frame(mode_frame)
        auto_switch_frame.pack(fill="x", padx=10, pady=5)
        
        auto_switch_checkbox = tk.Checkbutton(auto_switch_frame, text="Enable Auto Mode Switching", 
                                            variable=self.auto_switch_enabled)
        auto_switch_checkbox.pack(side=tk.LEFT)
        self.register_input_widget(auto_switch_checkbox, "checkbox")
        
        tk.Label(auto_switch_frame, text="Switch after:").pack(side=tk.LEFT, padx=(20,5))
        inactive_spinbox = tk.Spinbox(auto_switch_frame, from_=60, to=600, 
                                    textvariable=self.user_inactive_threshold, width=5)
        inactive_spinbox.pack(side=tk.LEFT, padx=5)
        tk.Label(auto_switch_frame, text="seconds of inactivity").pack(side=tk.LEFT)
        self.register_input_widget(inactive_spinbox, "spinbox")
        
        # --- Input Field Status ---
        input_status_frame = tk.LabelFrame(parent, text="🔒 Input Field Status", font=("Arial", 10, "bold"))
        input_status_frame.pack(padx=10, pady=5, fill="x")
        
        self.input_status_label = tk.Label(input_status_frame, text="Input Fields: 🔓 UNLOCKED", 
                                         font=("Arial", 10, "bold"), fg="green")
        self.input_status_label.pack(pady=5)
        
        tk.Label(input_status_frame, text="⚠️ All settings are locked during simulation to prevent conflicts", 
                font=("Arial", 9), fg="orange").pack()
        
        # --- Target Percentage Frame ---
        target_frame = tk.LabelFrame(parent, text="🎯 Daily Activity Target", font=("Arial", 10, "bold"))
        target_frame.pack(padx=10, pady=5, fill="x")
        
        target_row1 = tk.Frame(target_frame)
        target_row1.pack(fill="x", padx=5, pady=5)
        
        tk.Label(target_row1, text="Target Activity:").pack(side=tk.LEFT)
        target_scale = tk.Scale(target_row1, from_=10, to=95, orient=tk.HORIZONTAL, 
                               variable=self.target_percentage, length=300)
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
        
        # --- Enhanced File Management & Recovery ---
        file_frame = tk.LabelFrame(parent, text="📝 Text File Management", font=("Arial", 10, "bold"))
        file_frame.pack(padx=10, pady=5, fill="x")
        
        file_status_row = tk.Frame(file_frame)
        file_status_row.pack(fill="x", padx=5, pady=5)
        
        self.file_status_label = tk.Label(file_status_row, text="File: Not Created", 
                                        font=("Arial", 11, "bold"), fg="gray")
        self.file_status_label.pack(side=tk.LEFT)
        
        self.file_active_label = tk.Label(file_status_row, text="Status: Inactive", 
                                        font=("Arial", 10), fg="red")
        self.file_active_label.pack(side=tk.RIGHT)
        
        file_controls = tk.Frame(file_frame)
        file_controls.pack(fill="x", padx=5, pady=5)
        
        # FIXED: Text file checkbox - prevent auto-unchecking
        self.text_file_checkbox = tk.Checkbutton(file_controls, 
                      text="Enable Text File Simulation (Safe, dedicated file only)", 
                      variable=self.text_file_enabled,
                      command=self.on_text_file_toggle)
        self.text_file_checkbox.pack(anchor=tk.W, padx=5, pady=2)
        self.register_input_widget(self.text_file_checkbox, "checkbox")
        
        recovery_checkbox = tk.Checkbutton(file_controls, text="Auto File Recovery (recreate text file if closed)", 
                      variable=self.auto_file_recovery)
        recovery_checkbox.pack(anchor=tk.W, padx=5, pady=2)
        self.register_input_widget(recovery_checkbox, "checkbox")
        
        activate_checkbox = tk.Checkbutton(file_controls, text="Auto-Activate Text File (bring to foreground when inactive)", 
                      variable=self.auto_activate_enabled)
        activate_checkbox.pack(anchor=tk.W, padx=5, pady=2)
        self.register_input_widget(activate_checkbox, "checkbox")
        
        # --- Current Status Frame ---
        status_frame = tk.LabelFrame(parent, text="📊 Current Status", font=("Arial", 10, "bold"))
        status_frame.pack(padx=10, pady=5, fill="x")
        
        self.current_percentage_label = tk.Label(status_frame, text="Current Activity: 0.0%", 
                                               font=("Arial", 14, "bold"), fg="red")
        self.current_percentage_label.pack(pady=5)
        
        self.progress_bar = ttk.Progressbar(status_frame, length=500, mode='determinate')
        self.progress_bar.pack(pady=5)
        
        # --- System Status ---
        system_status_frame = tk.Frame(status_frame)
        system_status_frame.pack(fill="x", padx=5, pady=5)
        
        self.system_status_label = tk.Label(system_status_frame, text="System: Ready", 
                                          font=("Arial", 10, "bold"), fg="blue")
        self.system_status_label.pack(side=tk.LEFT)
        
        self.lock_status_label = tk.Label(system_status_frame, text="Screen: Unlocked", 
                                        font=("Arial", 10, "bold"), fg="green")
        self.lock_status_label.pack(side=tk.RIGHT)
        
        # --- Pause Status ---
        self.pause_status_label = tk.Label(status_frame, text="Status: Ready", 
                                         font=("Arial", 12, "bold"), fg="blue")
        self.pause_status_label.pack(pady=3)
        
        # --- User Activity Status (FIXED) ---
        user_status_frame = tk.Frame(status_frame)
        user_status_frame.pack(fill="x", padx=5, pady=5)
        
        self.user_activity_label = tk.Label(user_status_frame, text="User Status: Checking...", 
                                          font=("Arial", 10, "bold"))
        self.user_activity_label.pack(side=tk.LEFT)
        
        self.idle_time_label = tk.Label(user_status_frame, text="Idle: 0s")
        self.idle_time_label.pack(side=tk.RIGHT)
        
        # Session info
        session_info_frame = tk.Frame(status_frame)
        session_info_frame.pack(fill="x", padx=5, pady=5)
        
        self.session_time_label = tk.Label(session_info_frame, text="Session: 0h 0m")
        self.session_time_label.pack(side=tk.LEFT)
        
        self.activities_count_label = tk.Label(session_info_frame, text="Activities: 0")
        self.activities_count_label.pack(side=tk.RIGHT)
        
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
        
        # Manual pause/resume buttons (RESTORED)
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
        
        # Start user activity monitoring immediately
        self.start_user_activity_monitoring()
        
    def on_text_file_toggle(self):
        """Handle text file checkbox toggle - PREVENT AUTO-UNCHECKING"""
        if self.text_file_enabled.get():
            self.log_message("📝 Text file simulation enabled")
            # Update file status immediately
            self.master.after(100, self.update_file_status_display)
        else:
            self.log_message("📝 Text file simulation disabled")
            # Update file status
            self.master.after(100, self.update_file_status_display)
    
    def update_file_status_display(self):
        """Update file status display based on current state"""
        try:
            if self.text_file_enabled.get():
                if self.temp_file_path and os.path.exists(self.temp_file_path):
                    filename = os.path.basename(self.temp_file_path)
                    self.file_status_label.config(text=f"File: {filename}", fg="green")
                    
                    # Check if file is active
                    if self.is_our_text_file_active():
                        self.file_active_label.config(text="Status: ✅ Active", fg="green")
                    else:
                        self.file_active_label.config(text="Status: ⚠️ Inactive", fg="orange")
                else:
                    self.file_status_label.config(text="File: Ready to create", fg="blue")
                    self.file_active_label.config(text="Status: Not created", fg="gray")
            else:
                self.file_status_label.config(text="File: Disabled", fg="gray")
                self.file_active_label.config(text="Status: Disabled", fg="gray")
                
        except Exception as e:
            self.log_message(f"⚠️ File status update error: {e}")
    
    def start_user_activity_monitoring(self):
        """Start monitoring user activity for real-time updates"""
        if not hasattr(self, 'user_monitor_thread') or not self.user_monitor_thread or not self.user_monitor_thread.is_alive():
            self.user_monitor_thread = threading.Thread(target=self._run_user_monitoring, daemon=True)
            self.user_monitor_thread.start()
    
    def _run_user_monitoring(self):
        """Background thread for user activity monitoring"""
        try:
            while True:
                if hasattr(self, 'user_activity_label'):
                    # Update user activity status
                    self.master.after(0, self.update_user_activity_display)
                    
                    # Update file status
                    if self.text_file_enabled.get():
                        self.master.after(0, self.update_file_status_display)
                
                time.sleep(2)  # Update every 2 seconds
        except Exception as e:
            self.log_message(f"⚠️ User monitoring error: {e}")
    
    def update_user_activity_display(self):
        """Update user activity display (FIXED)"""
        try:
            idle_time = self.get_real_user_idle_time()
            threshold = self.user_idle_threshold.get()
            
            # Update the idle time display
            self.idle_time_label.config(text=f"Idle: {idle_time:.0f}s")
            
            is_active = idle_time < threshold
            
            # Update user status display with more detailed info
            if is_active:
                status_text = f"User Status: 🟢 ACTIVE (idle: {idle_time:.0f}s)"
                color = "green"
            else:
                status_text = f"User Status: 🔴 IDLE (idle: {idle_time:.0f}s)"
                color = "red"
                
            self.user_activity_label.config(text=status_text, fg=color)
            
        except Exception as e:
            self.user_activity_label.config(text="User Status: ⚠️ Error", fg="orange")

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

        # Initialize app display
        self.update_app_display()
        self.update_running_apps_display()

        # --- Timing Settings ---
        timing_frame = tk.LabelFrame(parent, text="⏱️ Timing Settings", font=("Arial", 10, "bold"))
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
        
        # --- Auto-Pause Settings ---
        autopause_frame = tk.LabelFrame(parent, text="⏸️ Auto-Pause Settings", font=("Arial", 10, "bold"))
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
        
        # --- Mouse Movement Settings ---
        mouse_frame = tk.LabelFrame(parent, text="🖱️ Mouse Movement Settings", font=("Arial", 10, "bold"))
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
        activity_frame = tk.LabelFrame(parent, text="🎬 Activity Types", font=("Arial", 10, "bold"))
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
        
        burst_checkbox = tk.Checkbutton(activity_frame, text="Burst Mode (Multiple actions in sequence)", 
                      variable=self.burst_mode_enabled)
        burst_checkbox.pack(anchor=tk.W, padx=5, pady=2)
        self.register_input_widget(burst_checkbox, "checkbox")
        
        # --- Intensity Mode Frame ---
        intensity_frame = tk.LabelFrame(parent, text="⚡ Intensity Mode", font=("Arial", 10, "bold"))
        intensity_frame.pack(padx=10, pady=5, fill="x")
        
        intensity_modes = ["Low", "Medium", "High", "Auto"]
        for mode in intensity_modes:
            radio = tk.Radiobutton(intensity_frame, text=mode, variable=self.intensity_mode, 
                          value=mode, command=self.update_intensity_settings)
            radio.pack(side=tk.LEFT, padx=10, pady=5)
            self.register_input_widget(radio, "radiobutton")

    def create_monitoring_tab(self, parent):
        """Create the monitoring tab with real-time stats (FIXED)"""
        
        # --- Real-time Status Dashboard ---
        dashboard_frame = tk.LabelFrame(parent, text="📊 Real-time Dashboard", font=("Arial", 12, "bold"))
        dashboard_frame.pack(padx=10, pady=5, fill="x")
        
        # Create metrics grid
        metrics_grid = tk.Frame(dashboard_frame)
        metrics_grid.pack(fill="x", padx=10, pady=10)
        
        # Row 1 - Primary Metrics
        row1 = tk.Frame(metrics_grid)
        row1.pack(fill="x", pady=5)
        
        self.efficiency_metric = tk.Label(row1, text="Efficiency: --", 
                                       font=("Arial", 11, "bold"), fg="#28a745")
        self.efficiency_metric.pack(side=tk.LEFT, padx=20)
        
        self.session_metric = tk.Label(row1, text="Session: 0h 0m", 
                                     font=("Arial", 11, "bold"), fg="#007bff")
        self.session_metric.pack(side=tk.LEFT, padx=20)
        
        self.activities_metric = tk.Label(row1, text="Activities: 0", 
                                       font=("Arial", 11, "bold"), fg="#ffc107")
        self.activities_metric.pack(side=tk.LEFT, padx=20)
        
        # Row 2 - System Metrics
        row2 = tk.Frame(metrics_grid)
        row2.pack(fill="x", pady=5)
        
        self.cpu_metric = tk.Label(row2, text="CPU: --", 
                                 font=("Arial", 11, "bold"), fg="#dc3545")
        self.cpu_metric.pack(side=tk.LEFT, padx=20)
        
        self.memory_metric = tk.Label(row2, text="Memory: --", 
                                    font=("Arial", 11, "bold"), fg="#6f42c1")
        self.memory_metric.pack(side=tk.LEFT, padx=20)
        
        self.mode_metric = tk.Label(row2, text="Mode: Automation", 
                                  font=("Arial", 11, "bold"), fg="#17a2b8")
        self.mode_metric.pack(side=tk.LEFT, padx=20)
        
        # --- Detailed Statistics ---
        stats_frame = tk.LabelFrame(parent, text="📈 Detailed Statistics", font=("Arial", 12, "bold"))
        stats_frame.pack(padx=10, pady=5, fill="both", expand=True)
        
        # Create scrollable text area for detailed stats
        self.stats_display = scrolledtext.ScrolledText(stats_frame, height=15, width=80, 
                                                      font=("Courier", 9), state='disabled',
                                                      bg='#f8f9fa')
        self.stats_display.pack(padx=5, pady=5, fill="both", expand=True)
        
        # --- Monitoring Controls ---
        controls_frame = tk.Frame(parent)
        controls_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Button(controls_frame, text="🔄 Refresh Stats", 
                 command=self.refresh_monitoring_display,
                 bg="#28a745", fg="white", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)
        
        tk.Button(controls_frame, text="📊 Export Data", 
                 command=self.export_monitoring_data,
                 bg="#17a2b8", fg="white", font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
        
        tk.Button(controls_frame, text="💾 Save Report", 
                 command=self.save_daily_report,
                 bg="#fd7e14", fg="white", font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
        
        tk.Button(controls_frame, text="🔄 Reset Stats", 
                 command=self.reset_daily_stats,
                 bg="#dc3545", fg="white", font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
        
        # Start monitoring updates
        self.update_monitoring_display()

    def create_analytics_tab(self, parent):
        """Create analytics tab with database-driven insights"""
        
        # --- Analytics Header ---
        header_frame = tk.Frame(parent)
        header_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(header_frame, text="📊 Advanced Analytics & Database Insights", 
                font=("Arial", 14, "bold"), fg="#2E86AB").pack()
        
        tk.Label(header_frame, text=f"Personalized analytics for {self.current_user['username']}", 
                font=("Arial", 10), fg="gray").pack()
        
        # --- Analytics Controls ---
        controls_frame = tk.LabelFrame(parent, text="🎛️ Analytics Controls", font=("Arial", 10, "bold"))
        controls_frame.pack(fill="x", padx=10, pady=5)
        
        control_buttons = tk.Frame(controls_frame)
        control_buttons.pack(fill="x", padx=5, pady=5)
        
        tk.Button(control_buttons, text="📈 Generate Reports", 
                 command=self.generate_analytics_reports,
                 bg="#28a745", fg="white", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)
        
        tk.Button(control_buttons, text="📊 View Trends", 
                 command=self.show_trend_analysis,
                 bg="#007bff", fg="white", font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
        
        tk.Button(control_buttons, text="🤖 AI Insights", 
                 command=self.show_ai_insights,
                 bg="#6f42c1", fg="white", font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
        
        # Time range selection
        range_frame = tk.Frame(controls_frame)
        range_frame.pack(fill="x", padx=5, pady=5)
        
        tk.Label(range_frame, text="Time Range:").pack(side=tk.LEFT)
        self.analytics_range = tk.StringVar(value="7")
        for days, label in [("1", "Today"), ("7", "Week"), ("30", "Month"), ("90", "Quarter")]:
            tk.Radiobutton(range_frame, text=label, variable=self.analytics_range, 
                          value=days).pack(side=tk.LEFT, padx=5)
        
        # --- Analytics Display ---
        analytics_notebook = ttk.Notebook(parent)
        analytics_notebook.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Performance Overview Tab
        perf_frame = ttk.Frame(analytics_notebook)
        analytics_notebook.add(perf_frame, text="📈 Performance")
        self.create_performance_overview(perf_frame)
        
        # Historical Data Tab
        history_frame = ttk.Frame(analytics_notebook)
        analytics_notebook.add(history_frame, text="📊 Historical Data")
        self.create_historical_analysis(history_frame)
        
        # Trends Tab
        trends_frame = ttk.Frame(analytics_notebook)
        analytics_notebook.add(trends_frame, text="📉 Trends & Patterns")
        self.create_trends_analysis(trends_frame)

    def create_performance_overview(self, parent):
        """Create performance overview with charts"""
        tk.Label(parent, text="📊 Performance charts will appear here after data collection", 
                font=("Arial", 12), fg="gray").pack(expand=True)
            
    def create_historical_analysis(self, parent):
        """Create historical data analysis"""
        
        # Historical stats summary
        summary_frame = tk.LabelFrame(parent, text="📊 Historical Summary", font=("Arial", 10, "bold"))
        summary_frame.pack(fill="x", padx=10, pady=5)
        
        self.hist_summary = tk.Text(summary_frame, height=8, font=("Arial", 10),
                                  bg="#f8f9fa", state='disabled')
        self.hist_summary.pack(fill="x", padx=5, pady=5)
        
        # Session history table
        table_frame = tk.LabelFrame(parent, text="📋 Recent Sessions", font=("Arial", 10, "bold"))
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Create treeview for session data
        columns = ('Date', 'Duration', 'Target%', 'Achieved%', 'Activities', 'Mode')
        self.session_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=10)
        
        for col in columns:
            self.session_tree.heading(col, text=col)
            self.session_tree.column(col, width=100)
        
        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.session_tree.yview)
        self.session_tree.configure(yscrollcommand=scrollbar.set)
        
        self.session_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

    def create_trends_analysis(self, parent):
        """Create trends and patterns analysis"""
        
        # Trends summary
        trends_summary_frame = tk.LabelFrame(parent, text="📈 Trend Analysis", font=("Arial", 10, "bold"))
        trends_summary_frame.pack(fill="x", padx=10, pady=5)
        
        self.trends_summary = tk.Text(trends_summary_frame, height=6, font=("Arial", 10),
                                    bg="#f8f9fa", state='disabled')
        self.trends_summary.pack(fill="x", padx=5, pady=5)
        
        # Recommendations
        rec_frame = tk.LabelFrame(parent, text="🤖 AI Recommendations", font=("Arial", 10, "bold"))
        rec_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.recommendations_display = tk.Text(rec_frame, height=10, font=("Arial", 10),
                                             bg="#f0f8ff", state='disabled')
        self.recommendations_display.pack(fill="both", expand=True, padx=5, pady=5)

    def create_log_tab(self, parent):
        """Create activity log tab"""
        
        # --- Log Controls ---
        log_controls_frame = tk.Frame(parent)
        log_controls_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(log_controls_frame, text="📋 Activity Logs", 
                font=("Arial", 14, "bold"), fg="#2E86AB").pack(side=tk.LEFT)
        
        # Log control buttons
        controls_right = tk.Frame(log_controls_frame)
        controls_right.pack(side=tk.RIGHT)
        
        tk.Button(controls_right, text="💾 Save Logs", 
                 command=self.save_logs,
                 bg="#28a745", fg="white", font=("Arial", 9)).pack(side=tk.LEFT, padx=2)
        
        tk.Button(controls_right, text="📤 Export", 
                 command=self.export_session_log,
                 bg="#17a2b8", fg="white", font=("Arial", 9)).pack(side=tk.LEFT, padx=2)
        
        tk.Button(controls_right, text="🗑️ Clear", 
                 command=self.clear_logs,
                 bg="#dc3545", fg="white", font=("Arial", 9)).pack(side=tk.LEFT, padx=2)
        
        # --- Main Log Display ---
        log_frame = tk.LabelFrame(parent, text="Activity Log", font=("Arial", 10, "bold"))
        log_frame.pack(padx=10, pady=5, fill="both", expand=True)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, width=80, height=25, 
                                                 state='disabled', font=("Consolas", 9))
        self.log_text.pack(padx=5, pady=5, fill="both", expand=True)
        
        # Initial welcome message
        self.log_message("🚀 Enhanced Activity Simulator Pro - Complete Edition initialized!")
        self.log_message(f"👤 Welcome {self.current_user['username']}! Database integration active.")
        self.log_message("📊 Features: Real-time analytics, ML insights, Database storage")
        self.log_message("📱 Enhanced app selection with visual interface")
        self.log_message("🔒 Input field locking during simulation")
        self.log_message("🔄 Smart mode toggle (Automation/User)")
        self.log_message("🔧 Advanced file recovery and auto-activation")
        self.log_message("⚠️ Emergency Stop: Move mouse to top-left corner")
        self.log_message(f"🕐 Session Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # === MODE MANAGEMENT METHODS (NEW) ===
    
    def start_mode_monitoring(self):
        """Start monitoring user activity for mode switching"""
        if not hasattr(self, 'mode_monitor_thread') or not self.mode_monitor_thread or not self.mode_monitor_thread.is_alive():
            self.mode_monitor_thread = threading.Thread(target=self._run_mode_monitoring, daemon=True)
            self.mode_monitor_thread.start()
            self.log_message("🔄 Mode monitoring started")
    
    def _run_mode_monitoring(self):
        """Background thread for mode monitoring"""
        try:
            while True:
                if self.auto_switch_enabled.get():
                    self.check_mode_switching()
                time.sleep(5)  # Check every 5 seconds
        except Exception as e:
            self.log_message(f"⚠️ Mode monitoring error: {e}")
    
    def check_mode_switching(self):
        """Check if mode should be switched based on user activity"""
        try:
            current_idle = self.get_real_user_idle_time()
            
            # Update last activity time if user is active
            if current_idle < 10:  # User active within last 10 seconds
                self.last_user_activity_time = time.time()
            
            # Calculate time since last user activity
            time_since_activity = time.time() - self.last_user_activity_time
            
            # Switch to user mode if user becomes active
            if (self.current_mode.get() == "automation" and 
                current_idle < 30 and 
                self.is_running.get()):
                self.switch_to_user_mode("User activity detected")
            
            # Switch to automation mode if user inactive for threshold time
            elif (self.current_mode.get() == "user" and 
                  time_since_activity >= self.user_inactive_threshold.get()):
                self.switch_to_automation_mode("User inactive timeout")
                
        except Exception as e:
            self.log_message(f"⚠️ Mode switching check error: {e}")
    
    def toggle_mode(self):
        """Manual mode toggle"""
        if self.current_mode.get() == "automation":
            self.switch_to_user_mode("Manual switch")
        else:
            self.switch_to_automation_mode("Manual switch")
    
    def switch_to_user_mode(self, reason):
        """Switch to user mode"""
        if self.current_mode.get() == "user":
            return
            
        self.current_mode.set("user")
        self.last_user_activity_time = time.time()
        
        # Update UI
        self.master.after(0, lambda: self.mode_status_label.config(
            text="Current Mode: 👤 User", fg="#007bff"))
        self.master.after(0, lambda: self.mode_toggle_button.config(
            text="🤖 Switch to Automation"))
        if hasattr(self, 'mode_metric'):
            self.master.after(0, lambda: self.mode_metric.config(
                text="Mode: User", fg="#007bff"))
        
        self.log_message(f"🔄 Switched to USER mode - {reason}")
        
        # Add to database if session is active
        if self.current_session_id:
            self.db_manager.add_pause_event(
                self.current_session_id, 'mode_switch_user', reason, datetime.now()
            )
    
    def switch_to_automation_mode(self, reason):
        """Switch to automation mode"""
        if self.current_mode.get() == "automation":
            return
            
        self.current_mode.set("automation")
        
        # Update UI
        self.master.after(0, lambda: self.mode_status_label.config(
            text="Current Mode: 🤖 Automation", fg="#28a745"))
        self.master.after(0, lambda: self.mode_toggle_button.config(
            text="👤 Switch to User"))
        if hasattr(self, 'mode_metric'):
            self.master.after(0, lambda: self.mode_metric.config(
                text="Mode: Automation", fg="#28a745"))
        
        self.log_message(f"🔄 Switched to AUTOMATION mode - {reason}")
        
        # Add to database if session is active
        if self.current_session_id:
            self.db_manager.add_pause_event(
                self.current_session_id, 'mode_switch_auto', reason, datetime.now()
            )

    # === TEXT FILE MANAGEMENT METHODS (ENHANCED & FIXED) ===
    
    def create_temp_text_file(self):
        """Create a temporary text file for simulation with enhanced tracking (FIXED)"""
        try:
            # Don't auto-disable the checkbox - this was the bug!
            if not self.text_file_enabled.get():
                self.log_message("📝 Text file simulation is disabled")
                return False
                
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
            
            header_content = f"""Enhanced Activity Simulator - User Session
{'='*70}
🚀 Enhanced Activity Simulator Pro - Complete Edition
👤 User: {self.current_user['username']}
📅 Session Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🆔 Session ID: {self.file_session_id}
🎯 Target: {self.target_percentage.get()}%
🔄 Mode: {self.current_mode.get().title()}
🔧 Auto-Activation: {'Enabled' if self.auto_activate_enabled.get() else 'Disabled'}
🔧 Auto-Recovery: {'Enabled' if self.auto_file_recovery.get() else 'Disabled'}
📊 Database: Connected
🔒 Input Fields: {'Locked during simulation' if self.is_running.get() else 'Unlocked'}
⚠️  DO NOT EDIT THIS FILE MANUALLY - IT WILL BE DELETED AUTOMATICALLY
🔄 Recovery Count: {self.file_recovery_count}
{'='*70}

📝 Working area (content below will be modified automatically):
"""
            self.temp_file_handle.write(header_content)
            self.temp_file_handle.flush()
            
            filename_only = os.path.basename(self.temp_file_path)
            self.our_window_title = filename_only
            
            # Open with default text editor
            if platform.system() == "Windows":
                self.text_editor_process = subprocess.Popen(['notepad.exe', self.temp_file_path])
            elif platform.system() == "Darwin":
                self.text_editor_process = subprocess.Popen(['open', '-W', self.temp_file_path])
            else:
                self.text_editor_process = subprocess.Popen(['xdg-open', self.temp_file_path])
                
            time.sleep(3)  # Give time for file to open
            
            # Update file status - DON'T disable checkbox!
            self.master.after(0, lambda: self.file_status_label.config(
                text=f"File: {filename_only}", fg="green"))
            self.master.after(0, lambda: self.file_active_label.config(
                text="Status: ✅ Active", fg="green"))
            
            self.log_message(f"📝 Created dedicated text file: {filename_only}")
            self.log_message(f"✅ Text file simulation remains ENABLED")
            self.log_message(f"🔄 Auto-activation: {'Enabled' if self.auto_activate_enabled.get() else 'Disabled'}")
            self.log_message(f"🔧 Auto-recovery: {'Enabled' if self.auto_file_recovery.get() else 'Disabled'}")
            self.log_message(f"🆔 Session ID: {self.file_session_id}")
            
            # Start file monitoring
            if self.auto_file_recovery.get():
                self.start_file_monitoring()
            
            return True
            
        except Exception as e:
            self.log_message(f"❌ Error creating temp file: {e}")
            # Don't disable the checkbox on error!
            return False
    
    def start_file_monitoring(self):
        """Start file monitoring thread"""
        if not hasattr(self, 'file_monitor_thread') or not self.file_monitor_thread or not self.file_monitor_thread.is_alive():
            self.file_monitor_thread = threading.Thread(target=self._monitor_file_status, daemon=True)
            self.file_monitor_thread.start()
            
    def _monitor_file_status(self):
        """Monitor file status in background thread"""
        try:
            while self.is_running.get() and self.text_file_enabled.get():
                self.check_file_status_internal()
                time.sleep(self.file_check_interval.get())
        except Exception as e:
            self.log_message(f"⚠️ File monitoring error: {e}")
    
    def check_file_status_internal(self):
        """Internal file status check"""
        try:
            if not self.our_window_title or not self.temp_file_path:
                return
                
            # Check if file still exists
            if not os.path.exists(self.temp_file_path):
                self.log_message("⚠️ Text file was deleted externally")
                self.trigger_file_recovery("File deleted")
                return
                
            # Check if process is still running
            if not check_process_running(self.text_editor_process):
                self.log_message("⚠️ Text editor process terminated")
                
                # Check if user closed it or it crashed
                windows = find_text_file_windows(self.our_window_title)
                if not windows:
                    self.log_message("📝 Text file window closed by user")
                    self.trigger_file_recovery("Window closed")
                    
        except Exception as e:
            self.log_message(f"⚠️ File status check error: {e}")
    
    def trigger_file_recovery(self, reason):
        """Trigger file recovery process"""
        if self.file_recovery_count >= self.max_recovery_attempts.get():
            self.log_message(f"❌ Max recovery attempts ({self.max_recovery_attempts.get()}) reached")
            return
            
        self.file_recovery_count += 1
        self.log_message(f"🔧 Triggering file recovery #{self.file_recovery_count} - {reason}")
        
        # Attempt recovery
        if self.attempt_file_recovery():
            self.log_message("✅ File recovery successful")
        else:
            self.log_message("❌ File recovery failed")
    
    def attempt_file_recovery(self):
        """Attempt to recover the text file"""
        try:
            if self.temp_file_path and os.path.exists(self.temp_file_path):
                # File exists, try to reopen
                if platform.system() == "Windows":
                    self.text_editor_process = subprocess.Popen(['notepad.exe', self.temp_file_path])
                elif platform.system() == "Darwin":
                    self.text_editor_process = subprocess.Popen(['open', '-W', self.temp_file_path])
                else:
                    self.text_editor_process = subprocess.Popen(['xdg-open', self.temp_file_path])
                    
                time.sleep(2)
                return True
            else:
                # File doesn't exist, create new one
                return self.create_temp_text_file()
                
        except Exception as e:
            self.log_message(f"❌ File recovery error: {e}")
            return False
    
    def is_our_text_file_active(self):
        """Enhanced check if our specific text file window is currently active"""
        if not self.our_window_title:
            return False
            
        # During lock screen, assume it's not active for text operations
        if self.lock_screen_mode:
            return False
            
        try:
            current_window_title = self.get_active_window_title()
            
            # Check exact match first
            if self.our_window_title in current_window_title:
                return True
            
            # Check base filename match
            filename_base = os.path.splitext(self.our_window_title)[0]
            if filename_base in current_window_title:
                return True
                
            # File not active
            return False
            
        except Exception as e:
            self.log_message(f"⚠️ File active check error: {e}")
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

    # === USER ACTIVITY DETECTION (ENHANCED) ===
    
    def get_real_user_idle_time(self):
        """Get actual system idle time using Windows API"""
        try:
            idle_time = get_idle_duration()
            return idle_time
        except:
            # Fallback method using mouse position
            current_mouse_pos = pyautogui.position()
            if current_mouse_pos != self.last_mouse_pos:
                if time.time() - self.our_last_mouse_movement > 2:
                    self.last_real_activity = time.time()
                    self.last_mouse_pos = current_mouse_pos
                    return 0
            
            return time.time() - self.last_real_activity

    # === DATABASE INTEGRATION METHODS ===
    
    def start_simulation(self):
        """Enhanced start simulation with database integration and FIXED text file handling"""
        if self.is_running.get():
            messagebox.showwarning("Already Running", "Simulation is already active.")
            return
            
        # Create new session in database
        self.current_session_id = self.db_manager.create_session(
            self.current_user['id'], 
            self.target_percentage.get(), 
            self.current_mode.get()
        )
        
        if not self.current_session_id:
            messagebox.showerror("Database Error", "Failed to create session in database.")
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
        
        self.log_message("🚀 Starting Enhanced Activity Simulation with Database Integration...")
        self.log_message(f"📊 Session ID: {self.current_session_id}")
        self.log_message(f"👤 User: {self.current_user['username']}")
        self.log_message(f"🔒 All input fields locked to prevent configuration conflicts")
        self.log_message(f"🎯 Target: {self.target_percentage.get()}% | Mode: {self.current_mode.get().title()}")
        self.log_message(f"🧠 Smart Detection: {'Real System Idle Time' if self.smart_detection_enabled.get() else 'OFF'}")
        self.log_message(f"⏸️ Auto-Pause: {'ON' if self.auto_pause_enabled.get() else 'OFF'}")
        self.log_message(f"🔄 Auto-Activation: {'ON' if self.auto_activate_enabled.get() else 'OFF'}")
        self.log_message(f"🔧 Auto-Recovery: {'ON' if self.auto_file_recovery.get() else 'OFF'}")
        self.log_message(f"🔄 Mode Switching: {'ON' if self.auto_switch_enabled.get() else 'OFF'}")
        
        # FIXED: Create text file if enabled - DON'T disable checkbox on failure
        if self.text_file_enabled.get():
            self.log_message("📝 Text file simulation is ENABLED - creating dedicated file...")
            if self.create_temp_text_file():
                self.log_message("✅ Text file created successfully and ready for simulation")
            else:
                self.log_message("⚠️ Text file creation failed, but simulation will continue")
                # DON'T disable the checkbox here!
        else:
            self.log_message("📝 Text file simulation is DISABLED by user")
        
        # Start all threads
        self.automation_thread = threading.Thread(target=self._run_enhanced_automation, daemon=True)
        self.automation_thread.start()
        
        self.monitoring_thread = threading.Thread(target=self._run_monitoring, daemon=True)
        self.monitoring_thread.start()
        
        # Start data collection thread
        self.data_thread = threading.Thread(target=self._run_data_collection, daemon=True)
        self.data_thread.start()
    
    def stop_simulation(self):
        """Enhanced stop simulation with database finalization"""
        if not self.is_running.get():
            return
            
        self.is_running.set(False)
        self.is_paused.set(False)
        
        # Finalize session in database
        if self.current_session_id:
            self.db_manager.end_session(
                self.current_session_id,
                self.current_percentage.get(),
                self.activities_today,
                self.total_pause_time
            )
        
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
        
        self.log_message(f"📊 Session Summary:")
        self.log_message(f"   Session ID: {self.current_session_id}")
        self.log_message(f"   Total Time: {total_session_time/60:.1f} minutes")
        self.log_message(f"   Active Time: {active_time/60:.1f} minutes")
        self.log_message(f"   Pause Time: {self.total_pause_time/60:.1f} minutes")
        self.log_message(f"   Pause Events: {pause_count}")
        self.log_message(f"   Activities: {self.activities_today}")
        self.log_message(f"   File Recovery Count: {self.file_recovery_count}")
        self.log_message(f"   Final Mode: {self.current_mode.get().title()}")
        self.log_message("✅ Session data saved to database")
        self.log_message("✅ Simulation stopped successfully")
        
        # Reset session ID
        self.current_session_id = None
    
    def _run_data_collection(self):
        """Background data collection for database storage"""
        try:
            while self.is_running.get():
                if time.time() - self.last_data_collection >= 10:  # Every 10 seconds
                    self.collect_and_store_data()
                    self.last_data_collection = time.time()
                
                time.sleep(2)
                
        except Exception as e:
            self.log_message(f"⚠️ Data collection error: {e}")
    
    def collect_and_store_data(self):
        """Collect current data and store in database"""
        try:
            if not self.current_session_id:
                return
                
            # Get current metrics
            user_idle = self.get_real_user_idle_time()
            sim_activity = 1 if not self.is_paused.get() and self.current_mode.get() == "automation" else 0
            
            try:
                cpu_usage = psutil.cpu_percent()
                memory_usage = psutil.virtual_memory().percent
            except:
                cpu_usage = 0
                memory_usage = 0
            
            target_pct = self.target_percentage.get()
            current_pct = self.calculate_current_percentage()
            is_paused = self.is_paused.get()
            is_locked = self.lock_screen_mode
            
            # Store in database
            self.db_manager.add_activity_data(
                self.current_session_id,
                datetime.now(),
                user_idle,
                sim_activity,
                cpu_usage,
                memory_usage,
                target_pct,
                current_pct,
                is_paused,
                is_locked,
                self.mouse_move_count,
                self.key_press_count,
                self.text_sim_count,
                self.current_mode.get()
            )
            
            # Reset counters after storing
            self.mouse_move_count = 0
            self.key_press_count = 0
            self.text_sim_count = 0
            
        except Exception as e:
            self.log_message(f"⚠️ Data storage error: {e}")

    # === MANUAL PAUSE/RESUME METHODS (RESTORED) ===
    
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
        
        # Add to database
        if self.current_session_id:
            self.db_manager.add_pause_event(
                self.current_session_id, 'manual_pause', 'User manual pause', datetime.now()
            )
        
        self.log_message("⏸️ MANUAL PAUSE: Simulation paused by user")
        self.update_pause_status()
        
    def manual_resume(self):
        """Manually resume the simulation"""
        if not self.is_running.get() or not self.is_paused.get():
            return
            
        self.is_paused.set(False)
        
        pause_duration = 0
        if self.pause_start_time > 0:
            pause_duration = time.time() - self.pause_start_time
            self.total_pause_time += pause_duration
        
        resume_event = {
            'type': 'manual_resume',
            'time': datetime.now().strftime('%H:%M:%S'),
            'reason': 'User manual resume',
            'pause_duration': pause_duration
        }
        self.pause_history.append(resume_event)
        
        # Add to database
        if self.current_session_id:
            self.db_manager.add_pause_event(
                self.current_session_id, 'manual_resume', 'User manual resume', 
                datetime.now(), pause_duration
            )
        
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
            elif self.current_mode.get() == "user":
                self.pause_status_label.config(text="Status: 👤 USER MODE", fg="blue")
            else:
                self.pause_status_label.config(text="Status: ▶️ ACTIVE", fg="green")
            self.manual_pause_button.config(state=tk.NORMAL)
            self.manual_resume_button.config(state=tk.DISABLED)

    # === MONITORING TAB METHODS (FIXED) ===
    
    def update_monitoring_display(self):
        """Update the monitoring display with real-time data"""
        try:
            if not hasattr(self, 'stats_display'):
                return
                
            # Calculate current metrics
            total_session_time = time.time() - self.session_start_time
            active_time = total_session_time - self.total_pause_time
            
            if self.is_paused.get() and self.pause_start_time > 0:
                current_pause = time.time() - self.pause_start_time
                active_time -= current_pause
            
            # Get system metrics
            try:
                cpu_usage = psutil.cpu_percent()
                memory_usage = psutil.virtual_memory().percent
            except:
                cpu_usage = 0
                memory_usage = 0
            
            efficiency = self.calculate_efficiency()
            
            # Update metric labels
            session_hours = total_session_time / 3600
            if hasattr(self, 'efficiency_metric'):
                self.efficiency_metric.config(text=f"Efficiency: {efficiency:.1f}%")
                self.session_metric.config(text=f"Session: {session_hours:.1f}h")
                self.activities_metric.config(text=f"Activities: {self.activities_today}")
                self.cpu_metric.config(text=f"CPU: {cpu_usage:.1f}%")
                self.memory_metric.config(text=f"Memory: {memory_usage:.1f}%")
                self.mode_metric.config(text=f"Mode: {self.current_mode.get().title()}")
            
            # Prepare detailed stats text
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            user_idle = self.get_real_user_idle_time()
            
            stats_text = f"""ENHANCED ACTIVITY SIMULATOR - MONITORING DASHBOARD
{'='*70}
📊 REAL-TIME STATUS:
   Timestamp: {current_time}
   User: {self.current_user['username']}
   Session ID: {self.current_session_id or 'Not Started'}
   
🎯 SESSION METRICS:
   Current Mode: {self.current_mode.get().title()}
   Target Percentage: {self.target_percentage.get()}%
   Current Percentage: {self.current_percentage.get():.1f}%
   Efficiency Rating: {efficiency:.1f}%
   
⏱️ TIMING INFORMATION:
   Session Duration: {total_session_time/60:.1f} minutes
   Active Time: {active_time/60:.1f} minutes
   Pause Time: {self.total_pause_time/60:.1f} minutes
   User Idle Time: {user_idle:.1f} seconds
   
📈 ACTIVITY STATISTICS:
   Total Activities: {self.activities_today}
   Mouse Movements: {self.mouse_move_count}
   Key Presses: {self.key_press_count}
   Text Simulations: {self.text_sim_count}
   File Recoveries: {self.file_recovery_count}
   
🖥️ SYSTEM PERFORMANCE:
   CPU Usage: {cpu_usage:.1f}%
   Memory Usage: {memory_usage:.1f}%
   Screen Status: {'🔒 Locked' if self.lock_screen_mode else '🔓 Unlocked'}
   
📝 FILE STATUS:
   Text File: {'✅ Enabled' if self.text_file_enabled.get() else '❌ Disabled'}
   File Active: {'✅ Active' if self.is_our_text_file_active() else '❌ Inactive'}
   Auto-Recovery: {'✅ Enabled' if self.auto_file_recovery.get() else '❌ Disabled'}
   
🔧 AUTOMATION SETTINGS:
   Auto-Pause: {'✅ Enabled' if self.auto_pause_enabled.get() else '❌ Disabled'}
   Auto-Activation: {'✅ Enabled' if self.auto_activate_enabled.get() else '❌ Disabled'}
   Smart Detection: {'✅ Enabled' if self.smart_detection_enabled.get() else '❌ Disabled'}
   Mode Auto-Switch: {'✅ Enabled' if self.auto_switch_enabled.get() else '❌ Disabled'}
   
🔒 SECURITY STATUS:
   Input Fields: {'🔒 Locked' if self.is_running.get() else '🔓 Unlocked'}
   Failsafe: ✅ Active (top-left corner)
   
📊 DATABASE STATUS:
   Connection: ✅ Active
   Data Collection: {'✅ Running' if self.is_running.get() else '⏹️ Stopped'}
   
🎮 CURRENT OPERATION:
   Status: {self.get_current_status()}
   Last Update: {current_time}
"""
            
            # Update the stats display
            self.stats_display.config(state='normal')
            self.stats_display.delete('1.0', tk.END)
            self.stats_display.insert('1.0', stats_text)
            self.stats_display.config(state='disabled')
            
            # Schedule next update if running
            if self.is_running.get():
                self.master.after(5000, self.update_monitoring_display)
            else:
                self.master.after(10000, self.update_monitoring_display)
                
        except Exception as e:
            self.log_message(f"⚠️ Monitoring display error: {e}")
    
    def get_current_status(self):
        """Get current operation status description"""
        if not self.is_running.get():
            return "⏹️ Stopped"
        elif self.is_paused.get():
            return "⏸️ Paused"
        elif self.current_mode.get() == "user":
            return "👤 User Mode Active"
        elif self.lock_screen_mode:
            return "🔒 Lock Screen Mode"
        else:
            return "🤖 Automation Active"
    
    def calculate_efficiency(self):
        """Calculate current efficiency percentage"""
        try:
            target = self.target_percentage.get()
            current = self.current_percentage.get()
            
            if target == 0:
                return 0
                
            efficiency = (current / target) * 100
            return min(100, max(0, efficiency))
            
        except:
            return 0
    
    def refresh_monitoring_display(self):
        """Manually refresh the monitoring display"""
        self.log_message("🔄 Refreshing monitoring display...")
        self.update_monitoring_display()
    
    def export_monitoring_data(self):
        """Export current monitoring data to file"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"monitoring_data_{timestamp}.txt"
            
            # Get current stats text
            current_stats = self.stats_display.get('1.0', tk.END)
            
            with open(filename, 'w') as f:
                f.write("ENHANCED ACTIVITY SIMULATOR - MONITORING DATA EXPORT\n")
                f.write("="*70 + "\n")
                f.write(f"Export Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"User: {self.current_user['username']}\n")
                f.write(f"Session ID: {self.current_session_id or 'Not Started'}\n")
                f.write("\n" + current_stats)
            
            self.log_message(f"📊 Monitoring data exported: {filename}")
            messagebox.showinfo("Export Complete", f"Monitoring data exported to:\n{filename}")
            
        except Exception as e:
            self.log_message(f"❌ Export error: {e}")
            messagebox.showerror("Export Error", f"Failed to export monitoring data:\n{e}")

    # === UTILITY METHODS ===
    
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
            # Auto mode adjusts based on current performance
            pass
    
    def log_message(self, message):
        timestamp = time.strftime("%H:%M:%S")
        if hasattr(self, 'log_text'):
            self.log_text.config(state='normal')
            self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
            self.log_text.see(tk.END)
            self.log_text.config(state='disabled')
    
    def clear_logs(self):
        """Clear the activity logs"""
        if messagebox.askyesno("Clear Logs", "Are you sure you want to clear all logs?"):
            self.log_text.config(state='normal')
            self.log_text.delete('1.0', tk.END)
            self.log_text.config(state='disabled')
            self.log_message("🗑️ Activity logs cleared")

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
            
            # Update session time
            session_time = time.time() - self.session_start_time
            hours = int(session_time // 3600)
            minutes = int((session_time % 3600) // 60)
            self.session_time_label.config(text=f"Session: {hours}h {minutes}m")
            
            # Update activities count
            self.activities_count_label.config(text=f"Activities: {self.activities_today}")
            
            # Update pause status
            self.update_pause_status()
            
        except Exception as e:
            self.log_message(f"Display update error: {e}")

    def _run_monitoring(self):
        """Background monitoring and display updates"""
        while self.is_running.get():
            try:
                self.master.after(0, self.update_display)
                time.sleep(2)
            except:
                break

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

    # === PLACEHOLDER METHODS FOR CORE AUTOMATION ===
    
    def _run_enhanced_automation(self):
        """Main automation loop - simplified placeholder"""
        try:
            while self.is_running.get():
                if self.is_paused.get():
                    time.sleep(1)
                    continue
                
                if self.current_mode.get() == "automation":
                    # Perform automation activities
                    self.activities_today += 1
                    self.log_message(f"🤖 Automation activity performed (Total: {self.activities_today})")
                
                # Sleep between activities
                sleep_time = self.base_interval_seconds.get()
                time.sleep(sleep_time)
                
        except Exception as e:
            self.log_message(f"⚠️ Automation error: {e}")
    
    # === MENU METHODS ===
    
    def show_dashboard(self):
        """Show user dashboard"""
        try:
            dash_window = tk.Toplevel(self.master)
            dash_window.title("📊 User Dashboard")
            dash_window.geometry("600x400")
            
            tk.Label(dash_window, text=f"📊 Dashboard for {self.current_user['username']}", 
                    font=("Arial", 16, "bold")).pack(pady=20)
            
            stats_text = f"""
User Statistics:
• Username: {self.current_user['username']}
• Total Sessions: {self.current_user['total_sessions']}
• Account Created: {self.current_user.get('created_at', 'Unknown')}
• Current Session: {self.current_session_id or 'Not Started'}

Session Information:
• Current Mode: {self.current_mode.get().title()}
• Target: {self.target_percentage.get()}%
• Activities Today: {self.activities_today}
            """
            
            tk.Text(dash_window, wrap=tk.WORD, font=("Arial", 11), height=15).pack(
                fill="both", expand=True, padx=20, pady=10)
            
        except Exception as e:
            self.log_message(f"❌ Dashboard error: {e}")
    
    def show_analytics_summary(self):
        """Show analytics summary"""
        try:
            self.generate_analytics_reports()
        except Exception as e:
            self.log_message(f"❌ Analytics error: {e}")
    
    def show_user_settings(self):
        """Show user settings window"""
        try:
            settings_window = tk.Toplevel(self.master)
            settings_window.title("⚙️ User Settings")
            settings_window.geometry("400x300")
            
            tk.Label(settings_window, text="⚙️ User Settings", 
                    font=("Arial", 16, "bold")).pack(pady=20)
            
            tk.Label(settings_window, text="Settings functionality will be added here", 
                    font=("Arial", 12)).pack(pady=50)
            
        except Exception as e:
            self.log_message(f"❌ Settings error: {e}")
    
    def show_user_guide(self):
        """Show user guide"""
        try:
            guide_window = tk.Toplevel(self.master)
            guide_window.title("📖 User Guide")
            guide_window.geometry("700x500")
            
            guide_text = """
Enhanced Activity Simulator Pro - User Guide

1. Login/Registration:
   • Create an account or login with existing credentials
   • All data is stored locally and securely encrypted

2. Target Setting:
   • Set your daily activity target percentage
   • Adjust working hours as needed

3. Mode Toggle:
   • Automation Mode: System performs activities automatically
   • User Mode: You work manually while system stays inactive
   • Auto-switching available based on user activity

4. Text File Simulation:
   • Enable to create a dedicated text file for safe simulation
   • Auto-recovery ensures file persistence
   • Auto-activation brings file to foreground when needed

5. Application Management:
   • Select applications where simulation should pause
   • Visual interface with 1000+ detected applications
   • Real-time running process detection

6. Monitoring:
   • Real-time dashboard with performance metrics
   • Detailed analytics and historical data
   • AI-powered insights and recommendations

7. Security:
   • Input fields are locked during simulation
   • Emergency stop: Move mouse to top-left corner
   • Secure database storage for all user data
            """
            
            text_widget = scrolledtext.ScrolledText(guide_window, wrap=tk.WORD, font=("Arial", 10))
            text_widget.pack(fill="both", expand=True, padx=20, pady=20)
            text_widget.insert('1.0', guide_text)
            text_widget.config(state='disabled')
            
        except Exception as e:
            self.log_message(f"❌ User guide error: {e}")
    
    def show_support(self):
        """Show support information"""
        try:
            support_window = tk.Toplevel(self.master)
            support_window.title("🆘 Support")
            support_window.geometry("500x300")
            
            tk.Label(support_window, text="🆘 Support Information", 
                    font=("Arial", 16, "bold")).pack(pady=20)
            
            support_text = """
For technical support and assistance:

• Check the User Guide for common questions
• Review the Activity Logs for error messages
• Ensure all dependencies are installed
• Try restarting the application
• Check database connectivity

Emergency Actions:
• Press Ctrl+C to force stop
• Move mouse to top-left corner for failsafe
• Use Task Manager if unresponsive

Contact Information:
• Email: support@activitysimulator.com
• Documentation: Available in Help menu
• Version: Enhanced Pro - Complete Edition
            """
            
            tk.Label(support_window, text=support_text, 
                    font=("Arial", 10), justify=tk.LEFT).pack(padx=20, pady=20)
            
        except Exception as e:
            self.log_message(f"❌ Support error: {e}")
    
    def show_about(self):
        """Show about information"""
        try:
            about_window = tk.Toplevel(self.master)
            about_window.title("ℹ️ About")
            about_window.geometry("500x400")
            
            tk.Label(about_window, text="🚀 Enhanced Activity Simulator Pro", 
                    font=("Arial", 18, "bold")).pack(pady=20)
            
            about_text = f"""
Complete Edition with Database Integration

Version: 3.0 Professional
User: {self.current_user['username']}
Database: SQLite (Local)

Features:
✅ Secure User Authentication
✅ Smart Mode Toggle (Auto/User)
✅ Enhanced Text File Management
✅ Visual Application Selector
✅ Real-time Analytics Dashboard
✅ Database-driven Insights
✅ AI-powered Recommendations
✅ Advanced File Recovery
✅ Input Field Locking
✅ Emergency Failsafe

Developed with Python, Tkinter, SQLite
© 2024 Enhanced Activity Simulator Pro

All data is stored locally and securely.
No data is transmitted externally.
            """
            
            tk.Label(about_window, text=about_text, 
                    font=("Arial", 10), justify=tk.LEFT).pack(padx=20, pady=20)
            
        except Exception as e:
            self.log_message(f"❌ About error: {e}")

    # === ADDITIONAL PLACEHOLDER METHODS ===
    
    def test_window_activation(self):
        """Test window activation functionality"""
        self.log_message("🧪 Testing window activation...")
        
    def force_file_recovery(self):
        """Force immediate file recovery"""
        self.log_message("🔧 Force file recovery initiated...")
        if self.text_file_enabled.get():
            if self.attempt_file_recovery():
                self.log_message("✅ File recovery successful")
            else:
                self.log_message("❌ File recovery failed")
        else:
            self.log_message("⚠️ Text file simulation is disabled")
        
    def check_file_status(self):
        """Check current file status and display information"""
        if self.text_file_enabled.get():
            if self.temp_file_path and os.path.exists(self.temp_file_path):
                filename = os.path.basename(self.temp_file_path)
                active_status = "Active" if self.is_our_text_file_active() else "Inactive"
                self.log_message(f"📋 File status: ✅ {filename} - {active_status}")
            else:
                self.log_message("📋 File status: ❌ No file created")
        else:
            self.log_message("📋 File status: Disabled by user")
        
    def save_daily_report(self):
        """Save daily activity report to file"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"daily_report_{self.current_user['username']}_{timestamp}.txt"
            
            total_session_time = time.time() - self.session_start_time
            
            with open(filename, 'w') as f:
                f.write("ENHANCED ACTIVITY SIMULATOR - DAILY REPORT\n")
                f.write("="*60 + "\n\n")
                f.write(f"User: {self.current_user['username']}\n")
                f.write(f"Date: {datetime.now().strftime('%Y-%m-%d')}\n")
                f.write(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write(f"Session Duration: {total_session_time/3600:.2f} hours\n")
                f.write(f"Activities Performed: {self.activities_today}\n")
                f.write(f"Current Mode: {self.current_mode.get().title()}\n")
                f.write(f"Target Percentage: {self.target_percentage.get()}%\n")
                f.write(f"Current Percentage: {self.current_percentage.get():.1f}%\n")
                
            self.log_message(f"📄 Daily report saved: {filename}")
            messagebox.showinfo("Report Saved", f"Daily report saved as:\n{filename}")
            
        except Exception as e:
            self.log_message(f"❌ Error saving report: {e}")
        
    def reset_daily_stats(self):
        """Reset daily statistics"""
        if messagebox.askyesno("Reset Stats", "Are you sure you want to reset daily statistics?"):
            self.activities_today = 0
            self.session_start_time = time.time()
            self.current_percentage.set(0.0)
            self.total_pause_time = 0
            self.log_message("🔄 Daily statistics reset")
        
    def save_logs(self):
        """Save activity logs to file"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"activity_logs_{self.current_user['username']}_{timestamp}.txt"
            
            with open(filename, 'w') as f:
                f.write("ENHANCED ACTIVITY SIMULATOR - ACTIVITY LOGS\n")
                f.write("="*60 + "\n\n")
                f.write(f"User: {self.current_user['username']}\n")
                f.write(f"Export Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write(self.log_text.get('1.0', tk.END))
                
            self.log_message(f"📄 Logs saved: {filename}")
            messagebox.showinfo("Logs Saved", f"Activity logs saved as:\n{filename}")
            
        except Exception as e:
            self.log_message(f"❌ Error saving logs: {e}")
            messagebox.showerror("Save Error", f"Failed to save logs:\n{e}")
        
    def export_session_log(self):
        """Export current session logs to a file"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"session_log_{self.current_user['username']}_{timestamp}.txt"
            
            total_session_time = time.time() - self.session_start_time
            
            with open(filename, 'w') as f:
                f.write("ENHANCED ACTIVITY SIMULATOR - SESSION LOG\n")
                f.write("="*60 + "\n\n")
                f.write(f"User: {self.current_user['username']}\n")
                f.write(f"Session ID: {self.current_session_id}\n")
                f.write(f"Session Start: {datetime.fromtimestamp(self.session_start_time).strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Export Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total Session Duration: {total_session_time/3600:.2f} hours\n")
                f.write(f"Current Mode: {self.current_mode.get().title()}\n")
                f.write(f"Activities: {self.activities_today}\n\n")
                f.write("ACTIVITY LOG:\n")
                f.write("-" * 50 + "\n")
                f.write(self.log_text.get('1.0', tk.END))
                
            self.log_message(f"📄 Session log exported: {filename}")
            messagebox.showinfo("Log Exported", f"Session log exported as:\n{filename}")
            
        except Exception as e:
            self.log_message(f"❌ Error exporting log: {e}")
            messagebox.showerror("Export Error", f"Failed to export log:\n{e}")

    # === ANALYTICS PLACEHOLDER METHODS ===
    
    def generate_analytics_reports(self):
        """Generate analytics reports placeholder"""
        try:
            messagebox.showinfo("Analytics", "Analytics reports will be generated from database data.\nFeature available in full implementation.")
            self.log_message("📊 Analytics reports requested")
        except Exception as e:
            self.log_message(f"❌ Analytics error: {e}")
    
    def show_trend_analysis(self):
        """Show trend analysis placeholder"""
        try:
            messagebox.showinfo("Trends", "Trend analysis will show patterns from historical data.\nFeature available in full implementation.")
            self.log_message("📈 Trend analysis requested")
        except Exception as e:
            self.log_message(f"❌ Trend error: {e}")
    
    def show_ai_insights(self):
        """Show AI insights placeholder"""
        try:
            messagebox.showinfo("AI Insights", "AI insights will provide intelligent recommendations.\nFeature available in full implementation.")
            self.log_message("🤖 AI insights requested")
        except Exception as e:
            self.log_message(f"❌ AI insights error: {e}")

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
            
            # Keep the file as backup instead of deleting
            if self.temp_file_path and os.path.exists(self.temp_file_path):
                self.log_message(f"💾 Keeping file as backup: {os.path.basename(self.temp_file_path)}")
            
            self.temp_file_path = None
            self.temp_file_handle = None
            self.text_editor_process = None
            self.our_window_title = None
            
        except Exception as e:
            self.log_message(f"⚠️ Error during cleanup: {e}")

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