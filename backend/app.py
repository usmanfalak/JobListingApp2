
import os
import json
import subprocess
import sys
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from models import db
from routes import routes

# Load environment variables from .env file
load_dotenv()  # ✅ This must be called BEFORE os.getenv

# In-memory storage for jobs (in production, use a real database)
jobs_storage = []
job_counter = 1

# Sample initial jobs
initial_jobs = [
    {
        "id": "1",
        "title": "Senior React Developer",
        "company": "TechCorp Solutions",
        "location": "Lahore",
        "job_type": "Full-time",
        "tags": ["React", "TypeScript", "Node.js"],
        "posting_date": "2024-01-15T10:00:00Z",
        "description": "We are looking for an experienced React developer to join our team."
    },
    {
        "id": "2",
        "title": "UI/UX Designer",
        "company": "Design Studio",
        "location": "Remote",
        "job_type": "Part-time",
        "tags": ["Figma", "Adobe XD", "Prototyping"],
        "posting_date": "2024-01-14T09:30:00Z",
        "description": "Create beautiful and intuitive user interfaces for web and mobile applications."
    }
]

jobs_storage.extend(initial_jobs)
job_counter = len(initial_jobs) + 1

def create_app():
    app = Flask(__name__)

    # Database configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///databse.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'fallbacksecret')

    # Enable CORS
    CORS(app)
    
    # Initialize database
    db.init_app(app)

    # Register existing routes blueprint
    app.register_blueprint(routes)

    # ✅ Create tables safely using app context
    with app.app_context():
        db.create_all()

    # Add new API endpoints for job management and scraping
    @app.route('/jobs', methods=['GET'])
    def get_jobs():
        """Get all jobs with optional filtering and sorting"""
        try:
            filtered_jobs = jobs_storage.copy()
            
            # Apply filters
            title_filter = request.args.get('title')
            if title_filter:
                filtered_jobs = [job for job in filtered_jobs 
                               if title_filter.lower() in job['title'].lower()]
            
            company_filter = request.args.get('company')
            if company_filter:
                filtered_jobs = [job for job in filtered_jobs 
                               if company_filter.lower() in job['company'].lower()]
            
            location_filter = request.args.get('location')
            if location_filter:
                filtered_jobs = [job for job in filtered_jobs 
                               if job['location'] == location_filter]
            
            job_type_filter = request.args.get('job_type')
            if job_type_filter:
                filtered_jobs = [job for job in filtered_jobs 
                               if job['job_type'] == job_type_filter]
            
            tags_filter = request.args.get('tags')
            if tags_filter:
                filtered_jobs = [job for job in filtered_jobs 
                               if any(tags_filter.lower() in tag.lower() for tag in job['tags'])]
            
            # Apply sorting
            sort_param = request.args.get('sort', 'posting_date_desc')
            if sort_param == 'posting_date_asc':
                filtered_jobs.sort(key=lambda x: x['posting_date'])
            else:
                filtered_jobs.sort(key=lambda x: x['posting_date'], reverse=True)
            
            return jsonify(filtered_jobs)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/jobs/<job_id>', methods=['GET'])
    def get_job(job_id):
        """Get a single job by ID"""
        try:
            job = next((job for job in jobs_storage if job['id'] == job_id), None)
            if job:
                return jsonify(job)
            else:
                return jsonify({'error': 'Job not found'}), 404
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/jobs', methods=['POST'])
    def create_job():
        """Create a new job"""
        try:
            global job_counter
            data = request.get_json()
            
            # Validate required fields
            required_fields = ['title', 'company', 'location']
            for field in required_fields:
                if not data.get(field):
                    return jsonify({'error': f'{field} is required'}), 400
            
            # Create new job
            new_job = {
                'id': str(job_counter),
                'title': data['title'],
                'company': data['company'],
                'location': data['location'],
                'job_type': data.get('job_type', 'Full-time'),
                'tags': data.get('tags', []),
                'posting_date': datetime.now().isoformat(),
                'description': data.get('description', '')
            }
            
            jobs_storage.append(new_job)
            job_counter += 1
            
            return jsonify(new_job), 201
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/jobs/<job_id>', methods=['PUT'])
    def update_job(job_id):
        """Update an existing job"""
        try:
            job = next((job for job in jobs_storage if job['id'] == job_id), None)
            if not job:
                return jsonify({'error': 'Job not found'}), 404
            
            data = request.get_json()
            
            # Update job fields
            job['title'] = data.get('title', job['title'])
            job['company'] = data.get('company', job['company'])
            job['location'] = data.get('location', job['location'])
            job['job_type'] = data.get('job_type', job['job_type'])
            job['tags'] = data.get('tags', job['tags'])
            job['description'] = data.get('description', job['description'])
            
            return jsonify(job)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/jobs/<job_id>', methods=['DELETE'])
    def delete_job(job_id):
        """Delete a job"""
        try:
            global jobs_storage
            job = next((job for job in jobs_storage if job['id'] == job_id), None)
            if not job:
                return jsonify({'error': 'Job not found'}), 404
            
            jobs_storage = [job for job in jobs_storage if job['id'] != job_id]
            return '', 204
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/scrape-jobs', methods=['POST'])
    def scrape_jobs():
        """Scrape jobs from ActuaryList using Selenium"""
        try:
            data = request.get_json() or {}
            max_jobs = data.get('max_jobs', 20)
            
            # Path to the scraper script
            scraper_path = os.path.join(os.path.dirname(__file__), '..', 'scraper', 'run_scraper.py')
            
            # Run the scraper
            result = subprocess.run(
                [sys.executable, scraper_path, str(max_jobs)],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                # Parse the JSON output from the scraper
                scraper_output = json.loads(result.stdout)
                
                if scraper_output['success']:
                    # Add scraped jobs to storage
                    global job_counter
                    scraped_jobs = scraper_output['jobs']
                    
                    for job in scraped_jobs:
                        job['id'] = str(job_counter)
                        jobs_storage.append(job)
                        job_counter += 1
                    
                    return jsonify({
                        'success': True,
                        'message': f'Successfully scraped {len(scraped_jobs)} jobs',
                        'jobs_added': len(scraped_jobs),
                        'jobs': scraped_jobs
                    })
                else:
                    return jsonify({
                        'success': False,
                        'error': scraper_output['error']
                    }), 500
            else:
                return jsonify({
                    'success': False,
                    'error': f'Scraper failed: {result.stderr}'
                }), 500
                
        except subprocess.TimeoutExpired:
            return jsonify({
                'success': False,
                'error': 'Scraping timeout - the process took too long'
            }), 500
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint"""
        return jsonify({
            'status': 'healthy',~
            'jobs_count': len(jobs_storage),
            'timestamp': datetime.now().isoformat()
        })

    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    print(f"Starting Flask server on port {port}")
    print(f"Debug mode: {debug}")
    print(f"Initial jobs loaded: {len(jobs_storage)}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)














# from flask import Flask
# from flask_cors import CORS
# from dotenv import load_dotenv
# from models import db
# from routes import routes
# import os

# # Load environment variables from .env file
# load_dotenv()  # ✅ This must be called BEFORE os.getenv

# def create_app():
#     app = Flask(__name__)

#     app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///databse.db')
#     app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#     app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'fallbacksecret')

#     CORS(app)
#     db.init_app(app)

#     app.register_blueprint(routes)

#     # ✅ Create tables safely using app context
#     with app.app_context():
#         db.create_all()

#     return app


# if __name__ == "__main__":
#     app = create_app()
#     app.run(debug=True)
