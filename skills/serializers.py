from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from .models import SkillCategory, Skill, UserSkill

class SkillCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SkillCategory
        fields = [
            'id',
            'name',
            'slug',
            'description',
            'parent',
            'is_active',
        ]
        read_only_fields = ['id', 'slug']


class SkillSerializer(serializers.ModelSerializer):
    category = SkillCategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=SkillCategory.objects.all(), write_only=True, source='category'
    )

    class Meta:
        model = Skill
        fields = [
            'id',
            'name',
            'slug',
            'description',
            'difficulty',
            'estimated_time_hours',
            'is_active',
            'category',
            'category_id',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']


class UserSkillSerializer(serializers.ModelSerializer):
    skill_detail = SkillSerializer(source='skill', read_only=True)
    proficiency_label = serializers.SerializerMethodField()

    class Meta:
        model = UserSkill
        fields = [
            'id',
            'user_id',
            'skill',
            'skill_detail',
            'proficiency',
            'proficiency_label',
            'learned_at',
            'notes',
            'is_verified',
            'created_at',
        ]
        read_only_fields = ['id', 'skill_detail', 'proficiency_label', 'created_at']
        validators = [
            UniqueTogetherValidator(
                queryset=UserSkill.objects.all(),
                fields=['user_id', 'skill'],
                message="User already has this skill recorded."
            )
        ]

    def get_proficiency_label(self, obj):
        return obj.get_proficiency_display()

    def validate_proficiency(self, value):
        if not 1 <= value <= 5:
            raise serializers.ValidationError("Proficiency must be between 1 and 5.")
        return value

    def validate(self, data):
        if data.get('is_verified') and data.get('proficiency', 0) < 3:
            raise serializers.ValidationError("Cannot mark skill as verified unless proficiency is 3+.")
        return data
