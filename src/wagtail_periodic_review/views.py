from django.core.exceptions import FieldError
from django.utils.translation import gettext as _
from wagtail import VERSION as WAGTAIL_VERSION
from wagtail.admin.views.reports import ReportView

from .filters import PeriodicReviewFilterSet
from .utils import add_review_date_annotations, filter_across_subtypes


if WAGTAIL_VERSION >= (5, 1):
    from wagtail.permission_policies.pages import PagePermissionPolicy
else:
    from wagtail.models import UserPagePermissionsProxy


class PeriodicReviewContentReport(ReportView):
    title = _("Periodic review content")
    header_icon = "wpr-calendar-stats"
    template_name = "reports/periodic_review_report.html"
    filterset_class = PeriodicReviewFilterSet

    def _get_editable_pages(self):
        if WAGTAIL_VERSION >= (5, 1):
            return PagePermissionPolicy().instances_user_has_permission_for(
                self.request.user, "change"
            )
        return UserPagePermissionsProxy(self.request.user).editable_pages()

    def get_queryset(self):
        queryset = filter_across_subtypes(
            self._get_editable_pages(),
            last_review_date__isnull=False,
        )
        try:
            return add_review_date_annotations(queryset).order_by("next_review_date")
        except FieldError:
            return queryset
