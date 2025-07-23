from django.test import TestCase
from rest_framework.test import APIClient
from .models import Skill, UserSkill, SkillCategory


class SkillsAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Parent category
        self.cat_programming = SkillCategory.objects.create(name="Programming")

        # Children categories
        self.cat_frontend = SkillCategory.objects.create(name="Frontend", parent=self.cat_programming)
        self.cat_backend = SkillCategory.objects.create(name="Backend", parent=self.cat_programming)

        # Skills
        self.skill_python = Skill.objects.create(
            name="Python Programming",
            category=self.cat_backend,
            difficulty=2,
        )

        self.skill_django = Skill.objects.create(
            name="Django",
            category=self.cat_backend,
            difficulty=3,
        )

        self.skill_react = Skill.objects.create(
            name="React",
            category=self.cat_frontend,
            difficulty=3,
        )

        self.skill_game_dev = Skill.objects.create(
            name="Game Development",
            category=self.cat_programming,
            difficulty=4,
        )

        self.user_id = 42

        UserSkill.objects.create(
            user_id=self.user_id,
            skill=self.skill_python,
            proficiency=3,
        )

    # List Skills
    def test_list_skills(self):
        response = self.client.get('/api/skills/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), len(Skill.objects.all()))

    def test_list_skills_empty(self):
        Skill.objects.all().delete()
        response = self.client.get('/api/skills/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])

    # Get Skills by slug
    def test_get_skill_by_slug(self):
        response = self.client.get(f'/api/skills/{self.skill_python.slug}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], "Python Programming")
        self.assertEqual(response.data['slug'], self.skill_python.slug)

    def test_get_nonexistent_skill_detail_returns_404(self):
        response = self.client.get('/api/skills/does-not-exist/')
        self.assertEqual(response.status_code, 404)

    # Recommend Skills
    def test_recommend_from_parent_category_includes_children(self):
        response = self.client.get(
            f"/api/skills/recommend/?category={self.cat_programming.slug}&user_id={self.user_id}")
        self.assertEqual(response.status_code, 200)

        recommended_names = [skill["name"] for skill in response.data]
        self.assertIn("React", recommended_names)
        self.assertNotIn("Python Programming", recommended_names)

    def test_recommend_from_child_category_includes_sibling_skills(self):
        response = self.client.get(f"/api/skills/recommend/?category={self.cat_frontend.slug}&user_id={self.user_id}")
        self.assertEqual(response.status_code, 200)

        recommended_names = [skill["name"] for skill in response.data]

        self.assertIn("Django", recommended_names)
        self.assertIn("React", recommended_names)
        self.assertNotIn("Python Programming", recommended_names)

    def test_recommend_skills_happy_path(self):
        response = self.client.get(
            f'/api/skills/recommend/?category={self.cat_programming.slug}&user_id={self.user_id}'
        )
        self.assertEqual(response.status_code, 200)

        recommended_names = [skill["name"] for skill in response.data]

        self.assertIn("React", recommended_names)
        self.assertNotIn("Python Programming", recommended_names)

    def test_recommend_skills_excludes_learned(self):
        url = f"/api/skills/recommend/?category={self.cat_programming.slug}&user_id={self.user_id}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        recommended_names = [skill['name'] for skill in response.data]

        self.assertNotIn("Python Programming", recommended_names)
        self.assertIn("React", recommended_names)

    def test_recommend_skills_missing_params(self):
        response = self.client.get("/api/skills/recommend/?user_id=42")
        self.assertEqual(response.status_code, 400)

    def test_recommend_invalid_category_slug_returns_404(self):
        response = self.client.get('/api/skills/recommend/?category=notreal&user_id=1')
        self.assertEqual(response.status_code, 404)

    def test_recommend_user_id_not_int(self):
        response = self.client.get(f'/api/skills/recommend/?category={self.cat_programming.slug}&user_id=abc')
        self.assertEqual(response.status_code, 400)

    # Create Skills
    def test_create_user_skill_success(self):
        payload = {
            "user_id": self.user_id,
            "skill": self.skill_react.id,
            "proficiency": 4,
            "learned_at": "2025-01-01"
        }
        response = self.client.post("/api/user-skills/", payload, format='json')
        self.assertEqual(response.status_code, 201)

        data = response.data
        self.assertEqual(data["user_id"], self.user_id)
        self.assertEqual(data["skill"], self.skill_react.id)
        self.assertEqual(data["proficiency"], 4)
        self.assertEqual(data["proficiency_label"], "Expert")

        self.assertIn("skill_detail", data)
        self.assertEqual(data["skill_detail"]["name"], "React")
        self.assertEqual(data["skill_detail"]["category"]["name"], "Frontend")

    def test_create_duplicate_user_skill(self):
        payload = {
            "user_id": self.user_id,
            "skill": self.skill_python.id,
            "proficiency": 3
        }
        response = self.client.post("/api/user-skills/", payload, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn("User already has this skill recorded.", response.data["non_field_errors"])

    def test_create_bad_payload(self):
        payload = {
            "user_id": self.user_id,
            "proficiency": 3
        }
        response = self.client.post("/api/user-skills/", payload, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn("skill", response.data)
