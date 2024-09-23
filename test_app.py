import unittest
from app import app, db
from models import User, Feedback

class FlaskAppTests(unittest.TestCase):

    def setUp(self):
        """Set up the test client and initialize the database."""
        self.client = app.test_client()
        app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///flask-feedback-test'
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for tests

        with app.app_context():
            db.create_all()

            # Add a test user
            user = User.register("testuser", "password", "Test", "User", "test@test.com")
            db.session.add(user)
            db.session.commit()


    def tearDown(self):
        """Clean up the database after each test."""
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_register(self):
        """Test registering a new user."""
        with self.client as client:
            data = {
                "username": "newuser",
                "password": "password",
                "first_name": "New",
                "last_name": "User",
                "email": "newuser@test.com"
            }
            resp = client.post("/register", data=data, follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn(b"newuser", resp.data)

    def test_login(self):
        """Test logging in."""
        with self.client as client:
            data = {"username": "testuser", "password": "password"}
            resp = client.post("/login", data=data, follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn(b"testuser", resp.data)

    def test_add_feedback(self):
        """Test adding feedback"""

        # First, log in the user
        with self.client as c:
            # Log in the test user
            resp = c.post('/login', data={
                'username': 'testuser',
                'password': 'password'
            }, follow_redirects=True)

            # Now try to add feedback using the correct route
            resp = c.post('/users/testuser/feedback/new', data={
                'title': 'Test Feedback',
                'content': 'This is a test feedback.'
            }, follow_redirects=True)

            # Ensure the feedback was added
            self.assertEqual(resp.status_code, 200)
            self.assertIn(b'Test Feedback', resp.data)
            self.assertIn(b'Test', resp.data)  # Ensure feedback username is displayed


if __name__ == "__main__":
    unittest.main()
