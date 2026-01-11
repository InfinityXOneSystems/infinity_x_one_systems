import sys
import os
from pathlib import Path
import asyncio
import threading

from production_orchestrator import ProductionAgentOrchestrator

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

class ProductionOrchestratorService:

    def __init__(self):
        self.orchestrator = None
        self.orchestrator_thread = None

    def _run_orchestrator(self):
        """Run the orchestrator in a thread"""
        try:
            # Create a new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            # Start all agents
            loop.run_until_complete(self.orchestrator.start())

            # Keep the service running
            while True:
                time.sleep(1)

        except Exception as e:
            print(f"Orchestrator thread failed: {e}")
        finally:
            # Cleanup
            if self.orchestrator:
                try:
                    loop.run_until_complete(self.orchestrator.stop())
                except:
                    pass

if __name__ == '__main__':
    # For Linux, we can directly run the orchestrator
    orchestrator = ProductionAgentOrchestrator()
    asyncio.run(orchestrator.run())
