import django_filters

from blog.models import BlogPost


class BlogPostFilter(
    django_filters.FilterSet
):

    title = django_filters.CharFilter(
        lookup_expr='icontains'
    )

    created_at = django_filters.DateFromToRangeFilter()

    class Meta:

        model = BlogPost

        fields = [

            'category',
            'status',
            'author',
            'tags',
            'title',

        ]