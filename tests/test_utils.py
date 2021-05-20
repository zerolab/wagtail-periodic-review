from django.test import TestCase
from django.utils import timezone

from wagtail.core.models import Page, Site

from dateutil.relativedelta import relativedelta

from tests.testapp.models import PeriodicReviewPage
from wagtail_periodic_review.utils import (
    for_review_this_month,
    get_periodic_review_models,
    review_overdue,
)


class TestUtils(TestCase):
    def setUp(self):
        self.site = Site.objects.get(is_default_site=True)
        self.root_page = self.site.root_page

        month_start = timezone.now().date().replace(day=1)

        # Note: the default review period is 12 months
        self.page_overdue = PeriodicReviewPage(
            title="Overdue",
            slug="overdue",
            last_review_date=month_start - relativedelta(months=13),
        )
        self.root_page.add_child(instance=self.page_overdue)

        self.page_soon = PeriodicReviewPage(
            title="Coming soon",
            slug="soon",
            last_review_date=month_start - relativedelta(months=12),
        )
        self.root_page.add_child(instance=self.page_soon)

        self.page_ok = PeriodicReviewPage(title="Review OK", slug="ok")
        self.root_page.add_child(instance=self.page_ok)

    def test_get_periodic_review_models(self):
        models = get_periodic_review_models()

        assert len(models) == 1
        assert models[0] == PeriodicReviewPage

    def test_review_overdue(self):
        pages = review_overdue(Page.objects.live())
        self.assertEqual(len(pages), 1)
        self.assertEqual(pages[0].pk, self.page_overdue.pk)

    def test_for_review_this_month(self):
        pages = for_review_this_month(Page.objects.live())
        self.assertEqual(len(pages), 1)
        self.assertEqual(pages[0].pk, self.page_soon.pk)
