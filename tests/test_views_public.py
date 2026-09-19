"""
Integration tests for the public website views (Module business pages):
homepage, about, services, team, gallery, blog, contact, class details.
"""
import pytest

from myapp.models import contacts, BlogPost

pytestmark = pytest.mark.django_db


class TestStaticPagesRender:
    def test_index_page(self, member_client, sample_about, sample_membership, sample_team,
                        sample_service, sample_feature, sample_gym_class,
                        approved_review, sample_blog):
        assert member_client.get('/').status_code == 200

    def test_about_page(self, member_client, sample_about, sample_team, sample_feature):
        assert member_client.get('/about').status_code == 200

    def test_services_page(self, member_client, sample_service, sample_membership):
        assert member_client.get('/services').status_code == 200

    def test_team_page(self, member_client, sample_team):
        assert member_client.get('/team').status_code == 200

    def test_gallery_page(self, member_client, sample_gallery_item):
        assert member_client.get('/gallery').status_code == 200

    def test_blog_page(self, member_client, sample_blog):
        assert member_client.get('/blog').status_code == 200

    def test_contact_page(self, member_client):
        assert member_client.get('/contact').status_code == 200

    def test_class_details_page(self, member_client, sample_gym_class):
        assert member_client.get('/class_details').status_code == 200

    def test_blog_details_page(self, member_client, sample_blog):
        assert member_client.get('/blog_details').status_code == 200


class TestContactForm:
    def test_valid_submission_stores_contact(self, member_client):
        response = member_client.post('/contact', {
            'name': 'Test User',
            'email': 'test@example.com',
            'phone': '9998887776',
            'comment': 'I have a question',
        })
        assert response.status_code == 200
        assert response.context['submitted'] is True
        assert contacts.objects.filter(email='test@example.com').exists()

    def test_incomplete_submission_does_not_store(self, member_client):
        response = member_client.post('/contact', {'name': 'Only Name'})
        assert response.status_code == 200
        assert response.context['submitted'] is False
        assert contacts.objects.count() == 0


class TestBlogFiltering:
    def test_filter_by_category(self, member_client, sample_blog):
        BlogPost.objects.create(
            title='Protein Guide', slug='protein-guide',
            category='Nutrition', snippet='s', content='c',
        )
        response = member_client.get('/blog', {'category': 'Nutrition'})
        titles = [b.title for b in response.context['blogs']]
        assert titles == ['Protein Guide']

    def test_search_by_title(self, member_client, sample_blog):
        response = member_client.get('/blog', {'q': 'Fat Loss'})
        titles = [b.title for b in response.context['blogs']]
        assert '10 Tips for Fat Loss' in titles

    def test_search_no_match_returns_empty(self, member_client, sample_blog):
        response = member_client.get('/blog', {'q': 'nonexistentzzz'})
        assert response.context['blogs'].count() == 0


class TestGalleryFiltering:
    def test_filter_by_category(self, member_client, sample_gallery_item):
        response = member_client.get('/gallery', {'category': 'workout'})
        assert response.context['gallery_items'].count() == 1

    def test_filter_unknown_category_returns_empty(self, member_client, sample_gallery_item):
        response = member_client.get('/gallery', {'category': 'yoga'})
        assert response.context['gallery_items'].count() == 0
