"""
Infinity XOS Production Agent Orchestrator
==========================================

Unified production-grade system for managing all agents with:
- Background execution (systemd/docker services)
- Parallel processing (multi-threading/async)
- Autonomous operation (self-scheduling, self-healing)
- 24/7 persistence (health monitoring, auto-restart)
- Full integration with /results system

This system orchestrates 50+ agents across multiple repositories:
- infinity-crawler: Web scraping workers
- autonomous_crawler: Autonomous crawling system
- background_agent: Maintenance agents
- Real_Estate_Intelligence: 40+ domain agents
- agent_communication: Communication framework
- agent_intelligence: Intelligence processing
"""

import asyncio
import json
import logging
import os
import signal
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
import subprocess
import psutil
import threading
import queue

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('production_orchestrator.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('production_orchestrator')

class ProductionAgentOrchestrator:
    """Production-grade orchestrator for all agents"""

    def __init__(self, workspace_root: str = r"c:\AI\repos"):
        self.workspace_root = Path(workspace_root)
        self.results_dir = self.workspace_root / "mcp" / "results"
        self.agents_dir = self.workspace_root / "production_agents"
        self.agents_dir.mkdir(exist_ok=True)

        # Agent management
        self.active_agents: Dict[str, Dict[str, Any]] = {}
        self.agent_processes: Dict[str, subprocess.Popen] = {}
        self.agent_threads: Dict[str, threading.Thread] = {}
        self.task_queue = queue.Queue()
        self.executor = ThreadPoolExecutor(max_workers=20)

        # Health monitoring
        self.health_checks: Dict[str, Dict[str, Any]] = {}
        self.last_health_check = datetime.now()

        # Autonomous scheduling
        self.scheduled_tasks: List[Dict[str, Any]] = []
        self.scheduler_thread: Optional[threading.Thread] = None

        # Shutdown handling
        self.running = True
        self.shutdown_event = threading.Event()

        logger.info("Production Agent Orchestrator initialized")

    def discover_agents(self) -> Dict[str, Dict[str, Any]]:
        """Discover all agents across repositories"""
        agents = {}

        # infinity-crawler workers
        crawler_path = self.workspace_root / "infinity-xos" / "systems" / "infinity-crawler"
        if crawler_path.exists():
            agents["infinity-crawler"] = {
                "type": "crawler",
                "path": str(crawler_path / "worker"),
                "command": ["node", "launch_crawler_team.js"],
                "workers": 5,
                "autonomous": True,
                "background": True,
                "parallel": True,
                "health_check_interval": 30,
                "restart_on_failure": True
            }

        # autonomous_crawler
        auto_crawler_path = self.workspace_root / "autonomous_crawler"
        if auto_crawler_path.exists():
            agents["autonomous-crawler"] = {
                "type": "crawler",
                "path": str(auto_crawler_path),
                "command": ["python", "controller/autonomous_controller.py"],
                "workers": 3,
                "autonomous": True,
                "background": True,
                "parallel": True,
                "health_check_interval": 60,
                "restart_on_failure": True
            }

        # background_agent
        bg_agent_path = self.workspace_root / "background_agent"
        if bg_agent_path.exists():
            agents["background-maintenance"] = {
                "type": "maintenance",
                "path": str(bg_agent_path),
                "command": ["python", "agents/maintenance.py"],
                "workers": 1,
                "autonomous": True,
                "background": True,
                "parallel": False,
                "health_check_interval": 300,  # 5 minutes
                "restart_on_failure": True,
                "schedule": "0 */6 * * *"  # Every 6 hours
            }

        # Real Estate Intelligence agents (40+ agents)
        rei_path = self.workspace_root / "Real_Estate_Intelligence"
        if rei_path.exists():
            rei_agents = self._discover_rei_agents(rei_path)
            agents.update(rei_agents)

        # agent_communication
        comm_path = self.workspace_root / "agent_communication"
        if comm_path.exists():
            agents["agent-communication"] = {
                "type": "communication",
                "path": str(comm_path),
                "command": ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"],
                "workers": 1,
                "autonomous": True,
                "background": True,
                "parallel": False,
                "health_check_interval": 30,
                "restart_on_failure": True
            }

        # agent_intelligence
        intel_path = self.workspace_root / "agent_intelligence"
        if intel_path.exists():
            agents["agent-intelligence"] = {
                "type": "intelligence",
                "path": str(intel_path),
                "command": ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"],
                "workers": 1,
                "autonomous": True,
                "background": True,
                "parallel": False,
                "health_check_interval": 30,
                "restart_on_failure": True
            }

        # orchestrator
        orch_path = self.workspace_root / "orchestrator"
        if orch_path.exists():
            agents["orchestrator"] = {
                "type": "orchestrator",
                "path": str(orch_path),
                "command": ["python", "main.py"],
                "workers": 1,
                "autonomous": True,
                "background": True,
                "parallel": False,
                "health_check_interval": 15,
                "restart_on_failure": True
            }

        logger.info(f"Discovered {len(agents)} agents")
        return agents

    def _discover_rei_agents(self, rei_path: Path) -> Dict[str, Dict[str, Any]]:
        """Discover Real Estate Intelligence agents"""
        agents = {}
        agents_dir = rei_path / "agents"

        if not agents_dir.exists():
            return agents

        # Common agent configuration
        base_config = {
            "type": "domain_specialist",
            "workers": 1,
            "autonomous": True,
            "background": True,
            "parallel": True,
            "health_check_interval": 60,
            "restart_on_failure": True,
            "domain": "real_estate"
        }

        # List of known REI agents
        rei_agent_names = [
            "acquisition-hunter", "ai-governance-officer", "client-relations",
            "commercial-strategist", "commercial-titan", "communication-director",
            "creative-designer", "customer-support", "cybersecurity-chief",
            "data-analyst", "deal-closer", "deal-sniper", "echo",
            "engineering-companion", "executive-assistant", "financial-advisor",
            "finsynapse", "first-time-guide", "growth-architect", "hr-recruiting",
            "it-service-desk", "knowledge-manager", "land-developer",
            "legal-compliance", "luxury-specialist", "maintenance-agent",
            "market-intelligence", "market-prophet", "marketing-content-creator",
            "multifamily-master", "negotiation-ninja", "onboarding-specialist",
            "operations-director", "procurement-specialist", "product-manager",
            "project-manager", "quality-assurance", "sales-development",
            "shadow-agent", "strategy-advisor", "systems-architect", "wealth-architect"
        ]

        for agent_name in rei_agent_names:
            agent_path = agents_dir / agent_name
            if agent_path.exists():
                # Check if it has identity.ts (TypeScript agent)
                identity_file = agent_path / "identity.ts"
                if identity_file.exists():
                    agent_config = base_config.copy()
                    agent_config.update({
                        "name": f"rei-{agent_name}",
                        "path": str(agent_path),
                        "command": ["npx", "ts-node", "identity.ts"],
                        "identity_file": str(identity_file)
                    })
                    agents[f"rei-{agent_name}"] = agent_config
                else:
                    # Python agent fallback
                    main_file = agent_path / "main.py"
                    if main_file.exists():
                        agent_config = base_config.copy()
                        agent_config.update({
                            "name": f"rei-{agent_name}",
                            "path": str(agent_path),
                            "command": ["python", "main.py"]
                        })
                        agents[f"rei-{agent_name}"] = agent_config

        logger.info(f"Discovered {len(agents)} Real Estate Intelligence agents")
        return agents

    async def start_agent(self, agent_id: str, agent_config: Dict[str, Any]) -> bool:
        """Start an agent in background mode"""
        try:
            logger.info(f"Starting agent: {agent_id}")

            # Change to agent directory
            cwd = agent_config["path"]

            # For parallel agents, start multiple instances
            workers = agent_config.get("workers", 1)
            processes = []

            for i in range(workers):
                worker_id = f"{agent_id}-worker-{i+1}" if workers > 1 else agent_id

                # Start process
                if agent_config.get("background", True):
                    process = subprocess.Popen(
                        agent_config["command"],
                        cwd=cwd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
                    )
                    processes.append(process)
                    self.agent_processes[worker_id] = process
                    logger.info(f"Started background process for {worker_id} (PID: {process.pid})")
                else:
                    # Start in thread
                    thread = threading.Thread(
                        target=self._run_agent_thread,
                        args=(worker_id, agent_config, cwd),
                        daemon=True
                    )
                    thread.start()
                    self.agent_threads[worker_id] = thread
                    logger.info(f"Started thread for {worker_id}")

            # Update active agents
            self.active_agents[agent_id] = {
                "config": agent_config,
                "started_at": datetime.now(),
                "workers": workers,
                "processes": processes if processes else None,
                "status": "running"
            }

            return True

        except Exception as e:
            logger.error(f"Failed to start agent {agent_id}: {e}")
            return False

    def _run_agent_thread(self, agent_id: str, config: Dict[str, Any], cwd: str):
        """Run agent in a thread"""
        try:
            while self.running and not self.shutdown_event.is_set():
                # Agent logic here - for now just sleep
                time.sleep(1)
        except Exception as e:
            logger.error(f"Agent thread {agent_id} error: {e}")

    async def stop_agent(self, agent_id: str) -> bool:
        """Stop an agent"""
        try:
            logger.info(f"Stopping agent: {agent_id}")

            # Stop processes
            if agent_id in self.active_agents:
                agent_info = self.active_agents[agent_id]
                processes = agent_info.get("processes", [])

                for process in processes:
                    if process and process.poll() is None:
                        process.terminate()
                        try:
                            process.wait(timeout=5)
                        except subprocess.TimeoutExpired:
                            process.kill()

                # Clean up
                self.active_agents.pop(agent_id, None)

            # Stop threads
            for worker_id, thread in list(self.agent_threads.items()):
                if worker_id.startswith(f"{agent_id}-"):
                    # Thread will stop when self.running becomes False
                    pass

            logger.info(f"Stopped agent: {agent_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to stop agent {agent_id}: {e}")
            return False

    async def health_check_agent(self, agent_id: str, agent_config: Dict[str, Any]) -> Dict[str, Any]:
        """Perform health check on an agent"""
        health_status = {
            "agent_id": agent_id,
            "timestamp": datetime.now(),
            "status": "unknown",
            "details": {}
        }

        try:
            # Check if agent is in active agents
            if agent_id not in self.active_agents:
                health_status["status"] = "stopped"
                return health_status

            agent_info = self.active_agents[agent_id]
            processes = agent_info.get("processes", [])

            if processes:
                # Check process health
                all_alive = True
                pids = []

                for process in processes:
                    if process.poll() is not None:
                        all_alive = False
                    else:
                        pids.append(process.pid)

                health_status["status"] = "healthy" if all_alive else "unhealthy"
                health_status["details"] = {
                    "pids": pids,
                    "alive_count": sum(1 for p in processes if p.poll() is None),
                    "total_count": len(processes)
                }
            else:
                # Thread-based agent - assume healthy if running
                health_status["status"] = "healthy"
                health_status["details"] = {"type": "thread"}

        except Exception as e:
            logger.error(f"Health check failed for {agent_id}: {e}")
            health_status["status"] = "error"
            health_status["details"] = {"error": str(e)}

        self.health_checks[agent_id] = health_status
        return health_status

    async def monitor_agents(self):
        """Monitor all agents and restart failed ones"""
        while self.running:
            try:
                current_time = datetime.now()

                # Health check all active agents
                for agent_id, agent_config in list(self.active_agents.items()):
                    last_check = self.health_checks.get(agent_id, {}).get("timestamp", datetime.min)
                    interval = agent_config["config"].get("health_check_interval", 60)

                    if (current_time - last_check).seconds >= interval:
                        health = await self.health_check_agent(agent_id, agent_config["config"])

                        if health["status"] == "unhealthy" and agent_config["config"].get("restart_on_failure", False):
                            logger.warning(f"Agent {agent_id} unhealthy, restarting...")
                            await self.stop_agent(agent_id)
                            await asyncio.sleep(2)  # Wait before restart
                            await self.start_agent(agent_id, agent_config["config"])

                # Check for scheduled tasks
                await self._process_scheduled_tasks()

                await asyncio.sleep(10)  # Check every 10 seconds

            except Exception as e:
                logger.error(f"Monitor error: {e}")
                await asyncio.sleep(10)

    async def _process_scheduled_tasks(self):
        """Process autonomous scheduled tasks"""
        current_time = datetime.now()

        for task in self.scheduled_tasks:
            if task.get("next_run", datetime.max) <= current_time:
                try:
                    # Execute scheduled task
                    await self._execute_scheduled_task(task)

                    # Schedule next run
                    interval = task.get("interval_minutes", 60)
                    task["next_run"] = current_time + timedelta(minutes=interval)

                except Exception as e:
                    logger.error(f"Scheduled task failed: {e}")

    async def _execute_scheduled_task(self, task: Dict[str, Any]):
        """Execute a scheduled task"""
        task_type = task.get("type")

        if task_type == "maintenance":
            # Run maintenance on all repos
            await self.run_maintenance_cycle()
        elif task_type == "health_report":
            # Generate health report
            await self.generate_health_report()
        elif task_type == "data_sync":
            # Sync data with /results system
            await self.sync_with_results_system()

    async def run_maintenance_cycle(self):
        """Run maintenance cycle on all repositories"""
        logger.info("Running maintenance cycle")

        # This would integrate with the maintenance agent
        # For now, just log
        maintenance_results = {
            "timestamp": datetime.now(),
            "repos_checked": len(list(self.workspace_root.glob("*"))),
            "status": "completed"
        }

        # Save to results system
        await self.save_to_results_system("maintenance", maintenance_results)

    async def generate_health_report(self):
        """Generate comprehensive health report"""
        logger.info("Generating health report")

        report = {
            "timestamp": datetime.now(),
            "active_agents": len(self.active_agents),
            "total_processes": len(self.agent_processes),
            "total_threads": len(self.agent_threads),
            "health_status": self.health_checks.copy(),
            "system_resources": self._get_system_resources()
        }

        # Save to results system
        await self.save_to_results_system("health_report", report)

    async def sync_with_results_system(self):
        """Sync agent data with /results system"""
        logger.info("Syncing with results system")

        # Collect agent metrics
        metrics = {
            "timestamp": datetime.now(),
            "agents": list(self.active_agents.keys()),
            "processes": len(self.agent_processes),
            "threads": len(self.agent_threads),
            "health_checks": len(self.health_checks)
        }

        await self.save_to_results_system("agent_metrics", metrics)

    def _get_system_resources(self) -> Dict[str, Any]:
        """Get system resource usage"""
        try:
            return {
                "cpu_percent": psutil.cpu_percent(),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_usage": psutil.disk_usage('/').percent
            }
        except:
            return {"error": "psutil not available"}

    async def save_to_results_system(self, data_type: str, data: Dict[str, Any]):
        """Save data to the /results system"""
        try:
            # Ensure results directory exists
            compiled_dir = self.results_dir / "compiled"
            compiled_dir.mkdir(parents=True, exist_ok=True)

            # Create timestamped file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"production_{data_type}_{timestamp}.json"
            filepath = compiled_dir / filename

            # Save data
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2, default=str)

            # Update manifest
            await self._update_results_manifest(filepath, data_type)

            logger.info(f"Saved {data_type} data to results system: {filepath}")

        except Exception as e:
            logger.error(f"Failed to save to results system: {e}")

    async def _update_results_manifest(self, filepath: Path, data_type: str):
        """Update the results manifest"""
        try:
            manifest_path = self.results_dir / "compiled_manifest.json"

            if manifest_path.exists():
                with open(manifest_path, 'r') as f:
                    manifest = json.load(f)
            else:
                manifest = []

            entry = {
                "source": f"production_orchestrator://{data_type}",
                "compiled": str(filepath),
                "size": filepath.stat().st_size,
                "timestamp": datetime.now().isoformat()
            }

            manifest.append(entry)

            with open(manifest_path, 'w') as f:
                json.dump(manifest, f, indent=2)

        except Exception as e:
            logger.error(f"Failed to update manifest: {e}")

    async def start_all_agents(self):
        """Start all discovered agents"""
        logger.info("Starting all agents...")

        agents = self.discover_agents()

        for agent_id, agent_config in agents.items():
            if agent_config.get("autonomous", False):
                await self.start_agent(agent_id, agent_config)

        # Start monitoring
        self.monitor_task = asyncio.create_task(self.monitor_agents())

        # Start scheduler
        self._start_scheduler()

        logger.info(f"Started {len(self.active_agents)} agents")

    async def stop_all_agents(self):
        """Stop all agents"""
        logger.info("Stopping all agents...")

        self.running = False
        self.shutdown_event.set()

        # Stop monitoring
        if hasattr(self, 'monitor_task'):
            self.monitor_task.cancel()

        # Stop scheduler
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)

        # Stop all agents
        for agent_id in list(self.active_agents.keys()):
            await self.stop_agent(agent_id)

        # Shutdown executor
        self.executor.shutdown(wait=True)

        logger.info("All agents stopped")

    def _start_scheduler(self):
        """Start the autonomous scheduler"""
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self.scheduler_thread.start()

    def _scheduler_loop(self):
        """Scheduler loop for autonomous tasks"""
        while self.running and not self.shutdown_event.is_set():
            try:
                # Schedule maintenance every 6 hours
                if not any(t["type"] == "maintenance" for t in self.scheduled_tasks):
                    self.scheduled_tasks.append({
                        "type": "maintenance",
                        "interval_minutes": 360,  # 6 hours
                        "next_run": datetime.now() + timedelta(minutes=60)
                    })

                # Schedule health reports every hour
                if not any(t["type"] == "health_report" for t in self.scheduled_tasks):
                    self.scheduled_tasks.append({
                        "type": "health_report",
                        "interval_minutes": 60,
                        "next_run": datetime.now() + timedelta(minutes=10)
                    })

                # Schedule data sync every 30 minutes
                if not any(t["type"] == "data_sync" for t in self.scheduled_tasks):
                    self.scheduled_tasks.append({
                        "type": "data_sync",
                        "interval_minutes": 30,
                        "next_run": datetime.now() + timedelta(minutes=5)
                    })

                time.sleep(60)  # Check every minute

            except Exception as e:
                logger.error(f"Scheduler error: {e}")
                time.sleep(60)

    def run_forever(self):
        """Run the orchestrator forever"""
        async def main():
            # Setup signal handlers
            def signal_handler(signum, frame):
                logger.info(f"Received signal {signum}, shutting down...")
                asyncio.create_task(self.stop_all_agents())

            signal.signal(signal.SIGINT, signal_handler)
            signal.signal(signal.SIGTERM, signal_handler)

            try:
                # Start all agents
                await self.start_all_agents()

                # Keep running
                while self.running:
                    await asyncio.sleep(1)

            except KeyboardInterrupt:
                logger.info("Keyboard interrupt received")
            finally:
                await self.stop_all_agents()

        # Run the async main function
        asyncio.run(main())


if __name__ == "__main__":
    orchestrator = ProductionAgentOrchestrator()
    orchestrator.run_forever()