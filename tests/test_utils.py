from unittest import mock

from dateutil.relativedelta import relativedelta
from django.test import TestCase
from django.utils import timezone
from wagtail.models import Page, Site

from tests.models import NonPageModel, ReviewedPage
from wagtail_periodic_review.utils import (
    add_review_date_annotations,
    for_review_this_month,
    get_periodic_review_models,
    review_overdue,
)


class TestUtils(TestCase):
    @classmethod
    def setUpTestData(cls):
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

        NonPageModel.objects.create(name="Non-page model")

    def test_get_periodic_review_models(self):
        models = get_periodic_review_models()

        self.assertEqual(len(models), 1)
        self.assertEqual(models[0], ReviewedPage)

    def test_review_overdue(self):
        pages = review_overdue(Page.objects.live())
        self.assertEqual(len(pages), 1)
        self.assertEqual(pages[0].pk, self.page_overdue.pk)

    @mock.patch(
        "wagtail_periodic_review.utils.get_periodic_review_models", return_value=[]
    )
    def test_review_overdue_with_no_periodic_review_models(
        self, _mocked_get_periodic_review_models
    ):
        self.assertEqual(review_overdue(Page.objects.live()).count(), 0)

    def test_review_overdue_with_non_page_queryset(self):
        # for non-Page querysets, we just return the queryset unchanged
        self.assertEqual(review_overdue(NonPageModel.objects.all()).count(), 1)

    def test_for_review_this_month(self):
        pages = for_review_this_month(Page.objects.live())
        self.assertEqual(len(pages), 1)
        self.assertEqual(pages[0].pk, self.page_soon.pk)

    @mock.patch(
        "wagtail_periodic_review.utils.get_periodic_review_models", return_value=[]
    )
    def test_for_review_this_month_with_no_periodic_review_models(
        self, _mocked_get_periodic_review_models
    ):
        self.assertEqual(for_review_this_month(Page.objects.live()).count(), 0)

    def test_for_review_this_month_with_non_page_queryset(self):
        # for non-Page querysets, we just return the queryset unchanged
        self.assertEqual(for_review_this_month(NonPageModel.objects.all()).count(), 1)

    def test_add_review_date_annotations(self):
        annotated = add_review_date_annotations(
            Page.objects.filter(pk=self.page_ok.pk)
        ).first()
        self.assertTrue(hasattr(annotated, "last_review_date"))
        self.assertTrue(hasattr(annotated, "next_review_date"))

    @mock.patch(
        "wagtail_periodic_review.utils.get_periodic_review_models", return_value=[]
    )
    def test_add_review_date_annotations_with_no_periodic_review_models(
        self, _mocked_get_periodic_review_models
    ):
        annotated = add_review_date_annotations(
            Page.objects.filter(pk=self.page_ok.pk)
        ).first()
        self.assertFalse(hasattr(annotated, "last_review_date"))
        self.assertFalse(hasattr(annotated, "next_review_date"))

    def test_add_review_date_annotations_with_non_page_queryset(self):
        qs = NonPageModel.objects.all()
        annotated_qs = add_review_date_annotations(qs)
        self.assertEqual(qs, annotated_qs)
        self.assertFalse(hasattr(annotated_qs.first(), "last_review_date"))
