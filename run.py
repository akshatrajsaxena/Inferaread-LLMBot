import os
import sys
import time
import subprocess
import threading
import signal
from pathlib import Path

class InferaReadRunner:
    def __init__(self):
        self.backend_process = None
        self.frontend_process = None
        self.project_root = Path(__file__).parent
        
    def check_requirements(self):
        print("Checking requirements...")
        backend_files = ["app/model.ipynb",".env"]
        for file_path in backend_files:
            if not (self.project_root / file_path).exists():
                print(f"Missing required file: {file_path}")
                return False
            
        frontendFiles = ["frontend/app.py","frontend/config.py","frontend/utils.py","frontend/requirements.txt"]
        for file_path in frontendFiles:
            if not (self.project_root / file_path).exists():
                print(f"Missing required file: {file_path}")
                return False
        
        print("All required files found!")
        return True
    
    def backend(self):
        print("Starting backend server...")
        try:
            backend_script = self.project_root / "app" / "backend_server.py"
            if not backend_script.exists():
                self.backendScript()
            self.backend_process = subprocess.Popen([sys.executable, str(backend_script)], cwd=self.project_root / "app")
            time.sleep(3)
            
            print("Backend server started on http://localhost:8000")
            return True
            
        except Exception as e:
            print(f"Failed to start backend: {e}")
            return False
    
    def backendScript(self):
        backend_script_content = '''
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        import subprocess
        import time

        print("Starting backend server from notebook code...")
        print("Please ensure your model.ipynb is running or convert it to a .py file")
        print("Backend should be available at http://localhost:8000")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Backend server stopped.")
        '''
        backend_script = self.project_root / "app" / "backend_server.py"
        with open(backend_script, 'w') as f:
            f.write(backend_script_content)
        
        print("Created backend server script. Please ensure your Jupyter notebook is running!")
    
    def frontend(self):
        print("Starting frontend application...")
        try:
            self.frontend_process = subprocess.Popen([sys.executable, "-m", "streamlit", "run", "app.py","--server.port", "8501","--server.address", "localhost","--server.headless", "true"], cwd=self.project_root / "frontend")
            print("Frontend application started on http://localhost:8501")
            return True
        except Exception as e:
            print(f"Failed to start frontend: {e}")
            return False
    
    def terminate(self):
        print("\nStopping all processes...")
        
        if self.backend_process:
            self.backend_process.terminate()
            self.backend_process.wait()
            print("Backend stopped")
        
        if self.frontend_process:
            self.frontend_process.terminate()
            self.frontend_process.wait()
            print("Frontend stopped")
    
    def run(self):
        try:
            print("InferaRead - RAG PDF Query System")
            print("=" * 50)
            if not self.check_requirements():
                print("Requirements check failed. Please ensure all files are present.")
                return

            print("\n Starting services...")
            print("\n  IMPORTANT: Make sure to run your Jupyter notebook (model.ipynb) first!")
            print(" The notebook contains the backend server code.")
            print("Press Enter when the notebook is running...")
            input()
            if self.frontend():
                print("\n InferaRead is now running!")
                print("\n Access URLs:")
                print("   • Backend API: http://localhost:8000")
                print("   • Frontend App: http://localhost:8501")
                try:
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    pass
            
        except KeyboardInterrupt:
            pass
        finally:
            self.terminate()
            print("\n InferaRead stopped")

def signal_handler(signum, frame):
    print("\nInterrupt received, stopping...")
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    runner = InferaReadRunner()
    runner.run()