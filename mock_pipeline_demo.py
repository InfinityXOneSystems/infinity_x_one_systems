import logging

import json
import os
import csv
from datetime import datetime
import sys

# Mock data for testing the pipeline without server
MOCK_CRAWL_DATA = [
    {
        "url": "https://www.realtor.com/realestateandhomes-search/San-Francisco_CA",
        "title": "San Francisco Real Estate",
        "content": "Beautiful homes in San Francisco with ocean views",
        "status_code": 200
    },
    {
        "url": "https://www.zillow.com/san-francisco-ca/",
        "title": "Zillow San Francisco",
        "content": "Find homes for sale in San Francisco CA",
        "status_code": 200
    },
    {
        "url": "https://www.redfin.com/city/17151/CA/San-Francisco",
        "title": "Redfin San Francisco",
        "content": "Real estate listings in San Francisco",
        "status_code": 200
    }
]

RESULTS_DIR = r"c:\AI\repos\mcp\results"

def save_unclean_data_to_results(data, pipeline_name="real_estate"):
    """Save unclean/raw data to /results/compiled/"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{pipeline_name}_unclean_{timestamp}.json"

    # Ensure compiled directory exists
    compiled_dir = os.path.join(RESULTS_DIR, "compiled")
    os.makedirs(compiled_dir, exist_ok=True)

    filepath = os.path.join(compiled_dir, filename)
    csv_filepath = os.path.join(compiled_dir, f"{filename}.csv")

    # Save as JSON
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)

    # Save as CSV
    if data:
        with open(csv_filepath, 'w', newline='') as csvfile:
            if isinstance(data, list) and data:
                fieldnames = data[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
    logging.info(f"Saved unclean data to {filepath}")

    logging.info(f"Saved unclean data to {filepath}")
    return filepath, csv_filepath

def mock_vision_cortex_processing(data):
    """Mock Vision Cortex processing"""
    logging.info("Mock processing with Vision Cortex...")
    insights = []

    for item in data:
        insight = {
            "original_url": item.get("url", ""),
            "processed_at": datetime.now().isoformat(),
            "agent_result": {
                "status_code": item.get("status_code", 200),
                "content_length": len(str(item.get("content", "")))
            },
            "analysis": "Mock Vision Cortex analyzed real estate data",
            "insights": {
                "data_quality": "high" if item.get("status_code") == 200 else "low",
                "content_length": len(str(item.get("content", ""))),
                "market_signals": "Extracted pricing, location, property details",
                "processing_confidence": 0.85
            }
        }
        insights.append(insight)

    return insights

def save_clean_data_to_results(data, pipeline_name="real_estate"):
    """Save clean/processed data to /results/compiled/"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{pipeline_name}_clean_{timestamp}.json"

    compiled_dir = os.path.join(RESULTS_DIR, "compiled")
    os.makedirs(compiled_dir, exist_ok=True)

    filepath = os.path.join(compiled_dir, filename)
    csv_filepath = os.path.join(compiled_dir, f"{filename}.csv")

    # Save as JSON
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)

    # Save as CSV
    if data:
        with open(csv_filepath, 'w', newline='') as csvfile:
            if isinstance(data, list) and data:
                fieldnames = data[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)

    logging.info(f"Saved clean data to {filepath}")
    return filepath, csv_filepath

def update_manifest(unclean_files, clean_files, pipeline_name="real_estate"):
    """Update the compiled manifest"""
    manifest_path = os.path.join(RESULTS_DIR, "compiled_manifest.json")

    if os.path.exists(manifest_path):
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
    else:
        manifest = []

    for file_path in list(unclean_files) + list(clean_files):
        if file_path and os.path.exists(file_path):
            entry = {
                "source": f"pipeline://{pipeline_name}",
                "compiled": file_path,
                "size": os.path.getsize(file_path),
                "timestamp": datetime.now().isoformat()
            }
            manifest.append(entry)

    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)

    logging.info(f"Updated manifest with new entries")

def create_index(clean_data, pipeline_name="real_estate"):
    """Create search index"""
    index_path = os.path.join(RESULTS_DIR, f"{pipeline_name}_index.json")

    if os.path.exists(index_path):
        with open(index_path, 'r') as f:
            index = json.load(f)
    else:
        index = []

    for i, item in enumerate(clean_data):
        entry = {
            "id": f"{pipeline_name}-{len(index) + i + 1}",
            "url": item.get("original_url", ""),
            "text": str(item.get("analysis", "")),
            "tokens": str(item.get("analysis", "")).split(),
            "token_count": len(str(item.get("analysis", "")).split()),
            "processed_at": item.get("processed_at", ""),
            "pipeline": pipeline_name
        }
        index.append(entry)

    with open(index_path, 'w') as f:
        json.dump(index, f, indent=2)

    logging.info(f"Updated index with {len(clean_data)} entries")

def run_mock_pipeline():
    """Run the complete pipeline with mock data"""
    logging.info("Starting Mock Real Estate Intelligence Pipeline with /results integration")

    # Simulate crawl data
    crawl_data = MOCK_CRAWL_DATA
    logging.info(f"Mock collected {len(crawl_data)} results")

    # Save unclean data
    unclean_files = save_unclean_data_to_results(crawl_data, "real_estate")

    # Process with mock Vision Cortex
    clean_data = mock_vision_cortex_processing(crawl_data)

    # Save clean data
    clean_files = save_clean_data_to_results(clean_data, "real_estate")

    # Update manifests and indexes
    update_manifest(unclean_files, clean_files, "real_estate")
    create_index(clean_data, "real_estate")

    logging.info("Mock Pipeline complete!")
    logging.info(f"  Unclean: {unclean_files}")
    logging.info(f"  Clean: {clean_files}")
    logging.info(f"  Processed {len(clean_data)} items")

    # Show what was created
    logging.info("\nFiles created in /results/compiled/:")
    compiled_dir = os.path.join(RESULTS_DIR, "compiled")
    if os.path.exists(compiled_dir):
        files = [f for f in os.listdir(compiled_dir) if "real_estate" in f and f.endswith((".json", ".csv"))]
        for file in sorted(files):
            logging.info(f"  - {file}")

if __name__ == "__main__":
    run_mock_pipeline()