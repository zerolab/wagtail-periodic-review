from dateutil.relativedelta import relativedelta
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from wagtail.models import Orderable
from wagtail.search import index

from .utils import get_periodic_review_models
from .widgets import PeriodicReviewContentTypeSelect


class ReviewFrequencyChoices(models.IntegerChoices):
    ONE_MONTH = 1, _("1 month")
    TWO_MONTHS = 2, _("2 months")
    THREE_MONTHS = 3, _("3 months")
    SIX_MONTHS = 6, _("6 months")
    TWELVE_MONTHS = 12, _("12 months")
    EIGHTEEN_MONTHS = 18, _("18 months")
    TWO_YEARS = 24, _("2 years")
    THREE_YEARS = 36, _("3 years")
    FOUR_YEARS = 48, _("4 years")


class PeriodicReviewMixin(models.Model):
    """
    A mixin class to be use with page types that require
    regular reviews for audit or other purposes.

    ``next_review_date`` values are set automatically on
    creation, drawing on the frequency settings for the
    relevant site. They are also updated automatically
    whenever changes to those settings are made.
    """

    last_review_date = models.DateField(blank=True, null=True)
    current_version_ref = models.CharField(
        verbose_name=_("current version ref"), max_length=20, blank=True
    )
    current_version_compiled_by = models.CharField(
        verbose_name=_("current version compiled by"), max_length=255, blank=True
    )

    # Non-editable
    next_review_date = models.DateField(null=True, editable=False)
    custom_review_frequency = models.PositiveIntegerField(null=True, editable=False)

    class Meta:
        abstract = True

    review_panels = [
        MultiFieldPanel(
            heading=_("Periodic review"),
            children=[
                FieldPanel("last_review_date"),
                FieldPanel("current_version_ref"),
                FieldPanel("current_version_compiled_by"),
            ],
        )
    ]

    additional_search_fields = [
        index.SearchField("current_version_ref"),
        index.SearchField("current_version_compiled_by"),
        index.FilterField("current_version_ref"),
        index.FilterField("current_version_compiled_by"),
        index.FilterField("last_review_date"),
        index.FilterField("next_review_date"),
        index.FilterField("custom_review_frequency"),
    ]

    def with_content_json(self, content_json):
        """
        Overrides Page.with_content_json() to preserve additional
        live page values when restoring from a revision.
        """
        obj = super().with_content_json(content_json)
        obj.next_review_date = self.next_review_date
        return obj

    def get_review_frequency_rule(self):
        if url_parts := self.get_url_parts():
            return PeriodicReviewFrequencyRule.objects.filter(
                sitesettings__site_id=url_parts[0],
                content_type=self.cached_content_type,
            ).first()

    def get_review_frequency(self):
        if self.custom_review_frequency:
            return self.custom_review_frequency
        if rule := self.get_review_frequency_rule():
            return rule.frequency
        return ReviewFrequencyChoices.TWELVE_MONTHS

    def calculate_next_review_date(self):
        if self.last_review_date:
            return self.last_review_date + relativedelta(
                months=self.get_review_frequency()
            )

    def save(self, *args, **kwargs):
        """
        Overrides Page.save() to recalculate ``next_review_date`` whenever
        ``last_review_date`` is updated.
        """
        if (
            "update_fields" not in kwargs
            or "last_review_date" in kwargs["update_fields"]
        ):
            self.next_review_date = self.calculate_next_review_date()
        super().save(*args, **kwargs)


class PeriodicReviewFrequencyRule(Orderable):
    sitesettings = ParentalKey(
        "wagtail_periodic_review.PeriodicReviewFrequencySettings",
        related_name="frequency_rules",
    )
    content_type = models.ForeignKey(
        ContentType, verbose_name=_("content type"), on_delete=models.CASCADE
    )
    frequency = models.PositiveIntegerField(
        verbose_name=_("review frequency"),
        choices=ReviewFrequencyChoices.choices,
        default=ReviewFrequencyChoices.TWELVE_MONTHS,
    )

    class Meta(Orderable.Meta):
        constraints = [
            models.UniqueConstraint(
                fields=["sitesettings", "content_type"], name="unique_rule"
            )
        ]

    panels = [
        FieldPanel("content_type", widget=PeriodicReviewContentTypeSelect),
        FieldPanel("frequency"),
    ]

    @property
    def cached_content_type(self):
        return ContentType.objects.get_for_id(self.content_type_id)

    @cached_property
    def model_class(self):
        return self.cached_content_type.model_class()

    def set_next_review_dates(self, site=None):
        """
        Updates ``next_review_date`` for all pages of relevant type,
        provided they have a ``last_review_date`` value and are not using
        ``custom_review_frequency``.
        """
        site = site or self.sitesettings.site
        to_update = []
        for obj in (
            self.model_class.objects.all()
            .descendant_of(site.root_page)
            .filter(
                # required for calculation
                last_review_date__isnull=False,
                # allow these pages to maintain their own value on save
                custom_review_frequency__isnull=True,
            )
            .only("id", "next_review_date")
        ):
            obj.next_review_date = obj.last_review_date + relativedelta(
                months=self.frequency
            )
        self.model_class.objects.bulk_update(to_update, ["next_review_date"])


@register_setting
class PeriodicReviewFrequencySettings(ClusterableModel, BaseSiteSetting):
    panels = [InlinePanel("frequency_rules")]

    def clean_frequency_rules(self):
        """
        Called after saving to ensure rules exist for all subclasses of PeriodicReviewMixin,
        and rules that no longer meet that criteria are deleted.
        """
        target_models = set(get_periodic_review_models())
        covered_models = set()

        for obj in self.frequency_rules.all():
            if obj.model_class not in target_models:
                obj.delete()
            else:
                covered_models.add(obj.model_class)

        for model_class in target_models:
            if model_class not in covered_models:
                PeriodicReviewFrequencyRule.objects.create(
                    sitesettings=self,
                    content_type=ContentType.objects.get_for_model(model_class),
                    frequency=ReviewFrequencyChoices.TWELVE_MONTHS,
                )

    def recalculate_next_review_dates(self):
        """
        Called after saving to update the 'next_review_date' value for all
        relevant pages, according to the ``rules`` defined for the site.

        NOTE: PageRevisions do not need updating, because pages should retain
        their live 'next_review_date' value when restored from revisions (see
        ``PeriodicReviewMixin.with_content_json()``).
        """
        # TODO: Reorder types in such a way that multiple non-abstract models in the same
        # inheritance chain are processed in 'least -> most specific' order.
        for rule in self.frequency_rules.all():
            rule.set_next_review_dates(site=self.site)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.clean_frequency_rules()
        self.recalculate_next_review_dates()

    class Meta:
        verbose_name = _("periodic review frequency")
        verbose_name_plural = _("periodic review frequencies")
