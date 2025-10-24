Zenith Focus 🚀

Zenith Focus is a modern productivity application designed to help you maintain focus by blocking distracting desktop applications during timed work sessions. It features a stunning, web-based user interface (UI) powered by a local Python back-end server.

Features

Modern & Immersive UI: A beautiful front-end built with HTML, Tailwind CSS, and JavaScript, featuring glassmorphism effects and smooth transitions.

Pomodoro Timer: A customizable timer to structure your focus sessions (defaulting to 25 minutes).

3D Animation: An engaging three.js animation on the focus screen enhances the visual experience.

Application Blocking: Specify desktop application executables (e.g., chrome.exe, javaw.exe, Minecraft.Windows.exe) to be automatically terminated during focus sessions.

Interactive Block List: Easily add and remove applications from your block list within the UI.

Session History: View a log of past session events (start, stop, apps blocked) in a dedicated history section.

Mock User Login: A simple login screen provides a professional feel (any non-empty username/password works).

Clean Exit: An "Exit App" button cleanly shuts down the back-end server.

Client-Server Architecture: Separates the visual front-end from the functional back-end for a robust and scalable design.

Architecture

Zenith Focus uses a client-server model:

Front-End Client (focus_app.html):

Runs in your web browser.

Provides the user interface (timer, block list, history).

Built with HTML, Tailwind CSS, and JavaScript (including lucide-icons and three.js).

Sends commands (start, stop, get status, get history, shutdown) to the back-end server via fetch requests.

Back-End Server (app_server.py):

Runs locally on your computer using Python and Flask.

Requires Administrator Privileges to terminate other desktop applications.

Listens for commands from the front-end on http://127.0.0.1:5000.

Manages the focus timer state.

Uses psutil to find and terminate specified processes.

Maintains a persistent session history log (zenith_focus_history.log).

Getting Started

Follow these steps carefully to set up and run the application.

Prerequisites

Python 3: Make sure Python 3 is installed (python.org).

pip: Python's package installer (usually comes with Python).

Git: For cloning the repository (git-scm.com).

Web Browser: Chrome, Firefox, Edge, etc.

Installation & Setup

Clone the Repository:

git clone [https://github.com/YourUsername/zenith-focus-app.git](https://github.com/YourUsername/zenith-focus-app.git) # Replace with your repo URL
cd zenith-focus-app # Navigate into the project folder


Create and Activate Virtual Environment: (Recommended)

# Create the environment (run once)
python -m venv .venv

# Activate the environment (run every time you open a new terminal)
# On Windows:
.\.venv\Scripts\activate
# On macOS/Linux:
# source .venv/bin/activate


Your terminal prompt should now show (.venv).

Install Python Dependencies:

pip install -r requirements.txt


This will install Flask, flask-cors, and psutil.

Running the Application (2 Steps)

You must run the Back-End Server first, and keep it running while you use the Front-End UI.

Step 1: Run the Back-End Server (As Administrator)

⚠️ THIS IS CRITICAL for the app blocking to work! ⚠️

Open your Terminal (Command Prompt, PowerShell, etc.) as an Administrator.

Search for your terminal application in the Start Menu.

Right-click it and select "Run as administrator".

Accept the User Account Control (UAC) prompt.

Navigate to the project directory (e.g., cd path\to\zenith-focus-app).

Activate the virtual environment (if not already active in this admin terminal):

.\.venv\Scripts\activate


Run the Flask server:

python app_server.py
