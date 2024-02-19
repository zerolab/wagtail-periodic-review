from django.db import models
from wagtail.models import Page

from wagtail_periodic_review.models import PeriodicReviewMixin


class SimplePage(Page): ...


class ReviewedPage(PeriodicReviewMixin, Page):
    settings_panels = PeriodicReviewMixin.review_panels + Page.settings_panels


class NonPageModel(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
