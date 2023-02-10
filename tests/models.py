from wagtail.models import Page

from wagtail_periodic_review.models import PeriodicReviewMixin


class SimplePage(Page):
    ...


class ReviewedPage(PeriodicReviewMixin, Page):
    settings_panels = PeriodicReviewMixin.review_panels + Page.settings_panels
