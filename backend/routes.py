from flask import Blueprint, request, jsonify
from models import db, Job
from sqlalchemy import desc

routes = Blueprint('routes', __name__)

# ------ GET ALL JOBS (with optional filters) ------
@routes.route("/jobs", methods=["GET"])
def get_jobs():
    query = Job.query

    # Filtering
    job_type = request.args.get("job_type")
    location = request.args.get("location")
    tag = request.args.get("tag")
    sort = request.args.get("sort", "posting_date_desc")

    if job_type:
        query = query.filter(Job.job_type.ilike(f"%{job_type}%"))
    if location:
        query = query.filter(Job.location.ilike(f"%{location}%"))
    if tag:
        query = query.filter(Job.tags.ilike(f"%{tag}%"))

    # Sorting
    if sort == "posting_date_desc":
        query = query.order_by(desc(Job.posting_date))
    elif sort == "posting_date_asc":
        query = query.order_by(Job.posting_date)

    jobs = query.all()
    return jsonify([job.to_dict() for job in jobs]), 200

# ----------------- GET SINGLE JOB -----------------
@routes.route("/jobs/<int:id>", methods=["GET"])
def get_job(id):
    job = Job.query.get(id)
    if job:
        return jsonify(job.to_dict()), 200
    return jsonify({"error": "Job not found"}), 404

# ----------------- CREATE A NEW JOB -----------------
@routes.route("/jobs", methods=["POST"])
def create_job():
    data = request.get_json()
    required = ["title", "company", "location", "job_type"]

    if not all(field in data for field in required):
        return jsonify({"error": "Missing required fields"}), 400

    new_job = Job(
        title=data["title"],
        company=data["company"],
        location=data["location"],
        job_type=data["job_type"],
        posting_date=data.get("posting_date"),
        tags=",".join(data.get("tags", []))
    )

    db.session.add(new_job)
    db.session.commit()
    return jsonify(new_job.to_dict()), 201

# ----------------- UPDATE JOB -----------------
@routes.route("/jobs/<int:id>", methods=["PUT", "PATCH"])
def update_job(id):
    job = Job.query.get(id)
    if not job:
        return jsonify({"error": "Job not found"}), 404

    data = request.get_json()

    job.title = data.get("title", job.title)
    job.company = data.get("company", job.company)
    job.location = data.get("location", job.location)
    job.job_type = data.get("job_type", job.job_type)
    job.tags = ",".join(data.get("tags", job.tags.split(",")))

    db.session.commit()
    return jsonify(job.to_dict()), 200

# ----------------- DELETE JOB -----------------
@routes.route("/jobs/<int:id>", methods=["DELETE"])
def delete_job(id):
    job = Job.query.get(id)
    if not job:
        return jsonify({"error": "Job not found"}), 404

    db.session.delete(job)
    db.session.commit()
    return jsonify({"message": "Job deleted"}), 204
