from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from seagro import db
from seagro.models.course import Course, CourseEnrollment

bp = Blueprint('courses', __name__)

@bp.route('/courses', methods=['GET'])
def get_courses():
    courses = Course.query.all()
    return jsonify([{
        'id': c.id,
        'title': c.title,
        'description': c.description
    } for c in courses])

@bp.route('/courses/<int:id>', methods=['GET'])
def get_course(id):
    course = Course.query.get_or_404(id)
    return jsonify({
        'id': course.id,
        'title': course.title,
        'description': course.description,
        'content': course.content
    })

@bp.route('/courses/<int:id>/enroll', methods=['POST'])
@login_required
def enroll_course(id):
    course = Course.query.get_or_404(id)
    
    # Check if already enrolled
    existing = CourseEnrollment.query.filter_by(
        user_id=current_user.id,
        course_id=course.id
    ).first()
    
    if existing:
        return jsonify({'message': 'Already enrolled'}), 400
        
    enrollment = CourseEnrollment(user_id=current_user.id, course_id=course.id)
    db.session.add(enrollment)
    db.session.commit()
    
    return jsonify({'message': 'Enrolled successfully'})

@bp.route('/courses/<int:id>/progress', methods=['POST'])
@login_required
def update_progress(id):
    progress = request.json.get('progress')
    if not progress or not isinstance(progress, int) or progress < 0 or progress > 100:
        return jsonify({'error': 'Invalid progress value'}), 400
        
    enrollment = CourseEnrollment.query.filter_by(
        user_id=current_user.id,
        course_id=id
    ).first_or_404()
    
    enrollment.progress = progress
    db.session.commit()
    
    return jsonify({'message': 'Progress updated'})