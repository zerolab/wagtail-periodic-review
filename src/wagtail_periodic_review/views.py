from django.core.exceptions import FieldError
from django.utils.translation import gettext as _
from wagtail import VERSION as WAGTAIL_VERSION
from wagtail.admin.views.reports import PageReportView
from wagtail.permission_policies.pages import PagePermissionPolicy

from .filters import PeriodicReviewFilterSet
from .utils import add_review_date_annotations, filter_across_subtypes


def _adapt_wagtail_report_attributes(cls):
    """
    A class decorator that adapts ReportView-derived classes for compatibility
    with multiple versions of Wagtail by conditionally assigning attributes
    based on the Wagtail version. This includes setting appropriate titles,
    and adjusting template names and URL names for AJAX support since Wagtail 6.2.
    Attributes adjusted:
    - `title` or `page_title` based on Wagtail version for the display name of the report.
    - For Wagtail 6.2 and above, additional attributes like `results_template_name`,
      `index_results_url_name`, and `index_url_name` are set to support AJAX updates
      and utilize the `wagtail.admin.ui.tables` framework.
    """
    if WAGTAIL_VERSION < (6, 2):
        cls.title = _("Periodic review content")
        cls.template_name = "reports/periodic_review_report.html"
    else:
        # The `title` attr was **changed** to `page_title` in Wagtail 6.2
        cls.page_title = _("Periodic review content")
        # The `results_template_name` attr was **added** in Wagtail 6.2
        # to support updating the listing via AJAX upon filtering and
        # to allow the use of the `wagtail.admin.ui.tables` framework.
        cls.results_template_name = "reports/periodic_review_report_results.html"
        # The `index_results_url_name` attr was **added** in Wagtail 6.2
        # to support updating the listing via AJAX upon filtering.
        cls.index_results_url_name = "wagtail_periodic_review_report_results"
        cls.index_url_name = "wagtail_periodic_review_report"
    return cls


@_adapt_wagtail_report_attributes
class PeriodicReviewContentReport(PageReportView):
    header_icon = "wpr-calendar-stats"

    filterset_class = PeriodicReviewFilterSet

    def _get_editable_pages(self):
        return PagePermissionPolicy().instances_user_has_permission_for(
            self.request.user, "change"
        )

    def get_queryset(self):
        queryset = filter_across_subtypes(
            self._get_editable_pages(),
            last_review_date__isnull=False,
        )
        try:
            return add_review_date_annotations(queryset).order_by("next_review_date")
        except FieldError:
            return queryset
