from django.contrib.contenttypes.models import ContentType
from django.forms import Select
from django.forms.models import ModelChoiceIterator
from django.utils.functional import cached_property

from .utils import get_periodic_review_models


class PeriodicReviewContentTypeSelect(Select):
    """
    Custom Widget that limits ContentType options provided by ModelChoiceFields to
    those that represent subclasses of PeriodicReviewMixin.
    """

    def __init__(self, *args, **kwargs):
        self._choices = None
        super().__init__(*args, **kwargs)

    @cached_property
    def relevant_object_ids(self):
        ids = []
        for model in get_periodic_review_models():
            ct = ContentType.objects.get_for_model(model)
            ids.append(ct.id)
        return ids

    @property
    def choices(self):
        return self._choices

    @choices.setter
    def choices(self, value):
        if isinstance(value, ModelChoiceIterator):
            value.queryset = value.queryset.filter(id__in=self.relevant_object_ids)
        self._choices = value

    def create_option(
        self, name, value, label, selected, index, subindex=None, attrs=None
    ):
        """
        Overrides ``Select.create_option()`` to simplify the "appname | model class" labels
        returned by ``ContentType.__str__()``.
        """
        label = label.split("|").pop().strip()  # use model name only
        label = label[0].upper() + label[1:]  # uppercase first character
        return super().create_option(
            name, value, label, selected, index, subindex, attrs
        )
