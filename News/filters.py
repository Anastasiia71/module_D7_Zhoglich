from django_filters import FilterSet, DateTimeFilter, ModelChoiceFilter
from django.forms import DateTimeInput
from .models import Post, Category


class PostFilter(FilterSet):
    category = ModelChoiceFilter(
        field_name='postCategory',
        queryset=Category.objects.all(),
        label='Категория',
        empty_label='любая'
    )

    added_after = DateTimeFilter(
        field_name='added_at',
        lookup_expr='gt',
        label='Дата',
        widget=DateTimeInput(
            format='%Y-%m-%dT%H:%M',
            attrs={'type': 'datetime-local'},
        ),
    )

    class Meta:
        model = Post
        fields = {
            'title': ['icontains'],
        }