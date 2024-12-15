from datetime import datetime, timedelta, timezone
from seagro import create_app, db
from seagro.models.user import User
from seagro.models.job import Job, JobApplication
from seagro.models.course import Course, Module, Lesson, Enrollment

def seed_data():
    # Drop all tables
    db.drop_all()
    # Create all tables
    db.create_all()
    
    # Create test users
    users = [
        {
            'username': 'john_doe',
            'email': 'john@example.com',
            'password': 'password123',
            'first_name': 'John',
            'last_name': 'Doe',
            'is_admin': True
        },
        {
            'username': 'jane_smith',
            'email': 'jane@example.com',
            'password': 'password123',
            'first_name': 'Jane',
            'last_name': 'Smith'
        }
    ]
    
    created_users = []
    for user_data in users:
        user = User(
            username=user_data['username'],
            email=user_data['email'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            is_admin=user_data.get('is_admin', False)
        )
        user.set_password(user_data['password'])
        db.session.add(user)
        created_users.append(user)
    
    db.session.commit()
    
    # Create test jobs
    jobs = [
        {
            'title': 'Senior Python Developer',
            'company': 'Tech Corp',
            'location': 'San Francisco, CA',
            'description': 'Looking for an experienced Python developer...',
            'requirements': '5+ years of Python experience\nExperience with Flask/Django',
            'salary_range': '$120k - $150k',
            'job_type': 'full-time',
            'deadline': datetime.now(timezone.utc) + timedelta(days=30),
            'user_id': created_users[0].id
        },
        {
            'title': 'Frontend Developer',
            'company': 'Web Solutions',
            'location': 'Remote',
            'description': 'Join our team as a frontend developer...',
            'requirements': '3+ years of React experience\nStrong CSS skills',
            'salary_range': '$90k - $120k',
            'job_type': 'full-time',
            'deadline': datetime.now(timezone.utc) + timedelta(days=15),
            'user_id': created_users[0].id
        }
    ]
    
    created_jobs = []
    for job_data in jobs:
        job = Job(**job_data)
        db.session.add(job)
        created_jobs.append(job)
    
    db.session.commit()
    
    # Create test job applications
    application = JobApplication(
        job_id=created_jobs[0].id,
        user_id=created_users[1].id,
        resume_url='https://example.com/resume.pdf',
        cover_letter='I am very interested in this position...',
        status='pending'
    )
    db.session.add(application)
    db.session.commit()
    
    # Create test courses
    courses = [
        {
            'title': 'Python for Beginners',
            'description': 'Learn Python from scratch',
            'instructor_id': created_users[0].id,
            'price': 49.99,
            'duration': '6 weeks',
            'level': 'beginner',
            'category': 'Programming',
            'tags': ['python', 'programming', 'web development'],
            'thumbnail_url': 'https://example.com/python-course.jpg',
            'prerequisites': 'No prior programming experience needed',
            'what_youll_learn': [
                'Python syntax and basic concepts',
                'Object-oriented programming',
                'Web development with Flask',
                'Database integration'
            ]
        },
        {
            'title': 'Advanced Web Development',
            'description': 'Master modern web development',
            'instructor_id': created_users[0].id,
            'price': 79.99,
            'duration': '8 weeks',
            'level': 'advanced',
            'category': 'Web Development',
            'tags': ['javascript', 'react', 'node.js'],
            'thumbnail_url': 'https://example.com/webdev-course.jpg',
            'prerequisites': 'Basic understanding of HTML, CSS, and JavaScript',
            'what_youll_learn': [
                'Modern JavaScript features',
                'React and Redux',
                'Node.js and Express',
                'MongoDB integration'
            ]
        }
    ]
    
    created_courses = []
    for course_data in courses:
        course = Course(**course_data)
        db.session.add(course)
        created_courses.append(course)
    
    db.session.commit()
    
    # Create modules and lessons for the first course
    modules = [
        {
            'title': 'Introduction to Python',
            'description': 'Basic Python concepts',
            'order': 1,
            'course_id': created_courses[0].id,
            'lessons': [
                {
                    'title': 'Variables and Data Types',
                    'content': 'Learn about Python variables...',
                    'order': 1
                },
                {
                    'title': 'Control Flow',
                    'content': 'Learn about if statements and loops...',
                    'order': 2
                }
            ]
        },
        {
            'title': 'Functions and Classes',
            'description': 'Object-oriented programming',
            'order': 2,
            'course_id': created_courses[0].id,
            'lessons': [
                {
                    'title': 'Functions',
                    'content': 'Learn about Python functions...',
                    'order': 1
                },
                {
                    'title': 'Classes',
                    'content': 'Learn about Python classes...',
                    'order': 2
                }
            ]
        }
    ]
    
    for module_data in modules:
        lessons_data = module_data.pop('lessons')
        module = Module(**module_data)
        db.session.add(module)
        db.session.commit()
        
        for lesson_data in lessons_data:
            lesson = Lesson(**lesson_data, module_id=module.id)
            db.session.add(lesson)
    
    # Create test enrollment
    enrollment = Enrollment(
        user_id=created_users[1].id,
        course_id=created_courses[0].id
    )
    db.session.add(enrollment)
    
    db.session.commit()
    print("Mock data has been added successfully!")

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        seed_data()
