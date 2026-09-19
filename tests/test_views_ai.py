"""
Integration tests for AI-powered views:
- Module 18: AI BMI Calculator (GET form + POST -> AI report + DB record)
- Module 22: NLP Chatbot page and AJAX API endpoint
"""
import json

import pytest

from myapp.models import BMIRecord

pytestmark = pytest.mark.django_db


class TestAIBMICalculatorView:
    def test_get_renders_form_without_result(self, client):
        response = client.get('/bmi_calculator')
        assert response.status_code == 200
        assert response.context['result'] is None
        assert response.context['history'].count() == 0

    def test_post_calculates_ai_report(self, client):
        response = client.post('/bmi_calculator', {
            'name': 'Aarav Sharma',
            'height': '175',
            'weight': '70',
            'age': '28',
            'gender': 'Male',
            'activity_level': 'moderate',
            'fitness_goal': 'weight_loss',
        })
        assert response.status_code == 200
        result = response.context['result']
        assert result is not None
        assert result['bmi'] == pytest.approx(22.9, abs=0.05)
        assert result['category'] == 'Healthy'
        # Weight loss goal must create a caloric deficit
        assert result['target_calories'] == result['tdee'] - 500

    def test_post_persists_bmi_record(self, client):
        client.post('/bmi_calculator', {
            'name': 'Saved Member',
            'height': '160',
            'weight': '55',
            'age': '25',
            'gender': 'Female',
            'activity_level': 'light',
            'fitness_goal': 'maintenance',
        })
        record = BMIRecord.objects.filter(name='Saved Member').first()
        assert record is not None
        assert record.bmi_value == pytest.approx(21.5, abs=0.05)
        assert record.category == 'Healthy'

    def test_post_obese_category_classification(self, client):
        response = client.post('/bmi_calculator', {
            'name': 'Heavy Member',
            'height': '170',
            'weight': '100',
            'age': '40',
            'gender': 'Male',
        })
        assert response.context['result']['category'] == 'Obese'

    def test_history_shows_latest_records(self, admin_client, sample_bmi_record):
        # Admins can view the full BMI history
        response = admin_client.get('/bmi_calculator')
        assert response.context['history'].count() == 1

    def test_history_hidden_from_anonymous_and_members(self, client, member_client, sample_bmi_record):
        # Security: anonymous visitors and members must NOT see other members' BMI records
        assert client.get('/bmi_calculator').context['history'].count() == 0
        assert member_client.get('/bmi_calculator').context['history'].count() == 0

    def test_macro_chart_data_is_valid_json(self, client):
        response = client.get('/bmi_calculator')
        labels = json.loads(response.context['macro_labels'])
        data = json.loads(response.context['macro_data'])
        assert labels == ['Protein', 'Carbs', 'Fats']
        assert len(data) == 3


class TestChatbotPage:
    def test_chatbot_page_renders(self, client):
        response = client.get('/chatbot/')
        assert response.status_code == 200
        assert 'chatbot.html' in [t.name for t in response.templates]


class TestChatbotAPI:
    def test_post_json_message_returns_reply(self, client):
        response = client.post(
            '/api/chatbot/',
            data=json.dumps({'message': 'what are the membership plans?'}),
            content_type='application/json',
        )
        assert response.status_code == 200
        payload = response.json()
        assert payload['status'] == 'success'
        assert 'Plan' in payload['reply'] or '₹' in payload['reply']

    def test_post_form_encoded_message_returns_reply(self, client):
        response = client.post('/api/chatbot/', {'message': 'gym timings please'})
        payload = response.json()
        assert payload['status'] == 'success'
        assert '5:00 AM' in payload['reply']

    def test_post_empty_message_returns_prompt(self, client):
        response = client.post(
            '/api/chatbot/',
            data=json.dumps({'message': ''}),
            content_type='application/json',
        )
        assert response.json()['reply'] == 'Please ask me a question!'

    def test_get_request_returns_error_status(self, client):
        response = client.get('/api/chatbot/')
        payload = response.json()
        assert payload['status'] == 'error'

    def test_invalid_json_body_falls_back_gracefully(self, client):
        response = client.post(
            '/api/chatbot/',
            data='not-json',
            content_type='application/json',
        )
        # Falls back to form-encoded parsing -> empty message prompt
        assert response.status_code == 200
        assert response.json()['status'] == 'success'
