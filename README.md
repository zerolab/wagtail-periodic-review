# Wagtail Periodic Review

A Wagtail package for periodic page content reviews for quality or audit purposes.

[![Build status](https://img.shields.io/github/workflow/status/zerolab/wagtail-periodic-review/CI/main?style=for-the-badge)](https://github.com/zerolab/wagtail-periodic-review/actions)
[![black](https://img.shields.io/badge/code%20style-black-000000.svg?style=for-the-badge)](https://github.com/psf/black)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white&style=for-the-badge)](https://github.com/pre-commit/pre-commit)


## Features

- Dashboard panels
- Filtered report
- Configurable next review frequency


## Installation

Install using pip:

```bash
  pip install wagtail-periodic-review
```


After installing the module, add `wagtail_periodic_review` and `wagtail.contrib.settings` to installed apps in your settings file:

```python
# settings.py

INSTALLED_APPS = [
    # ...
    "wagtail.contrib.settings",
    "wagtail_periodic_review",
]
```

Run migrations:

```bash
$ ./manage.py migrate
```


## Usage

Add the `PeriodicReviewMixin` to your Page models:

```python
from wagtail.core.models import Page
from wagtail_periodic_review.models import PeriodicReviewMixin


class MyPage(PeriodicReviewMixin, Page):

    # Add the periodic review panels to the settings panels
    settings_panels = PeriodicReviewMixin.review_panels + Page.settings_panels
```
