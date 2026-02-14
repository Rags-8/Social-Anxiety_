import subprocess
import time
import sys
import re
import threading
import webbrowser
import os

def stream_reader(pipe, label, url_event, url_container):
    """Reads stream and prints it. If it finds a URL, sets the event."""
    try:
        for line in iter(pipe.readline, ''):
            if not line:
                break
            line = line.strip()
            # print(f"[{label}] {line}") # Debugging only needed if it fails

            # Look for Serveo URL
            if "Forwarding HTTP traffic from" in line:
                match = re.search(r'(https?://[^\s]+)', line)
                if match:
                    url = match.group(1)
                    url_container[0] = url
                    url_event.set()
            
            # Look for Localhost.run URL
            if ".lhr.life" in line or "localhost.run" in line:
                 match = re.search(r'(https?://[^\s]+\.lhr\.life)', line)
                 if match:
                    url = match.group(1)
                    url_container[0] = url
                    url_event.set()

    except Exception as e:
        print(f"Error reading {label}: {e}")

def main():
    print("========================================================")
    print("        STARTING YOUR PUBLIC DEMO... PLEASE WAIT")
    print("========================================================")

    # 1. Start Backend
    print(" -> Starting Backend...")
    backend = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "main:app", "--reload", "--port", "8000"],
        cwd="backend",
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=subprocess.CREATE_NEW_CONSOLE
    )

    # 2. Start Frontend
    print(" -> Starting Frontend...")
    # Set environment variable for the frontend process
    env = os.environ.copy()
    env["API_URL"] = "http://localhost:8000"
    
    frontend = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "streamlit_app.py", "--server.port", "8501"],
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=subprocess.CREATE_NEW_CONSOLE
    )

    # 3. Start Tunnel (Serveo)
    print(" -> Establishing Public Tunnel (this takes 5-10 seconds)...")
    
    # We use -tt to force pseudo-tty allocation which sometimes helps with ssh output buffering
    # But for serveo straightforward piping is usually fine.
    # We need to capture stdout/stderr to find the link.
    tunnel_cmd = ["ssh", "-o", "StrictHostKeyChecking=no", "-R", "80:localhost:8501", "serveo.net"]
    
    # On Windows, ssh might output to stderr
    tunnel = subprocess.Popen(
        tunnel_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        encoding='utf-8',
        bufsize=1,
        universal_newlines=True
    )

    url_event = threading.Event()
    url_container = [None]

    # Start a thread to monitor output
    t = threading.Thread(
        target=stream_reader, 
        args=(tunnel.stdout, "TUNNEL", url_event, url_container),
        daemon=True
    )
    t.start()

    # Wait for URL
    found = url_event.wait(timeout=20)

    if found and url_container[0]:
        public_url = url_container[0]
        print("\n========================================================")
        print("          SUCCESS! YOUR PUBLIC APP IS READY")
        print("========================================================")
        print(f"\n   LINK:  {public_url}")
        print("\n========================================================")
        print("Opening in your browser now...")
        webbrowser.open(public_url)
    else:
        print("\n[!] Could not auto-detect URL from Serveo.")
        print("    Please check the raw output above or try again.")

    print("\nPress Ctrl+C to stop the demo.")
    
    try:
        tunnel.wait()
    except KeyboardInterrupt:
        print("\nStopping...")
        backend.terminate()
        frontend.terminate()
        tunnel.terminate()
        sys.exit(0)

if __name__ == "__main__":
    main()
