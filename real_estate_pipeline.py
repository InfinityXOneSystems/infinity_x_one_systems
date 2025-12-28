import logging

import requests
import time
import json
import os
import csv
from datetime import datetime
import sys

# Add MCP path for vision cortex imports
sys.path.append(r'c:\AI\repos\mcp')

ORCHESTRATOR_URL = "http://localhost:8000"
RESULTS_DIR = r"c:\AI\repos\mcp\results"

# Real estate data sources
REAL_ESTATE_SOURCES = [
    "https://www.realtor.com/realestateandhomes-search/San-Francisco_CA",
    "https://www.zillow.com/san-francisco-ca/",
    "https://www.redfin.com/city/17151/CA/San-Francisco",
    # Add more as needed
]

def submit_crawl_jobs(urls):
    payload = {
        "request_id": "real-estate-crawl",
        "command": "crawl",
        "parameters": {
            "service": "crawler",
            "urls": urls
        }
    }
        logging.info("Crawl jobs submitted successfully")
    if response.status_code == 200:
        logging.info("Crawl jobs submitted successfully")
        return True
    else:
        logging.info(f"Failed to submit jobs: {response.text}")
        return False

def collect_crawl_results():
    # Poll for results
    results = []
    for _ in range(30):  # Poll for 30 seconds
        response = requests.get(f"{ORCHESTRATOR_URL}/results")
        if response.status_code == 200:
            data = response.json()
            results.extend(data.get("results", []))
        if results:
            break
        time.sleep(1)
    return results

def save_unclean_data_to_results(data, pipeline_name="real_estate"):
    """Save unclean/raw crawl data to /results/compiled/"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{pipeline_name}_unclean_{timestamp}.json"

    # Ensure compiled directory exists
    compiled_dir = os.path.join(RESULTS_DIR, "compiled")
    os.makedirs(compiled_dir, exist_ok=True)

    filepath = os.path.join(compiled_dir, filename)

    # Save as JSON
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)

    # Also save as CSV for compiled format
    csv_filename = f"{pipeline_name}_unclean_{timestamp}.json.csv"
    csv_filepath = os.path.join(compiled_dir, csv_filename)

    if data:
        # Flatten JSON to CSV (simple approach)
        with open(csv_filepath, 'w', newline='') as csvfile:
            if isinstance(data, list) and data:
                fieldnames = data[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
            elif isinstance(data, dict):
                writer = csv.writer(csvfile)
                for key, value in data.items():
                    writer.writerow([key, str(value)])

    logging.info(f"Saved unclean data to {filepath} and {csv_filepath}")
    return filepath, csv_filepath

def process_with_vision_cortex(data):
    """Process data using Vision Cortex agents"""
    try:
        from vision_cortex.agents.headless_crawler import HeadlessCrawlerAgent
        from vision_cortex.agents.base_agent import AgentContext

        logging.info("Processing data with Vision Cortex agents...")

        agent = HeadlessCrawlerAgent()
        insights = []

        for item in data:
            # Create agent context
            context = AgentContext(
                session_id="real_estate_pipeline",
                task_id=f"process_{len(insights)}",
                governance_level="MEDIUM"
            )

            # Process each item (could be enhanced with more sophisticated analysis)
            payload = {
                "url": item.get("url", ""),
                "data": item
            }

            result = agent.run_task(context, payload)

            insight = {
                "original_url": item.get("url", ""),
                "processed_at": datetime.now().isoformat(),
                "agent_result": result,
                "analysis": "Vision Cortex processed real estate data",
                "insights": {
                    "data_quality": "high" if result.get("status_code") == 200 else "low",
                    "content_length": len(str(result.get("content_snippet", ""))),
                    "processing_confidence": 0.85
                }
            }
            insights.append(insight)

        return insights

    except ImportError as e:
        logging.info(f"Vision Cortex not available: {e}")
        # Fallback processing
        return process_fallback(data)

def process_fallback(data):
    """Fallback processing when Vision Cortex is not available"""
    logging.info("Using fallback processing...")
    insights = []
    for item in data:
        insight = {
            "url": item.get("url", ""),
            "analysis": "Basic extraction - Vision Cortex not available",
            "valuation": "Unable to estimate",
            "market_trends": "Analysis unavailable",
            "processed_at": datetime.now().isoformat()
        }
        insights.append(insight)
    return insights

def save_clean_data_to_results(clean_data, pipeline_name="real_estate"):
    """Save clean/processed data to /results/compiled/"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{pipeline_name}_clean_{timestamp}.json"

    compiled_dir = os.path.join(RESULTS_DIR, "compiled")
    os.makedirs(compiled_dir, exist_ok=True)

    filepath = os.path.join(compiled_dir, filename)

    # Save as JSON
    with open(filepath, 'w') as f:
        json.dump(clean_data, f, indent=2)

    # Also save as CSV
    csv_filename = f"{pipeline_name}_clean_{timestamp}.json.csv"
    csv_filepath = os.path.join(compiled_dir, csv_filename)

    if clean_data:
        with open(csv_filepath, 'w', newline='') as csvfile:
            if isinstance(clean_data, list) and clean_data:
                fieldnames = clean_data[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(clean_data)
            elif isinstance(clean_data, dict):
                writer = csv.writer(csvfile)
                for key, value in clean_data.items():
                    writer.writerow([key, str(value)])

    logging.info(f"Saved clean data to {filepath} and {csv_filepath}")
    return filepath, csv_filepath

def update_manifest(unclean_files, clean_files, pipeline_name="real_estate"):
    """Update the compiled manifest with new files"""
    manifest_path = os.path.join(RESULTS_DIR, "compiled_manifest.json")

    # Load existing manifest
    if os.path.exists(manifest_path):
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
    else:
        manifest = []

    # Add new entries
    for file_path in unclean_files + clean_files:
        if file_path:
            entry = {
                "source": f"pipeline://{pipeline_name}",
                "compiled": file_path,
                "size": os.path.getsize(file_path) if os.path.exists(file_path) else 0,
                "timestamp": datetime.now().isoformat()
            }
            manifest.append(entry)

    # Save updated manifest
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)

    logging.info(f"Updated manifest with {len(unclean_files) + len(clean_files)} new entries")

def create_index_entry(clean_data, pipeline_name="real_estate"):
    """Create index entries for search (similar to manus_index.json)"""
    index_path = os.path.join(RESULTS_DIR, f"{pipeline_name}_index.json")

    # Load existing index
    if os.path.exists(index_path):
        with open(index_path, 'r') as f:
            index = json.load(f)
    else:
        index = []

    # Add new entries
    for i, item in enumerate(clean_data):
        entry = {
            "id": f"{pipeline_name}-{len(index) + i + 1}",
            "url": item.get("original_url", ""),
            "text": str(item.get("analysis", "")),
            "tokens": item.get("analysis", "").split(),  # Simple tokenization
            "token_count": len(item.get("analysis", "").split()),
            "processed_at": item.get("processed_at", ""),
            "pipeline": pipeline_name
        }
        index.append(entry)

    # Save updated index
    with open(index_path, 'w') as f:
        json.dump(index, f, indent=2)

    logging.info(f"Updated index with {len(clean_data)} new entries")

def run_real_estate_pipeline():
    logging.info("Starting Real Estate Intelligence Pipeline with /results integration")

    # Step 1: Submit crawl jobs
    if not submit_crawl_jobs(REAL_ESTATE_SOURCES):
        return

    # Step 2: Wait for crawling
    logging.info("Waiting for crawling to complete...")
    time.sleep(15)  # Allow time for crawling

    # Step 3: Collect results
    crawl_data = collect_crawl_results()
    logging.info(f"Collected {len(crawl_data)} crawl results")

    if not crawl_data:
        logging.info("No crawl data collected")
        return

    # Step 4: Save unclean data to /results
    unclean_files = save_unclean_data_to_results(crawl_data, "real_estate")

    # Step 5: Process with Vision Cortex
    clean_data = process_with_vision_cortex(crawl_data)

    # Step 6: Save clean data to /results
    clean_files = save_clean_data_to_results(clean_data, "real_estate")

    # Step 7: Update manifests and indexes
    update_manifest(unclean_files, clean_files, "real_estate")
    create_index_entry(clean_data, "real_estate")

    logging.info("Pipeline complete!")
    logging.info(f"Unclean data saved: {unclean_files}")
    logging.info(f"Clean data saved: {clean_files}")
    logging.info(f"Processed {len(clean_data)} items with AI insights")

if __name__ == "__main__":
    run_real_estate_pipeline()