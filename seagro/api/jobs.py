from flask import jsonify, request
from flask_login import login_required, current_user
from seagro.api import bp
from seagro.models.job import Job, JobApplication
from seagro import db

@bp.route('/jobs', methods=['GET'])
def get_jobs():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    jobs = Job.query.order_by(Job.created_at.desc())\
        .paginate(page=page, per_page=per_page)
    
    return jsonify({
        'jobs': [{
            'id': job.id,
            'title': job.title,
            'company': job.company,
            'location': job.location,
            'salary': job.salary,
            'requirements': job.requirements,
            'created_at': job.created_at.isoformat()
        } for job in jobs.items],
        'total': jobs.total,
        'pages': jobs.pages,
        'current_page': jobs.page
    })

@bp.route('/jobs', methods=['POST'])
@login_required
def create_job():
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No input data provided'}), 400
        
    job = Job(
        title=data['title'],
        company=data['company'],
        location=data.get('location'),
        description=data['description'],
        requirements=data.get('requirements'),
        salary=data.get('salary'),
        author_id=current_user.id
    )
    
    db.session.add(job)
    db.session.commit()
    
    return jsonify({
        'message': 'Job created successfully',
        'id': job.id
    }), 201

@bp.route('/jobs/<int:id>', methods=['GET'])
def get_job(id):
    job = Job.query.get_or_404(id)
    
    return jsonify({
        'id': job.id,
        'title': job.title,
        'company': job.company,
        'location': job.location,
        'description': job.description,
        'requirements': job.requirements,
        'salary': job.salary,
        'created_at': job.created_at.isoformat(),
        'author': {
            'id': job.author.id,
            'username': job.author.username
        }
    })

@bp.route('/jobs/<int:id>/apply', methods=['POST'])
@login_required
def apply_job(id):
    job = Job.query.get_or_404(id)
    
    existing_application = JobApplication.query.filter_by(
        job_id=job.id,
        applicant_id=current_user.id
    ).first()
    
    if existing_application:
        return jsonify({'error': 'You have already applied for this job'}), 400
        
    data = request.get_json()
    
    application = JobApplication(
        job_id=job.id,
        applicant_id=current_user.id,
        resume=data.get('resume'),
        cover_letter=data.get('cover_letter')
    )
    
    db.session.add(application)
    db.session.commit()
    
    return jsonify({
        'message': 'Application submitted successfully',
        'id': application.id
    }), 201

@bp.route('/jobs/<int:id>/applications', methods=['GET'])
@login_required
def get_job_applications(id):
    job = Job.query.get_or_404(id)
    
    # Only job author can view applications
    if job.author_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    applications = JobApplication.query.filter_by(job_id=id).all()
    
    return jsonify({
        'applications': [{
            'id': app.id,
            'job_id': app.job_id,
            'applicant_id': app.applicant_id,
            'cover_letter': app.cover_letter,
            'resume': app.resume,
            'status': app.status,
            'created_at': app.created_at.isoformat()
        } for app in applications]
    })
