#!/usr/bin/env python3
"""
Actuary List Job Scraper

This script scrapes job listings from https://www.actuarylist.com
and outputs them as JSON for integration with the job board application.
"""

import json
import time
import sys
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

class ActuaryListScraper:
    def __init__(self, headless=True, max_jobs=50):
        self.headless = headless
        self.max_jobs = max_jobs
        self.driver = None
        self.jobs = []
        
    def setup_driver(self):
        """Setup Chrome WebDriver with appropriate options"""
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.implicitly_wait(10)
        
    def scrape_jobs(self):
        """Main scraping function"""
        try:
            print("Setting up Chrome driver...")
            self.setup_driver()
            
            print("Navigating to Actuary List...")
            self.driver.get("https://www.actuarylist.com/jobs")
            
            # Wait for page to load
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, "job-listing"))
            )
            
            print("Page loaded, starting to scrape jobs...")
            
            # Try to load more jobs if there's a "Load More" button
            self._load_more_jobs()
            
            # Get all job listings
            job_elements = self.driver.find_elements(By.CLASS_NAME, "job-listing")
            print(f"Found {len(job_elements)} job listings")
            
            for i, job_element in enumerate(job_elements[:self.max_jobs]):
                try:
                    job_data = self._extract_job_data(job_element)
                    if job_data:
                        self.jobs.append(job_data)
                        print(f"Scraped job {i+1}: {job_data['title']} at {job_data['company']}")
                except Exception as e:
                    print(f"Error scraping job {i+1}: {str(e)}")
                    continue
                    
            print(f"Successfully scraped {len(self.jobs)} jobs")
            return self.jobs
            
        except Exception as e:
            print(f"Error during scraping: {str(e)}")
            return []
        finally:
            if self.driver:
                self.driver.quit()
                
    def _load_more_jobs(self):
        """Try to load more jobs by clicking load more button or scrolling"""
        try:
            # Try to find and click "Load More" button
            load_more_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Load More') or contains(text(), 'Show More')]")
            
            for _ in range(3):  # Try up to 3 times
                if load_more_buttons:
                    button = load_more_buttons[0]
                    if button.is_displayed() and button.is_enabled():
                        self.driver.execute_script("arguments[0].click();", button)
                        time.sleep(2)
                        load_more_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Load More') or contains(text(), 'Show More')]")
                    else:
                        break
                else:
                    # Try scrolling to load more content
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(2)
                    break
                    
        except Exception as e:
            print(f"Could not load more jobs: {str(e)}")
            
    def _extract_job_data(self, job_element):
        """Extract job data from a job listing element"""
        try:
            # Get the HTML content for BeautifulSoup parsing
            job_html = job_element.get_attribute('outerHTML')
            soup = BeautifulSoup(job_html, 'html.parser')
            
            # Extract job title
            title_element = job_element.find_element(By.CSS_SELECTOR, "h3, .job-title, [class*='title'], a[href*='/job/']")
            title = title_element.text.strip() if title_element else "Unknown Title"
            
            # Extract company name
            company_selectors = [
                ".company-name", ".employer", "[class*='company']", 
                "h4", ".job-company", "[data-company]"
            ]
            company = "Unknown Company"
            for selector in company_selectors:
                try:
                    company_element = job_element.find_element(By.CSS_SELECTOR, selector)
                    if company_element and company_element.text.strip():
                        company = company_element.text.strip()
                        break
                except:
                    continue
                    
            # Extract location
            location_selectors = [
                ".location", ".job-location", "[class*='location']",
                "[data-location]", ".city", ".state"
            ]
            location = "Remote"
            for selector in location_selectors:
                try:
                    location_element = job_element.find_element(By.CSS_SELECTOR, selector)
                    if location_element and location_element.text.strip():
                        location = location_element.text.strip()
                        break
                except:
                    continue
                    
            # Extract posting date
            date_selectors = [
                ".date", ".posted-date", "[class*='date']", ".time",
                "[data-date]", ".posted", "time"
            ]
            posting_date = datetime.now().isoformat()
            for selector in date_selectors:
                try:
                    date_element = job_element.find_element(By.CSS_SELECTOR, selector)
                    if date_element and date_element.text.strip():
                        date_text = date_element.text.strip()
                        # Keep original date text for now, could parse it later
                        posting_date = datetime.now().isoformat()
                        break
                except:
                    continue
                    
            # Extract job type (default to Full-time)
            job_type_selectors = [
                ".job-type", ".employment-type", "[class*='type']",
                ".full-time", ".part-time", ".contract", ".intern"
            ]
            job_type = "Full-time"
            for selector in job_type_selectors:
                try:
                    type_element = job_element.find_element(By.CSS_SELECTOR, selector)
                    if type_element and type_element.text.strip():
                        type_text = type_element.text.strip().lower()
                        if 'part' in type_text:
                            job_type = "Part-time"
                        elif 'contract' in type_text:
                            job_type = "Contract"
                        elif 'intern' in type_text:
                            job_type = "Internship"
                        break
                except:
                    continue
                    
            # Extract tags/skills
            tags = []
            tag_selectors = [
                ".skills", ".tags", ".keywords", "[class*='skill']",
                ".badge", ".chip", ".tag", "[class*='tag']"
            ]
            
            for selector in tag_selectors:
                try:
                    tag_elements = job_element.find_elements(By.CSS_SELECTOR, selector)
                    for tag_element in tag_elements:
                        tag_text = tag_element.text.strip()
                        if tag_text and len(tag_text) < 50:  # Reasonable tag length
                            tags.append(tag_text)
                except:
                    continue
                    
            # Default tags for actuarial jobs
            if not tags:
                tags = ["Actuarial", "Insurance", "Risk Management"]
            else:
                tags = list(set(tags[:5]))  # Limit to 5 unique tags
                
            # Create job data object
            job_data = {
                "id": f"scraped_{int(time.time())}_{len(self.jobs)}",
                "title": title,
                "company": company,
                "location": location,
                "job_type": job_type,
                "tags": tags,
                "posting_date": posting_date,
                "description": f"Actuarial position at {company} in {location}. This job was scraped from ActuaryList.com."
            }
            
            return job_data
            
        except Exception as e:
            print(f"Error extracting job data: {str(e)}")
            return None
            
    def save_to_json(self, filename="scraped_jobs.json"):
        """Save scraped jobs to JSON file"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.jobs, f, indent=2, ensure_ascii=False)
            print(f"Saved {len(self.jobs)} jobs to {filename}")
        except Exception as e:
            print(f"Error saving to JSON: {str(e)}")
            
def main():
    """Main function to run the scraper"""
    try:
        # Parse command line arguments
        max_jobs = 50
        headless = True
        
        if len(sys.argv) > 1:
            try:
                max_jobs = int(sys.argv[1])
            except ValueError:
                print("Invalid max_jobs argument, using default: 50")
                
        if len(sys.argv) > 2:
            headless = sys.argv[2].lower() != 'false'
            
        print(f"Starting scraper with max_jobs={max_jobs}, headless={headless}")
        
        # Create and run scraper
        scraper = ActuaryListScraper(headless=headless, max_jobs=max_jobs)
        jobs = scraper.scrape_jobs()
        
        if jobs:
            # Save to JSON file
            scraper.save_to_json("scraped_jobs.json")
            
            # Output JSON to stdout for API integration
            print("\n=== SCRAPED JOBS JSON ===")
            print(json.dumps(jobs, indent=2))
            print("=== END SCRAPED JOBS ===")
        else:
            print("No jobs were scraped")
            
    except KeyboardInterrupt:
        print("\nScraping interrupted by user")
    except Exception as e:
        print(f"Error in main: {str(e)}")
        
if __name__ == "__main__":
    main()
