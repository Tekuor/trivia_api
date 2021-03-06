import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category

class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.username = 'postgres'
        self.password = '123456'
        self.url = 'localhost:5432'
        self.database_path  = "postgres://{}:{}@{}/{}".format(self.username, self.password, self.url, self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

        self.new_question = {
            'question':'Which African country was formerly known as Abyssinia?',
            'answer':'Ethiopia',
            'difficulty':'3',
            'category':'3'
        }

        self.wrong_question = {
            'question':'Which African country was formerly known as Abyssinia?',
            'answer':'Ethiopia',
            'difficulty':'3',
            'category':[]
        }

        self.search = {
            'searchTerm':'African'
        }

        self.wrong_search = {
            'searchTerm':[]
        }

        self.quiz_data = {
            'previous_questions': [],
            'quiz_category': {'type': "Entertainment", 'id': '5'}
        }

        self.wrong_quiz_data = {
            'previous_questions': [],
            'quiz_category': '5'
        }
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_all_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['categories']))

    def test_retrieve_paginated_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
        self.assertTrue(len(data['categories']))

    def test_404_sent_requesting_beyond_valid_page(self):
        res = self.client().get('/questions?page=300')
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_create_new_question(self):
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['created'])
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])

    def test_422_if_create_question_unprocessible_entity(self):
        res = self.client().post('/questions', json=self.wrong_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessible entity')

    def test_search_questions(self):
        res = self.client().post('/questions/search', json=self.search)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])

    def test_422_if_search_questions_unprocessible_entity(self):
        res = self.client().post('/questions/search', json=self.wrong_search)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessible entity')

    def test_get_category_questions(self):
        res = self.client().get('/categories/3/questions')
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['current_category'])

    def test_404_if_category_cannot_be_found(self):
        res = self.client().get('/categories/500/questions')
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_get_quiz(self):
        res = self.client().post('/quizzes', json=self.quiz_data)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])

    def test_422_if_unprocessible_entity_quiz(self):
        res = self.client().post('/quizzes', json=self.wrong_quiz_data)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessible entity')

    def test_delete_question(self):
        res = self.client().delete('/questions/42')
        data = json.loads(res.data)

        question = Question.query.filter(Question.id == 42).one_or_none()
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
        self.assertEqual(data['deleted'], 42)
        self.assertEqual(question, None)

    def test_422_if_question_does_not_exist(self):
        res = self.client().delete('/questions/200')
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessible entity')

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()