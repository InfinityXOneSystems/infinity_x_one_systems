# Infinity XOS Production Agent Orchestrator Windows Service
# Install with: python production_orchestrator_service.py install
# Start with: python production_orchestrator_service.py start
# Stop with: python production_orchestrator_service.py stop
# Remove with: python production_orchestrator_service.py remove

import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import sys
import os
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from production_orchestrator import ProductionAgentOrchestrator
import asyncio
import threading

class ProductionOrchestratorService(win32serviceutil.ServiceFramework):
    _svc_name_ = "InfinityXOSProductionOrchestrator"
    _svc_display_name_ = "Infinity XOS Production Agent Orchestrator"
    _svc_description_ = "Production-grade orchestrator for all Infinity XOS agents with 24/7 autonomous operation"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.orchestrator = None
        self.orchestrator_thread = None
        socket.setdefaulttimeout(60)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

        # Stop the orchestrator
        if self.orchestrator:
            # Run stop in a thread to avoid blocking
            stop_thread = threading.Thread(target=self._stop_orchestrator_sync)
            stop_thread.start()
            stop_thread.join(timeout=30)  # Wait up to 30 seconds

    def _stop_orchestrator_sync(self):
        """Synchronous wrapper to stop orchestrator"""
        try:
            # Create a new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            # Stop the orchestrator
            loop.run_until_complete(self.orchestrator.stop_all_agents())
            loop.close()
        except Exception as e:
            servicemanager.LogErrorMsg(f"Error stopping orchestrator: {e}")

    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                            servicemanager.EVENTLOG_INFORMATION_TYPE,
                            (self._svc_name_, " service is starting"))

        try:
            # Initialize orchestrator
            workspace_root = os.environ.get('WORKSPACE_ROOT', r"c:\AI\repos")
            self.orchestrator = ProductionAgentOrchestrator(workspace_root)

            # Start orchestrator in a separate thread
            self.orchestrator_thread = threading.Thread(target=self._run_orchestrator)
            self.orchestrator_thread.daemon = True
            self.orchestrator_thread.start()

            # Wait for stop event
            win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)

        except Exception as e:
            servicemanager.LogErrorMsg(f"Service failed: {e}")

        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                            servicemanager.EVENTLOG_INFORMATION_TYPE,
                            (self._svc_name_, " service has stopped"))

    def _run_orchestrator(self):
        """Run the orchestrator in a thread"""
        try:
            # Create a new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            # Start all agents
            loop.run_until_complete(self.orchestrator.start_all_agents())

            # Keep the service running
            while True:
                # Check if we should stop
                if win32event.WaitForSingleObject(self.hWaitStop, 1000) == win32event.WAIT_OBJECT_0:
                    break

                # Small delay to prevent busy waiting
                import time
                time.sleep(1)

        except Exception as e:
            servicemanager.LogErrorMsg(f"Orchestrator thread failed: {e}")
        finally:
            # Cleanup
            if self.orchestrator:
                try:
                    loop.run_until_complete(self.orchestrator.stop_all_agents())
                except:
                    pass

if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(ProductionOrchestratorService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(ProductionOrchestratorService)