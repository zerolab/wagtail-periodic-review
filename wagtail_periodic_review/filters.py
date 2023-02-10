import django_filters

from django.contrib.contenttypes.models import ContentType
from django.utils.text import capfirst
from wagtail.admin.filters import DateRangePickerWidget, WagtailFilterSet
from wagtail.core.models import Page

from wagtail_periodic_review.utils import get_periodic_review_models


def content_type_choices():
    choices = []
    for model in get_periodic_review_models():
        ct = ContentType.objects.get_for_model(model)
        if ct:
            choices.append((ct.id, capfirst(model._meta.verbose_name)))
    return choices


class PeriodicReviewFilterSet(WagtailFilterSet):
    content_type = django_filters.ChoiceFilter(
        label="Content type",
        field_name="content_type_id",
        choices=content_type_choices,
        empty_label="Any",
    )
    last_review = django_filters.DateFromToRangeFilter(
        label="Last reviewed",
        field_name="last_review_date",
        widget=DateRangePickerWidget(),
    )
    next_review = django_filters.DateFromToRangeFilter(
        label="Next review due",
        field_name="next_review_date",
        widget=DateRangePickerWidget(),
    )

    class Meta:
        model = Page
        fields = ("content_type", "last_review", "next_review")
