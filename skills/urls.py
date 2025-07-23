from django.urls import path
from .views import (
    SkillListView,
    SkillRecommendationView,
    UserSkillCreateView,
    SkillDetailView,
)

urlpatterns = [
    path('skills/recommend/', SkillRecommendationView.as_view(), name='skill-recommend'),
    path('skills/<slug:slug>/', SkillDetailView.as_view(), name='skill-detail'),
    path('skills/', SkillListView.as_view(), name='skill-list'),
    path('user-skills/', UserSkillCreateView.as_view(), name='user-skill-create'),
]
