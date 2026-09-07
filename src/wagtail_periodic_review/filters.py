import django_filters

from django.contrib.contenttypes.models import ContentType
from django.utils.text import capfirst
from django.utils.translation import gettext as _
from wagtail import VERSION as WAGTAIL_VERSION
from wagtail.admin.filters import DateRangePickerWidget, WagtailFilterSet

from .utils import get_periodic_review_models


if WAGTAIL_VERSION >= (8, 0):
    import swapper

    Page = swapper.load_model("wagtailcore", "Page")
else:
    from wagtail.models import Page


def content_type_choices():
    choices = []
    for model in get_periodic_review_models():
        if ct := ContentType.objects.get_for_model(model):
            choices.append((ct.id, capfirst(model._meta.verbose_name)))
    return choices


class PeriodicReviewFilterSet(WagtailFilterSet):
    content_type = django_filters.ChoiceFilter(
        label=_("Content type"),
        field_name="content_type_id",
        choices=content_type_choices,
        empty_label=_("Any"),
    )
    last_review = django_filters.DateFromToRangeFilter(
        label=_("Last reviewed"),
        field_name="last_review_date",
        widget=DateRangePickerWidget(),
    )
    next_review = django_filters.DateFromToRangeFilter(
        label=_("Next review due"),
        field_name="next_review_date",
        widget=DateRangePickerWidget(),
    )

    class Meta:
        model = Page
        fields = ("content_type", "last_review", "next_review")
