import logging

import datetime
import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import FastAPI
import jsonschema

app = FastAPI()

LEDGER = []
JOBS = []
RESULTS = []
RUNS = {}
STATE = {}


def now():
    return datetime.datetime.utcnow().isoformat()


def log(event: str, meta: Optional[Dict[str, Any]] = None):
    logging.info(entry, flush=True)
    LEDGER.append(entry)
    logging.info(entry, flush=True)


def inventory() -> Dict[str, Any]:
    inv = {
        "github": {
            "GITHUB_APP_ID": bool(os.getenv("GITHUB_APP_ID")),
            "GITHUB_APP_PRIVATE_KEY_B64": bool(os.getenv("GITHUB_APP_PRIVATE_KEY_B64")),
        },
        "google_cloud": {
            "GOOGLE_APPLICATION_CREDENTIALS": bool(
                os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            ),
        },
        "openai": {
            "OPENAI_API_KEY": bool(os.getenv("OPENAI_API_KEY")),
        },
        "workspace_assumed_via_gcp_sa": bool(
            os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        ),
    }
    missing = []
    for group in inv.values():
        if isinstance(group, dict):
            missing += [k for k, v in group.items() if not v]
    inv["missing"] = sorted(set(missing))
    return inv


# ...existing code...


def load_schema(schema_name):
    schema_path = Path(__file__).parent / "contracts" / schema_name
    with open(schema_path) as f:
        return json.load(f)


GPT_COMMAND_SCHEMA = load_schema("gpt-command.schema.json")
GPT_RESPONSE_SCHEMA = load_schema("gpt-response.schema.json")


def validate_contract(payload, schema):
    try:
        jsonschema.validate(instance=payload, schema=schema)
        return True, None
    except jsonschema.ValidationError as e:
        return False, str(e)


def contract_response(request_id, status, result=None, error=None):
    resp = {
        "request_id": request_id,
        "timestamp": now(),
        "status": status,
        "result": result,
        "error": error,
    }
    jsonschema.validate(instance=resp, schema=GPT_RESPONSE_SCHEMA)
    # Persist response to Firestore and emit telemetry
    try:
        from memory.firestore_memory import FirestoreMemory

        memory = FirestoreMemory(collection_name="orchestrator_responses")
        memory.store(request_id, resp)
    except Exception as e:
        logging.info(f"[FIRESTORE ERROR] {e}")
    try:
        from orchestrator.telemetry import log_event

        log_event({"type": "orchestrator_response", "response": resp})
    except Exception as e:
        logging.info(f"[TELEMETRY ERROR] {e}")
    return resp


# ================= ENFORCED ENDPOINTS =================
@app.post("/execute")
def execute(payload: Dict[str, Any]):
    valid, err = validate_contract(payload, GPT_COMMAND_SCHEMA)
    log("execute_request", {"payload": payload, "valid": valid, "error": err})
    if not valid:
        return contract_response(
            payload.get("request_id", "unknown"), "rejected", error=err
        )
    # dry_run/live mode
    if payload.get("dry_run", False):
        result = {
            "dry_run": True,
            "command": payload["command"],
            "parameters": payload["parameters"],
        }
        return contract_response(payload["request_id"], "accepted", result=result)
    params = payload["parameters"]
    service = params.get("service")
    if service == "github":
        import base64
        from github_app_client import GitHubAppClient

        app_id = os.getenv("GITHUB_APP_ID")
        inst_id = os.getenv("GITHUB_APP_INSTALLATION_ID")
        key_b64 = os.getenv("GITHUB_APP_PRIVATE_KEY_B64")
        private_key_pem = base64.b64decode(key_b64).decode() if key_b64 else None
        gh_client = GitHubAppClient(app_id, inst_id, private_key_pem)
        action = params.get("action")
        if hasattr(gh_client, action):
            result = getattr(gh_client, action)(**params)
        else:
            raise Exception(f"Unknown GitHub action: {action}")
    elif service == "google_workspace":
        # Example: params = {"api": "drive", "method": "list_files", ...}
        api = params.get("api")
        method = params.get("method")
        # Add google logic here
        result = {"google": True, "api": api, "method": method}
    elif service == "crawler":
        urls = params.get("urls", [])
        for url in urls:
            JOBS.append({"url": url, "id": len(JOBS) + 1})
        result = {"crawler": True, "queued": len(urls)}
    else:
        result = {"executed": True, "command": payload["command"], "parameters": params}
    return contract_response(payload["request_id"], "completed", result=result)


@app.get("/jobs")
def get_jobs():
    global JOBS
    jobs = JOBS[:]
    JOBS = []
    return {"jobs": jobs}


@app.post("/results")
def post_results(result: Dict[str, Any]):
    global RESULTS
    RESULTS.append(result)
    return {"status": "received"}


@app.get("/results")
def get_results():
    global RESULTS
    results = RESULTS[:]
    RESULTS = []  # Clear after retrieval
    return {"results": results}


@app.post("/scan")
def scan(payload: Dict[str, Any]):
    valid, err = validate_contract(payload, GPT_COMMAND_SCHEMA)
    log("scan_request", {"payload": payload, "valid": valid, "error": err})
    if not valid:
        return contract_response(
            payload.get("request_id", "unknown"), "rejected", error=err
        )
    # dry_run/live mode
    if payload.get("dry_run", False):
        result = {
            "dry_run": True,
            "command": payload["command"],
            "parameters": payload["parameters"],
        }
        return contract_response(payload["request_id"], "accepted", result=result)
    # Actual scan stub
    result = {
        "scanned": True,
        "command": payload["command"],
        "parameters": payload["parameters"],
    }
    return contract_response(payload["request_id"], "completed", result=result)


@app.post("/ingest")
def ingest(payload: Dict[str, Any]):
    valid, err = validate_contract(payload, GPT_COMMAND_SCHEMA)
    log("ingest_request", {"payload": payload, "valid": valid, "error": err})
    if not valid:
        return contract_response(
            payload.get("request_id", "unknown"), "rejected", error=err
        )
    if payload.get("dry_run", False):
        result = {
            "dry_run": True,
            "command": payload["command"],
            "parameters": payload["parameters"],
        }
        return contract_response(payload["request_id"], "accepted", result=result)
    result = {
        "ingested": True,
        "command": payload["command"],
        "parameters": payload["parameters"],
    }
    return contract_response(payload["request_id"], "completed", result=result)


@app.post("/index")
def index(payload: Dict[str, Any]):
    valid, err = validate_contract(payload, GPT_COMMAND_SCHEMA)
    log("index_request", {"payload": payload, "valid": valid, "error": err})
    if not valid:
        return contract_response(
            payload.get("request_id", "unknown"), "rejected", error=err
        )
    if payload.get("dry_run", False):
        result = {
            "dry_run": True,
            "command": payload["command"],
            "parameters": payload["parameters"],
        }
        return contract_response(payload["request_id"], "accepted", result=result)
    result = {
        "indexed": True,
        "command": payload["command"],
        "parameters": payload["parameters"],
    }
    return contract_response(payload["request_id"], "completed", result=result)


@app.post("/evolve-docs")
def evolve_docs(payload: Dict[str, Any]):
    valid, err = validate_contract(payload, GPT_COMMAND_SCHEMA)
    log("evolve_docs_request", {"payload": payload, "valid": valid, "error": err})
    if not valid:
        return contract_response(
            payload.get("request_id", "unknown"), "rejected", error=err
        )
    if payload.get("dry_run", False):
        result = {
            "dry_run": True,
            "command": payload["command"],
            "parameters": payload["parameters"],
        }
        return contract_response(payload["request_id"], "accepted", result=result)
    result = {
        "evolved": True,
        "command": payload["command"],
        "parameters": payload["parameters"],
    }
    return contract_response(payload["request_id"], "completed", result=result)


@app.get("/status")
def status():
    # Emit orchestrator status in contract format
    resp = contract_response("status", "completed", result={"state": STATE})
    log("status_request", resp)
    return resp


@app.get("/agent/next_task")
def next_task(agent_id: str):
    """Endpoint for agents to get next task"""
    # Return empty task for now to prevent 404 errors
    return {"task": None, "status": "no_tasks"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
# ============================================================
