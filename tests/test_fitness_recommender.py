"""
Module 18: AI-Based BMI & Fitness Recommendation - Unit Tests
Covers BMR (Mifflin-St Jeor), TDEE activity multipliers, BMI categorization,
goal-based calorie adjustment and macro-nutrient distribution.
"""
import pytest

from myapp.ai_engine.fitness_recommender import (
    calculate_bmr,
    calculate_tdee,
    generate_ai_recommendation,
)


class TestCalculateBMR:
    def test_bmr_male_mifflin_st_jeor(self):
        # 10*70 + 6.25*175 - 5*25 + 5 = 1673.75
        assert calculate_bmr(70, 175, 25, 'male') == pytest.approx(1673.75)

    def test_bmr_female_mifflin_st_jeor(self):
        # 10*70 + 6.25*175 - 5*25 - 161 = 1507.75
        assert calculate_bmr(70, 175, 25, 'female') == pytest.approx(1507.75)

    def test_bmr_gender_is_case_insensitive(self):
        assert calculate_bmr(70, 175, 25, 'FEMALE') == pytest.approx(1507.75)

    def test_bmr_male_is_higher_than_female(self):
        assert calculate_bmr(70, 175, 25, 'male') > calculate_bmr(70, 175, 25, 'female')

    def test_bmr_decreases_with_age(self):
        young = calculate_bmr(70, 175, 20, 'male')
        old = calculate_bmr(70, 175, 50, 'male')
        assert young > old

    def test_unknown_gender_treated_as_male(self):
        # Non-'female' values fall through to the male equation
        assert calculate_bmr(70, 175, 25, 'other') == pytest.approx(1673.75)


class TestCalculateTDEE:
    def test_sedentary_multiplier(self):
        assert calculate_tdee(1000, 'sedentary') == 1200

    def test_light_multiplier(self):
        assert calculate_tdee(1000, 'light') == 1375

    def test_moderate_multiplier(self):
        assert calculate_tdee(1000, 'moderate') == 1550

    def test_very_active_multiplier(self):
        assert calculate_tdee(1000, 'very_active') == 1725

    def test_extra_active_multiplier(self):
        assert calculate_tdee(1000, 'extra_active') == 1900

    def test_unknown_activity_level_defaults_to_light(self):
        assert calculate_tdee(1000, 'unknown_level') == 1375

    def test_activity_level_case_insensitive(self):
        assert calculate_tdee(1000, 'MODERATE') == 1550


class TestBMICalculationAndCategory:
    def test_bmi_value_formula(self):
        # 70 / 1.75^2 = 22.857 -> 22.9
        res = generate_ai_recommendation(175, 70, 25, 'male')
        assert res['bmi'] == pytest.approx(22.9, abs=0.05)

    @pytest.mark.parametrize('height,weight,expected_category', [
        (175, 50, 'Underweight'),   # BMI 16.3
        (175, 70, 'Healthy'),       # BMI 22.9
        (175, 85, 'Overweight'),    # BMI 27.8
        (175, 100, 'Obese'),        # BMI 32.7
    ])
    def test_bmi_category_boundaries(self, height, weight, expected_category):
        res = generate_ai_recommendation(height, weight, 30, 'male')
        assert res['category'] == expected_category

    def test_bmi_boundary_18_5_is_healthy(self):
        # BMI exactly 18.5 -> not < 18.5 -> Healthy
        res = generate_ai_recommendation(200, 74, 30, 'male')
        assert res['bmi'] == pytest.approx(18.5, abs=0.01)
        assert res['category'] == 'Healthy'

    def test_bmi_boundary_25_is_overweight(self):
        # BMI exactly 25.0 -> not < 25 -> Overweight
        res = generate_ai_recommendation(200, 100, 30, 'male')
        assert res['bmi'] == pytest.approx(25.0, abs=0.01)
        assert res['category'] == 'Overweight'

    def test_ai_insight_present_for_every_category(self):
        for weight, _ in [(50, 'Underweight'), (70, 'Healthy'), (85, 'Overweight'), (100, 'Obese')]:
            res = generate_ai_recommendation(175, weight, 30, 'male')
            assert res['ai_insight']
            assert len(res['ai_insight']) > 20


class TestGoalBasedRecommendation:
    def _result(self, goal, activity='moderate'):
        return generate_ai_recommendation(175, 75, 28, 'male', activity, goal)

    def test_weight_loss_creates_500_kcal_deficit(self):
        res = self._result('weight_loss')
        assert res['target_calories'] == res['tdee'] - 500
        assert (res['protein_ratio'], res['carb_ratio'], res['fat_ratio']) == (40, 30, 30)

    def test_muscle_gain_creates_400_kcal_surplus(self):
        res = self._result('muscle_gain')
        assert res['target_calories'] == res['tdee'] + 400
        assert (res['protein_ratio'], res['carb_ratio'], res['fat_ratio']) == (30, 50, 20)

    def test_endurance_creates_150_kcal_surplus(self):
        res = self._result('endurance')
        assert res['target_calories'] == res['tdee'] + 150
        assert (res['protein_ratio'], res['carb_ratio'], res['fat_ratio']) == (25, 55, 20)

    def test_maintenance_keeps_tdee(self):
        res = self._result('maintenance')
        assert res['target_calories'] == res['tdee']
        assert (res['protein_ratio'], res['carb_ratio'], res['fat_ratio']) == (30, 40, 30)

    def test_unknown_goal_falls_back_to_maintenance(self):
        res = self._result('not_a_real_goal')
        assert res['target_calories'] == res['tdee']

    def test_macro_ratios_sum_to_100_for_all_goals(self):
        for goal in ['weight_loss', 'muscle_gain', 'endurance', 'maintenance']:
            res = self._result(goal)
            total = res['protein_ratio'] + res['carb_ratio'] + res['fat_ratio']
            assert total == 100, f"Macro ratios must sum to 100 for {goal}"

    def test_macro_grams_match_target_calories(self):
        res = self._result('weight_loss')
        cal = res['target_calories']
        assert res['protein_g'] == round(cal * 0.40 / 4)
        assert res['carbs_g'] == round(cal * 0.30 / 4)
        assert res['fats_g'] == round(cal * 0.30 / 9)

    def test_higher_activity_level_raises_target_calories(self):
        sedentary = self._result('weight_loss', 'sedentary')
        extra = self._result('weight_loss', 'extra_active')
        assert extra['target_calories'] > sedentary['target_calories']

    def test_workout_and_cardio_recommendations_present(self):
        for goal in ['weight_loss', 'muscle_gain', 'endurance', 'maintenance']:
            res = self._result(goal)
            assert res['workout_type']
            assert res['cardio_recommendation']
            assert res['strength_recommendation']
            assert res['goal_text']

    def test_result_contains_all_expected_keys(self):
        res = self._result('weight_loss')
        expected_keys = {
            'bmi', 'category', 'bmr', 'tdee', 'target_calories', 'goal_text',
            'workout_type', 'cardio_recommendation', 'strength_recommendation',
            'protein_g', 'carbs_g', 'fats_g', 'protein_ratio', 'carb_ratio',
            'fat_ratio', 'ai_insight',
        }
        assert expected_keys.issubset(res.keys())
