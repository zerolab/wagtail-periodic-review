from wagtail.core.models import Page

from wagtail_periodic_review.models import PeriodicReviewMixin


class HomePage(Page):
    pass


class PeriodicReviewPage(PeriodicReviewMixin, Page):
    pass
