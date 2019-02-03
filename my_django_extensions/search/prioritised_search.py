import operator
from functools import reduce
from django.db import models
from django.db.models.functions import Coalesce
from django.utils import six
from django.db.models import ExpressionWrapper, Q, BooleanField
from rest_framework.filters import SearchFilter
from rest_framework.compat import distinct


class PrioritySearchFilter(SearchFilter):

    def get_search_terms(self, request):
        """
        PrioritySearchFilter do not support comma and/or whitespace delimitation
        in ?search=... query parameter.
        """
        return request.query_params.get(self.search_param, '')

    def filter_queryset(self, request, queryset, view):
        """
        Prioritise the search by search fields
        """
        search_fields = getattr(view, 'search_fields', None)
        search_term = self.get_search_terms(request)

        if not search_fields or not search_term:
            return queryset

        base = queryset
        orm_lookups = [
            self.construct_search(six.text_type(search_field))
            for search_field in search_fields
        ]

        annotate_query = {}
        annotate_query_lookups = []
        for index, orm_lookup in enumerate(orm_lookups):
            annotate_query_lookups.append(f'lookup{index}')
            annotate_query.update({
                annotate_query_lookups[index] : Coalesce(
                    ExpressionWrapper(Q(**{orm_lookup: search_term}), output_field=BooleanField()), False
                )
            })

        queryset = queryset.annotate(**annotate_query).filter(
            reduce(operator.or_, [models.Q(**{lookup: True}) for lookup in annotate_query_lookups])
        )

        if self.must_call_distinct(queryset, search_fields):
            # Filtering against a many-to-many field requires us to
            # call queryset.distinct() in order to avoid duplicate items
            # in the resulting queryset.
            # We try to avoid this if possible, for performance reasons.
            queryset = distinct(queryset, base)

        queryset = queryset.order_by(*[f'-{lookup}' for lookup in annotate_query_lookups])
        return queryset
