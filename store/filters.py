from django_filters.rest_framework import FilterSet

from .models import Course

class CourseFilter(FilterSet):
    class Meta:
        model = Course
        fields = {
            'name': ['icontains'],
            'description': ['icontains'],
            'unit_price': ['exact', 'lt', 'gt'],
            'teacher': ['exact'],
            'language': ['exact'],
            'level': ['exact'],
        }
