from django.db import models
from django.utils.text import slugify


class SkillCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='children'
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_descendant_ids(self):
        ids = []

        def collect_children(category):
            for child in category.children.all():
                ids.append(child.id)
                collect_children(child)

        collect_children(self)
        return ids

    def get_sibling_ids(self):
        if self.parent is None:
            siblings = SkillCategory.objects.filter(parent__isnull=True)
        else:
            siblings = SkillCategory.objects.filter(parent=self.parent)

        siblings = siblings.exclude(id=self.id)

        return list(siblings.values_list("id", flat=True))


class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    category = models.ForeignKey(
        SkillCategory,
        on_delete=models.PROTECT,
        related_name='skills'
    )
    description = models.TextField(blank=True)
    difficulty = models.PositiveSmallIntegerField()
    estimated_time_hours = models.FloatField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['category__name', 'difficulty', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class UserSkill(models.Model):
    PROFICIENCY_LEVELS = [
        (1, "Beginner"),
        (2, "Intermediate"),
        (3, "Advanced"),
        (4, "Expert"),
        (5, "Mastered"),
    ]

    user_id = models.PositiveIntegerField(db_index=True)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='user_skills')
    proficiency = models.PositiveSmallIntegerField(choices=PROFICIENCY_LEVELS)
    learned_at = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user_id', 'skill')
        ordering = ['-created_at']

    def __str__(self):
        return f"User {self.user_id} - {self.skill.name} ({self.get_proficiency_display()})"


class SuggestionRule(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    recommended_skill = models.ForeignKey(Skill, null=True, blank=True, on_delete=models.SET_NULL)
    recommended_category = models.ForeignKey(SkillCategory, null=True, blank=True, on_delete=models.SET_NULL)

    required_all = models.ManyToManyField(SkillCategory, related_name='rules_all')
    required_any = models.ManyToManyField(SkillCategory, related_name='rules_any')
