import psutil
import time
import datetime
import sys
import threading
import os
from flask import Flask, request, jsonify
from flask_cors import CORS

class Blocker:
    def __init__(self):
        self.blocking_active = False
        self.monitoring_thread = None
        self.stop_event = threading.Event()
        self.check_interval_seconds = 1.0
        self.target_apps = []
        
        self.timer_seconds_remaining = 0
        self.timer_job = None
        self.start_time = None

    def start_blocking(self, apps_to_block, minutes):
        if self.blocking_active:
            return False, "Blocking is already active."

        self.target_apps = [app.lower() for app in apps_to_block]
        self.timer_seconds_remaining = int(minutes) * 60
        self.start_time = time.time()
        
        if not self.target_apps:
            return False, "No applications specified."
            
        self.blocking_active = True
        
        self.log_message(f"Focus session started for {minutes} minutes. Blocking: {', '.join(self.target_apps)}", "INFO")
        
        self.stop_event.clear()
        self.monitoring_thread = threading.Thread(target=self.monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        self.update_timer()
        return True, "Session started."

    def stop_blocking(self):
        if not self.blocking_active:
            return False, "Not active."
            
        self.blocking_active = False
        self.stop_event.set()
        
        # Stop the timer
        if self.timer_job:
            self.timer_job.cancel()
            self.timer_job = None
        
        if self.timer_seconds_remaining <= 0:
             self.log_message("Focus session completed successfully", "SUCCESS")
        else:
             self.log_message("Focus session terminated manually", "INFO")
             
        self.timer_seconds_remaining = 0
        return True, "Session stopped."

    def update_timer(self):
        """Internal timer that runs in its own thread."""
        if self.timer_seconds_remaining > 0:
            self.timer_seconds_remaining -= 1
            self.timer_job = threading.Timer(1.0, self.update_timer)
            self.timer_job.start()
        else:
            self.log_message("Focus session completed successfully", "SUCCESS")
            self.stop_blocking()

    def get_status(self):
        return {
            "isActive": self.blocking_active,
            "timeRemaining": self.timer_seconds_remaining,
            "targets": self.target_apps
        }

    def monitoring_loop(self):
        """The core loop that runs in a background thread to check and kill processes."""
        print("Monitoring loop started...")
        while not self.stop_event.is_set():
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if proc.info['name'].lower() in self.target_apps:
                        pid = proc.info['pid']
                        name = proc.info['name']
                        self.log_message(f"Blocked application: {name} (PID: {pid})", "INFO")
                        self.terminate_process(proc)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    proc_name = proc.info.get('name', 'unknown process')
                    self.log_message(f"Access denied for {proc_name}. Try running as administrator.", "ERROR")
                except Exception as e:
                    self.log_message(f"An unexpected error occurred: {e}", "ERROR")
            
            self.stop_event.wait(self.check_interval_seconds)
        print("Monitoring loop stopped.")

    def terminate_process(self, proc):
        """Safely terminates a process, trying gracefully first, then forcing it."""
        try:
            name = proc.name()
            pid = proc.pid
            
            proc.terminate()
            gone, alive = psutil.wait_procs([proc], timeout=1)
            
            if alive:
                self.log_message(f"{name} (PID: {pid}) unresponsive. Forcing kill.", "INFO")
                proc.kill()
            
            self.log_message(f"Successfully terminated {name} (PID: {pid})", "SUCCESS")

        except psutil.NoSuchProcess:
            pass
        except psutil.AccessDenied:
            self.log_message(f"Access denied to terminate {proc.name()} (PID: {proc.pid})", "ERROR")

    def write_to_history_log(self, message):
        """Writes a message to the persistent log file."""
        try:
            with open(HISTORY_LOG_FILE, 'a', encoding='utf-8') as f:
                f.write(message)
        except Exception as e:
            print(f"Error writing to history log: {e}")

    def log_message(self, message, level="INFO"):
        """Appends a timestamped message to the UI log area AND writes to history."""
        now_log = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted_message_log = f"[{now_log}] [{level.upper()}] {message}\n"
        print(formatted_message_log) # Log to console
        self.write_to_history_log(formatted_message_log)

HISTORY_LOG_FILE = "focus_history.log"

app = Flask(__name__)
CORS(app)  
blocker = Blocker() 

@app.route('/start', methods=['POST'])
def start_session():
    data = request.json
    apps = data.get('apps', [])
    minutes = data.get('minutes', 25)
    
    if not apps:
        return jsonify({"success": False, "message": "No apps provided"}), 400
        
    success, message = blocker.start_blocking(apps, minutes)
    return jsonify({"success": success, "message": message})

@app.route('/stop', methods=['POST'])
def stop_session():
    success, message = blocker.stop_blocking()
    return jsonify({"success": success, "message": message})

@app.route('/status', methods=['GET'])
def get_status():
    return jsonify(blocker.get_status())

@app.route('/history', methods=['GET'])
def get_history():
    history_content = "No history found."
    if os.path.exists(HISTORY_LOG_FILE):
        try:
            with open(HISTORY_LOG_FILE, 'r', encoding='utf-8') as f:
                history_content = f.read()
        except Exception as e:
            history_content = f"Error loading history: {e}"
    return jsonify({"history": history_content})

@app.route('/shutdown', methods=['POST'])
def shutdown():
    """Gracefully shutdown the server"""
    def shutdown_server():
        time.sleep(1)
        os._exit(0)
    
    threading.Thread(target=shutdown_server).start()
    return jsonify({"success": True, "message": "Server shutting down..."})

if __name__ == "__main__":
    print("Starting Zenith Focus Server...")
    print("WARNING: Run this terminal as an ADMINISTRATOR to block system apps.")
    app.run(debug=True, port=5000)