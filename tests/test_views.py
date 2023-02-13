from dateutil.relativedelta import relativedelta
from django.urls import reverse
from django.utils import timezone
from wagtail.admin.tests.api.utils import AdminAPITestCase
from wagtail.models import Site

from tests.models import ReviewedPage


class DashboardPanelsTest(AdminAPITestCase):
    def setUp(self):
        self.root_page = Site.objects.get(is_default_site=True).root_page

        self.month_start = timezone.now().date().replace(day=1)
        self.dashboard_url = reverse("wagtailadmin_home")

        self.page_ok = ReviewedPage(title="Review OK", slug="ok")
        self.root_page.add_child(instance=self.page_ok)

        super().setUp()

    def test_overdue_panel(self):
        # Note: the default review period is 12 months
        page_overdue = ReviewedPage(
            title="The Overdue Page",
            slug="overdue",
            last_review_date=self.month_start - relativedelta(months=13),
        )
        self.root_page.add_child(instance=page_overdue)

        response = self.client.get(self.dashboard_url)

        self.assertContains(response, "Content review overdue")
        self.assertContains(response, "The Overdue Page")

        self.assertNotContains(response, "Review OK")
        self.assertNotContains(response, "For review this month")

        page_overdue.unpublish()
        response = self.client.get(self.dashboard_url)
        self.assertNotContains(response, "Content review overdue")
        self.assertNotContains(response, "The Overdue Page")

    def test_for_view_this_month(self):
        page_soon = ReviewedPage(
            title="Coming soon",
            slug="soon",
            last_review_date=self.month_start - relativedelta(months=12),
        )
        self.root_page.add_child(instance=page_soon)

        response = self.client.get(self.dashboard_url)

        self.assertNotContains(response, "Content review overdue")
        self.assertNotContains(response, "Review OK")

        self.assertContains(response, "For review this month")
        self.assertContains(response, "Coming soon")


# To-Do: test the report view
# To-Do: test settings
