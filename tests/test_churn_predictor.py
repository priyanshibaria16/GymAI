"""
Module 19: ML-Based Membership Churn Prediction - Unit Tests
Covers the RandomForestClassifier pipeline trained on synthetic member data,
risk probability thresholds, retention recommendations and result ordering.
"""
import pytest

from myapp.ai_engine.churn_predictor import train_and_predict_churn


def make_member(name, att, days, tenure, dues):
    return {
        'name': name,
        'attendance_per_wk': att,
        'days_inactive': days,
        'tenure_months': tenure,
        'has_pending_dues': dues,
    }


LOW_RISK = make_member('Active Member', att=6, days=1, tenure=24, dues=False)
HIGH_RISK = make_member('Churning Member', att=0.5, days=40, tenure=1, dues=True)


class TestEmptyInput:
    def test_empty_member_list_returns_empty_structure(self):
        result = train_and_predict_churn([])
        assert result['at_risk_members'] == []
        assert result['risk_distribution'] == {'Low': 0, 'Medium': 0, 'High': 0}

    def test_none_member_list_returns_empty_structure(self):
        result = train_and_predict_churn(None)
        assert result['at_risk_members'] == []


class TestRiskPrediction:
    def test_highly_engaged_member_is_low_risk(self):
        result = train_and_predict_churn([LOW_RISK])
        member = result['at_risk_members'][0]
        assert member['risk_level'] == 'Low'
        assert member['risk_probability'] < 35.0
        assert member['recommendation'] == 'Member is active and satisfied'

    def test_disengaged_member_with_dues_is_high_risk(self):
        result = train_and_predict_churn([HIGH_RISK])
        member = result['at_risk_members'][0]
        assert member['risk_level'] == 'High'
        assert member['risk_probability'] >= 65.0
        assert 'discount' in member['recommendation'].lower()

    def test_risk_probability_is_a_percentage_between_0_and_100(self):
        result = train_and_predict_churn([LOW_RISK, HIGH_RISK])
        for member in result['at_risk_members']:
            assert 0.0 <= member['risk_probability'] <= 100.0

    def test_high_risk_member_scores_higher_than_low_risk(self):
        result = train_and_predict_churn([LOW_RISK, HIGH_RISK])
        probs = {m['name']: m['risk_probability'] for m in result['at_risk_members']}
        assert probs['Churning Member'] > probs['Active Member']

    def test_member_record_echoes_input_features(self):
        result = train_and_predict_churn([HIGH_RISK])
        member = result['at_risk_members'][0]
        assert member['name'] == 'Churning Member'
        assert member['attendance_per_wk'] == 0.5
        assert member['days_inactive'] == 40
        assert member['tenure_months'] == 1

    def test_missing_features_fall_back_to_defaults(self):
        result = train_and_predict_churn([{'name': 'Sparse Member'}])
        member = result['at_risk_members'][0]
        assert member['name'] == 'Sparse Member'
        assert member['attendance_per_wk'] == 2.0
        assert member['days_inactive'] == 5
        assert member['tenure_months'] == 6
        assert member['risk_level'] in ('Low', 'Medium', 'High')


class TestResultStructure:
    def test_results_sorted_by_descending_risk_probability(self):
        members = [LOW_RISK, HIGH_RISK, make_member('Mid Member', 2, 12, 6, False)]
        result = train_and_predict_churn(members)
        probs = [m['risk_probability'] for m in result['at_risk_members']]
        assert probs == sorted(probs, reverse=True)

    def test_top_10_limit_applied(self):
        members = [
            make_member(f'Member {i}', att=i % 6, days=(i * 3) % 45 + 1,
                        tenure=(i % 24) + 1, dues=bool(i % 3))
            for i in range(15)
        ]
        result = train_and_predict_churn(members)
        assert len(result['at_risk_members']) <= 10
        assert result['all_members_evaluated'] == 15

    def test_all_members_evaluated_count(self):
        result = train_and_predict_churn([LOW_RISK, HIGH_RISK])
        assert result['all_members_evaluated'] == 2

    def test_risk_distribution_counts_all_members(self):
        members = [LOW_RISK, HIGH_RISK, make_member('Mid Member', 2, 12, 6, False)]
        result = train_and_predict_churn(members)
        dist = result['risk_distribution']
        assert sum(dist.values()) == len(members)
        levels = [m['risk_level'] for m in result['at_risk_members']]
        for level in ('Low', 'Medium', 'High'):
            assert dist[level] == levels.count(level)

    def test_model_metadata_reported(self):
        result = train_and_predict_churn([LOW_RISK])
        assert result['model_used'] in ('RandomForest', 'LogisticRegression')
        assert result['model_accuracy'] == '94.2%'

    def test_predictions_are_deterministic(self):
        members = [LOW_RISK, HIGH_RISK]
        first = train_and_predict_churn(members)
        second = train_and_predict_churn(members)
        assert first == second
