from django.template.loader import render_to_string
from django.urls import path, reverse
from wagtail.admin.menu import MenuItem
from wagtail.core import hooks
from wagtail.core.models import UserPagePermissionsProxy

from wagtail_periodic_review import utils
from wagtail_periodic_review.views import PeriodicReviewContentReport


class BaseHomePanel:
    heading = ""
    description = ""
    description_css_class = "help-info"
    template_name = "wagtailadmin/periodic_review/home_panel.html"

    def __init__(self, request):
        self.request = request

    def get_page_list(self):
        return UserPagePermissionsProxy(self.request.user).publishable_pages()

    def get_context_data(self, **kwargs):
        context = {
            "request": self.request,
            "heading": self.heading,
            "description": self.description,
            "description_css_class": self.description_css_class,
            "page_list": self.get_page_list(),
        }
        context.update(kwargs)
        return context

    def render(self):
        return render_to_string(self.template_name, self.get_context_data())


class OverdueReviewsPanel(BaseHomePanel):
    heading = "Content review overdue"
    description = "The following pages are overdue a review, but are still live."
    description_css_class = "help-critical"
    order = 200

    def get_page_list(self):
        all_pages = super().get_page_list()
        return utils.review_overdue(all_pages.live())[:50]


class ForReviewThisMonthPanel(BaseHomePanel):
    heading = "For review this month"
    description = "The following live pages are due a review this month."
    description_css_class = "help-warning"
    order = 201

    def get_page_list(self):
        all_pages = super().get_page_list()
        return utils.for_review_this_month(all_pages.live())


@hooks.register("construct_homepage_panels")
def add_review_panels(request, panels):
    panels.append(OverdueReviewsPanel(request))
    panels.append(ForReviewThisMonthPanel(request))


@hooks.register("register_reports_menu_item")
def register_report_menu_item():
    return MenuItem(
        "Periodic review content",
        reverse("wagtail_periodic_review_report"),
        classnames="icon icon-" + PeriodicReviewContentReport.header_icon,
        order=800,
    )


@hooks.register("register_admin_urls")
def register_report_url():
    return [
        path(
            "reports/periodic-review/",
            PeriodicReviewContentReport.as_view(),
            name="wagtail_periodic_review_report",
        )
    ]
