"""
Module 22: NLP Gym Chatbot (GymBot) - Unit Tests
Covers TF-IDF + Cosine Similarity intent matching against the Gym Knowledge
Base, the keyword fallback matcher and edge cases.
"""
import pytest

from myapp.ai_engine.nlp_chatbot import (
    GYM_KB,
    get_bot_response,
    match_intent_simple,
)


class TestKnowledgeBase:
    def test_knowledge_base_is_not_empty(self):
        assert len(GYM_KB) >= 10

    def test_every_intent_has_required_fields(self):
        for item in GYM_KB:
            assert item['intent']
            assert isinstance(item['keywords'], list) and item['keywords']
            assert item['answer']

    def test_intent_names_are_unique(self):
        intents = [item['intent'] for item in GYM_KB]
        assert len(intents) == len(set(intents))


class TestIntentMatching:
    @pytest.mark.parametrize('query,expected_fragment', [
        ('what are your gym timings?', '5:00 AM'),
        ('when does the gym open?', '5:00 AM'),
        ('how much does membership cost?', 'Plan'),
        ('tell me about membership plans and pricing', '₹'),
        ('which classes do you offer?', 'classes'),
        ('who are your trainers?', 'priya'),
        ('how do I calculate my bmi?', 'BMI'),
        ('where is the gym located?', 'Ahmedabad'),
        ('do you have sauna facilities?', 'facilities'),
        ('can I download reports?', 'CSV'),
    ])
    def test_intent_answers_contain_relevant_info(self, query, expected_fragment):
        reply = get_bot_response(query)
        assert expected_fragment.lower() in reply.lower()

    def test_greeting_intent(self):
        reply = get_bot_response('hello there')
        assert 'welcome' in reply.lower()

    def test_thanks_intent(self):
        reply = get_bot_response('thank you so much')
        assert 'welcome' in reply.lower()

    def test_query_is_case_insensitive(self):
        lower = get_bot_response('what are the membership plans?')
        upper = get_bot_response('WHAT ARE THE MEMBERSHIP PLANS?')
        assert lower == upper


class TestEdgeCases:
    def test_empty_message_returns_prompt(self):
        assert get_bot_response('') == 'Please ask me a question!'

    def test_none_message_returns_prompt(self):
        assert get_bot_response(None) == 'Please ask me a question!'

    def test_whitespace_only_message_returns_prompt(self):
        assert get_bot_response('   ') == 'Please ask me a question!'

    def test_unrelated_query_returns_fallback_message(self):
        reply = get_bot_response('quadratic polynomial eigenvalue zzzz')
        assert 'didn\'t quite understand' in reply or 'ask me about' in reply.lower()

    def test_response_is_always_a_nonempty_string(self):
        for query in ['hi', 'membership?', 'zzz999']:
            reply = get_bot_response(query)
            assert isinstance(reply, str) and len(reply) > 0


class TestSimpleKeywordMatcher:
    def test_exact_keyword_scores_high(self):
        _, score = match_intent_simple('membership plans price')
        assert score >= 6  # at least two whole-word keyword hits

    def test_no_keyword_match_returns_fallback_with_zero_score(self):
        answer, score = match_intent_simple('xyzzy plugh')
        assert score == 0
        assert 'didn\'t quite understand' in answer

    def test_best_matching_intent_wins(self):
        answer, score = match_intent_simple('I want to know the gym timing today')
        assert '5:00 AM' in answer
        assert score > 0
