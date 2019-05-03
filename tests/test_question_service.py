
import unittest
from unittest.mock import patch
import os

from services import QuestionService

class QuestionServiceTestCase(unittest.TestCase):
    def setUp(self):
        self.session_id = 'mysessionid'
        self.questions = [
            {
                'text': 'question1',
                'context': 'question1',
                'correct_response': 'response1, response2',
                'description': 'Description1'
            },
            {
                'text': 'question2',
                'context': 'question2',
                'correct_response': 'response3, response4',
                'description': 'Description2'
            }
        ]
        self.service = QuestionService(self.session_id, self.questions)

    def test_get_question_valid_result_empty_history(self):
        history_questions = []

        question = self.service.get_question(history_questions)

        self.assertIn(question, self.questions)

    def test_get_question_valid_result_one_in_history(self):
        history_questions = ['question1']

        question = self.service.get_question(history_questions)

        self.assertEqual(question['context'], 'question2')

    def test_get_response_to_question_valid_answer_correct_response(self):
        text = 'response3'
        question_object = self.questions[1]
        expected_response = self.service.CORRECT_QUESTION_FORMAT.format(
            question_object['correct_response'],
            question_object['description'],
        )

        response = self.service.get_response_to_question(text, question_object)

        self.assertEqual(response, expected_response)

    def test_get_response_to_question_valid_answer_incorrect_response(self):
        text = 'response_bad'
        question_object = self.questions[1]
        expected_response = self.service.INCORRECT_QUESTION_FORMAT.format(
            question_object['correct_response'],
        )

        response = self.service.get_response_to_question(text, question_object)

        self.assertEqual(response, expected_response)

    def test_get_response_to_question_invalid_text_incorrect_response(self):
        text = 'bad'
        question_object = self.questions[1]
        expected_response = self.service.INCORRECT_QUESTION_FORMAT.format(
            question_object['correct_response'],
        )

        response = self.service.get_response_to_question(text, question_object)

        self.assertEqual(response, expected_response)

    def test_is_valid_answer_text_length_invalid(self):
        text = 'bad'
        correct_response = 'response3, response4'

        is_valid = self.service.is_valid_answer(text, correct_response)

        self.assertFalse(is_valid)

    def test_is_valid_answer_text_incorrect(self):
        text = 'response_bad'
        correct_response = 'response3, response4'

        is_valid = self.service.is_valid_answer(text, correct_response)

        self.assertFalse(is_valid)

    def test_is_valid_answer_text_correct(self):
        text = 'response3'
        correct_response = 'response3, response4'

        is_valid = self.service.is_valid_answer(text, correct_response)

        self.assertTrue(is_valid)
