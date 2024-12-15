import unittest
from seagro import create_app, db
from seagro.models.user import User
from seagro.models.job import Job, JobApplication
import flask_login

class TestAPI(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        
        # Create a test user
        self.user = User(
            username='test_user',
            email='test@example.com',
            first_name='Test',
            last_name='User'
        )
        self.user.set_password('password123')
        db.session.add(self.user)
        db.session.commit()
        
        # Create a test job
        self.job = Job(
            title='Test Job',
            company='Test Company',
            description='Test Description',
            location='Test Location',
            salary='$100k-$120k',
            requirements='Test Requirements',
            author_id=self.user.id
        )
        db.session.add(self.job)
        db.session.commit()
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def login(self):
        with self.client.session_transaction() as session:
            session['_user_id'] = str(self.user.id)
            session['_fresh'] = True
        return self.client.post('/auth/login', json={
            'email': 'test@example.com',
            'password': 'password123'
        })
    
    def test_get_jobs(self):
        response = self.client.get('/api/jobs')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('jobs', data)
        self.assertIn('total', data)
        self.assertEqual(len(data['jobs']), 1)
        self.assertEqual(data['total'], 1)
    
    def test_create_job(self):
        # First, login
        login_response = self.login()
        self.assertEqual(login_response.status_code, 200)
        
        # Create a job
        job_data = {
            'title': 'New Test Job',
            'company': 'New Test Company',
            'description': 'New Test Description',
            'location': 'New Test Location',
            'salary': '$80k-$100k',
            'requirements': 'New Test Requirements'
        }
        response = self.client.post('/api/jobs', json=job_data)
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertIn('id', data)
        
        # Verify job was created
        response = self.client.get(f'/api/jobs/{data["id"]}')
        self.assertEqual(response.status_code, 200)
        job = response.get_json()
        self.assertEqual(job['title'], job_data['title'])
    
    def test_apply_for_job(self):
        # First, login
        login_response = self.login()
        self.assertEqual(login_response.status_code, 200)
        
        # Apply for job
        application_data = {
            'cover_letter': 'Test Cover Letter',
            'resume': 'test_resume.pdf'
        }
        response = self.client.post(f'/api/jobs/{self.job.id}/apply', json=application_data)
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertIn('id', data)
        
        # Verify application was created
        with self.app.app_context():
            application = JobApplication.query.get(data['id'])
            self.assertIsNotNone(application)
            self.assertEqual(application.job_id, self.job.id)
            self.assertEqual(application.applicant_id, self.user.id)
    
    def test_get_job_applications(self):
        # First, login
        login_response = self.login()
        self.assertEqual(login_response.status_code, 200)
        
        # Create an application
        application = JobApplication(
            job_id=self.job.id,
            applicant_id=self.user.id,
            cover_letter='Test Cover Letter',
            resume='test_resume.pdf'
        )
        db.session.add(application)
        db.session.commit()
        
        # Get applications for job
        response = self.client.get(f'/api/jobs/{self.job.id}/applications')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('applications', data)
        self.assertEqual(len(data['applications']), 1)
        self.assertEqual(data['applications'][0]['job_id'], self.job.id)

    def test_get_courses(self):
        response = self.client.get('/api/courses')
        self.assertEqual(response.status_code, 200)
        
    def test_enroll_course(self):
        self.login()
        response = self.client.post(f'/api/courses/{self.course.id}/enroll')
        self.assertEqual(response.status_code, 200)
        
    def test_update_progress(self):
        self.login()
        self.client.post(f'/api/courses/{self.course.id}/enroll')
        response = self.client.post(
            f'/api/courses/{self.course.id}/progress',
            json={'progress': 50}
        )
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
