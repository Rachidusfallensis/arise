#!/usr/bin/env python3
"""
Real-time log monitoring for SAFE MBSE RAG System
"""

import time
import subprocess
import sys
from pathlib import Path

def monitor_logs():
    """Monitor logs in real-time using tail"""
    log_file = Path("logs/requirements_generation.log")
    
    print("📊 SAFE MBSE RAG System - Log Monitor")
    print("=" * 50)
    print(f"📄 Monitoring: {log_file}")
    print("🛑 Press Ctrl+C to stop monitoring")
    print("=" * 50)
    
    # Create log file if it doesn't exist
    log_file.parent.mkdir(exist_ok=True)
    if not log_file.exists():
        log_file.touch()
        print("📝 Created log file")
    
    try:
        # Use tail -f to follow the log file
        if sys.platform.startswith('win'):
            # Windows: Use PowerShell Get-Content with -Wait
            subprocess.run([
                "powershell", "-Command", 
                f"Get-Content -Path '{log_file}' -Wait -Tail 10"
            ])
        else:
            # Unix/Linux/macOS: Use tail -f
            subprocess.run(["tail", "-f", str(log_file)])
    
    except KeyboardInterrupt:
        print("\n🛑 Log monitoring stopped")
    except FileNotFoundError:
        print("❌ tail command not found. Falling back to Python monitoring...")
        python_monitor(log_file)
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Falling back to Python monitoring...")
        python_monitor(log_file)

def python_monitor(log_file):
    """Python-based log monitoring fallback"""
    try:
        # Read existing content
        with open(log_file, 'r') as f:
            f.seek(0, 2)  # Go to end of file
            
        print("📖 Monitoring logs (Python fallback)...")
        
        while True:
            with open(log_file, 'r') as f:
                f.seek(0, 2)  # Go to end
                
                while True:
                    line = f.readline()
                    if not line:
                        time.sleep(0.1)
                        continue
                    print(line.rstrip())
    
    except KeyboardInterrupt:
        print("\n🛑 Log monitoring stopped")
    except Exception as e:
        print(f"❌ Error monitoring logs: {e}")

if __name__ == "__main__":
    monitor_logs() 