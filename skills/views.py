from rest_framework import generics, status, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.db.models import Q

from .models import Skill, UserSkill, SkillCategory
from .serializers import SkillSerializer, UserSkillSerializer


class BaseSkillView:
    queryset = Skill.objects.filter(is_active=True)
    serializer_class = SkillSerializer


class SkillListView(BaseSkillView, generics.ListAPIView):
    pass


class SkillDetailView(BaseSkillView, generics.RetrieveAPIView):
    lookup_field = "slug"


class SkillRecommendationView(APIView):
    def get(self, request):
        category_slug = request.query_params.get("category")
        user_id = request.query_params.get("user_id")

        if not user_id or not category_slug:
            raise ValidationError("Both category and user_id are required.")

        try:
            user_id = int(user_id)
        except ValueError:
            raise ValidationError({"user_id": "Must be a valid integer."})

        category = get_object_or_404(SkillCategory, slug=category_slug)

        category_ids = [category.id]
        if category.parent:
            sibling_ids = category.get_sibling_ids()
            category_ids += sibling_ids
        if category.children:
            category_ids += category.get_descendant_ids()

        learned_ids = UserSkill.objects.filter(
            user_id=user_id
        ).values_list('skill_id', flat=True)

        recommendations = Skill.objects.filter(
            category__id__in=category_ids,
            is_active=True
        ).exclude(
            id__in=learned_ids
        ).order_by('difficulty')[:3]

        return Response(SkillSerializer(recommendations, many=True).data)


class UserSkillCreateView(generics.CreateAPIView):
    serializer_class = UserSkillSerializer
