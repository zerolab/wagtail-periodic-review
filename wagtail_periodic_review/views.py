from wagtail.admin.views.reports import ReportView
from wagtail.core.models import Page

from wagtail_periodic_review.filters import PeriodicReviewFilterSet
from wagtail_periodic_review.utils import (
    add_review_date_annotations,
    filter_across_subtypes,
)


class PeriodicReviewContentReport(ReportView):
    title = "Periodic review"
    header_icon = "doc-empty-inverse"
    template_name = "reports/periodic_review_report.html"
    filterset_class = PeriodicReviewFilterSet

    def get_queryset(self):
        queryset = filter_across_subtypes(
            Page.objects.all(), last_review_date__isnull=False
        )
        return add_review_date_annotations(queryset).order_by("next_review_date")
