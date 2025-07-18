#!/usr/bin/env python3
"""
Simple script to run the Actuary List scraper and return JSON output
"""

import json
import sys
from actuarylist_scraper import ActuaryListScraper

def run_scraper(max_jobs=20):
    """Run the scraper and return jobs as JSON"""
    try:
        scraper = ActuaryListScraper(headless=True, max_jobs=max_jobs)
        jobs = scraper.scrape_jobs()
        return {
            "success": True,
            "jobs": jobs,
            "count": len(jobs)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "jobs": [],
            "count": 0
        }

if __name__ == "__main__":
    max_jobs = 20
    if len(sys.argv) > 1:
        try:
            max_jobs = int(sys.argv[1])
        except ValueError:
            pass
    
    result = run_scraper(max_jobs)
    print(json.dumps(result))
