# polls/filters.py
from django_filters import rest_framework as filters
from .models import Poll

class PollFilter(filters.FilterSet):
    expiry_start = filters.DateFilter(field_name="expiry_date", lookup_expr="gte")
    expiry_end = filters.DateFilter(field_name="expiry_date", lookup_expr="lte")
    created_start = filters.DateFilter(field_name="created_at", lookup_expr="gte")
    created_end = filters.DateFilter(field_name="created_at", lookup_expr="lte")
    created_by = filters.CharFilter(field_name="created_by__username", lookup_expr="icontains")
    id = filters.NumberFilter(field_name="id")

    class Meta:
        model = Poll
        fields = ['id', 'created_by', 'expiry_start', 'expiry_end', 'created_start', 'created_end']
