from unittest import mock

from dateutil.relativedelta import relativedelta
from django.urls import reverse
from django.utils import timezone
from wagtail.admin.tests.api.utils import AdminAPITestCase
from wagtail.models import Site

from tests.models import NonPageModel, ReviewedPage, SimplePage


class DashboardPanelsTest(AdminAPITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.root_page = Site.objects.get(is_default_site=True).root_page

        cls.month_start = timezone.now().date().replace(day=1)
        cls.dashboard_url = reverse("wagtailadmin_home")

        cls.page_ok = ReviewedPage(title="Review OK", slug="ok")
        cls.root_page.add_child(instance=cls.page_ok)

        cls.page_overdue_title = "The Overdue Page"
        cls.page_soon_title = "The Soon Page"

    def add_overdue_page(self):
        # Note: the default review period is 12 months
        self.page_overdue = ReviewedPage(
            title=self.page_overdue_title,
            slug="overdue",
            last_review_date=self.month_start - relativedelta(months=13),
        )
        self.root_page.add_child(instance=self.page_overdue)

    def add_soon_page(self):
        self.page_soon = ReviewedPage(
            title=self.page_soon_title,
            slug="soon",
            last_review_date=self.month_start - relativedelta(months=12),
        )
        self.root_page.add_child(instance=self.page_soon)

    def test_overdue_panel(self):
        self.add_overdue_page()
        response = self.client.get(self.dashboard_url)

        self.assertContains(response, "Content review overdue")
        self.assertContains(response, self.page_overdue_title)

        self.assertNotContains(response, "For review this month")
        self.assertNotContains(response, self.page_ok.title)

        self.page_overdue.unpublish()
        response = self.client.get(self.dashboard_url)
        self.assertNotContains(response, "Content review overdue")
        self.assertNotContains(response, self.page_overdue_title)

    @mock.patch(
        "wagtail_periodic_review.utils.get_periodic_review_models", return_value=[]
    )
    def test_overdue_panel_with_no_periodic_review_models(
        self, _mocked_get_periodic_review_models
    ):
        self.add_overdue_page()
        response = self.client.get(self.dashboard_url)
        self.assertNotContains(response, "Content review overdue")

    def test_for_view_this_month_panel(self):
        self.add_soon_page()
        response = self.client.get(self.dashboard_url)

        self.assertNotContains(response, "Content review overdue")
        self.assertNotContains(response, self.page_ok.title)
        self.assertNotContains(response, self.page_overdue_title)

        self.assertContains(response, "For review this month")
        self.assertContains(response, self.page_soon_title)

        self.page_soon.unpublish()
        response = self.client.get(self.dashboard_url)
        self.assertNotContains(response, "For review this month")
        self.assertNotContains(response, self.page_soon_title)

    @mock.patch(
        "wagtail_periodic_review.utils.get_periodic_review_models", return_value=[]
    )
    def test_for_review_this_month_panel_with_no_periodic_review_models(
        self, _mocked_get_periodic_review_models
    ):
        self.add_soon_page()
        response = self.client.get(self.dashboard_url)
        self.assertNotContains(response, "Content review overdue")
        self.assertNotContains(response, self.page_soon.title)


class PeriodicReviewReportTest(AdminAPITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.report_url = reverse("wagtail_periodic_review_report")

        cls.site = Site.objects.get(is_default_site=True)
        cls.root_page = cls.site.root_page

        month_start = timezone.now().date().replace(day=1)

        # Note: the default review period is 12 months
        cls.page_overdue = ReviewedPage(
            title="Overdue",
            slug="overdue",
            last_review_date=month_start - relativedelta(months=13),
        )
        cls.root_page.add_child(instance=cls.page_overdue)

        cls.page_soon = ReviewedPage(
            title="Coming soon",
            slug="soon",
            last_review_date=month_start - relativedelta(months=12),
        )
        cls.root_page.add_child(instance=cls.page_soon)

        cls.page_ok = ReviewedPage(title="Review OK", slug="ok")
        cls.root_page.add_child(instance=cls.page_ok)

        cls.regular_page = SimplePage(title="Simple page", slug="simple")
        cls.root_page.add_child(instance=cls.regular_page)

        cls.non_page_model = NonPageModel.objects.create(name="Non-page model")

    def test_report(self):
        response = self.client.get(self.report_url)
        self.assertEqual(response.status_code, 200)

        self.assertContains(response, self.page_soon.title)
        self.assertContains(response, self.page_overdue.title)
        self.assertNotContains(response, self.page_ok.title)
        self.assertNotContains(response, self.regular_page.title)

    @mock.patch(
        "wagtail_periodic_review.utils.get_periodic_review_models", return_value=[]
    )
    def test_report_with_no_periodic_review_models(
        self, _mocked_get_periodic_review_models
    ):
        response = self.client.get(self.report_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No pages")
        self.assertNotContains(response, self.page_soon.title)
        self.assertNotContains(response, self.page_overdue.title)
        self.assertNotContains(response, self.page_ok.title)
        self.assertNotContains(response, self.regular_page.title)
        self.assertNotContains(response, self.non_page_model.name)


# To-Do: test settings
