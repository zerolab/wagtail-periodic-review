from django.core.exceptions import FieldError
from django.utils.translation import gettext as _
from wagtail.admin.views.reports import ReportView
from wagtail.models import Page

from .filters import PeriodicReviewFilterSet
from .utils import add_review_date_annotations, filter_across_subtypes


class PeriodicReviewContentReport(ReportView):
    title = _("Periodic review content")
    header_icon = "wpr-calendar-stats"
    template_name = "reports/periodic_review_report.html"
    filterset_class = PeriodicReviewFilterSet

    def get_queryset(self):
        queryset = filter_across_subtypes(
            Page.objects.all(), last_review_date__isnull=False
        )
        try:
            return add_review_date_annotations(queryset).order_by("next_review_date")
        except FieldError:
            return queryset
