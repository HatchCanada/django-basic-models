# Copyright 2011 Concentric Sky, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.




from django.core.cache import cache
from django.conf import settings
from django.db.models.query import QuerySet
from django.db import models
import cachemodel


class CustomQuerySetManager(models.Manager):
    def __init__(self, query_set=None, *args, **kwargs):
        self._custom_query_set = query_set
        # this is required to fix an AttributeError with django 1.5
        self._db = None

    def get_query_set(self):
        if self._custom_query_set:
            return self._custom_query_set(self.model)
        return QuerySet(self.model)

    def __getattr__(self, attr, *args):
        if attr.startswith('_'):
            # Helps avoid problems when pickling a model.
            raise AttributeError
        # expose queryset methods as manager methods as well.
        return getattr(self.get_query_set(), attr, *args)


class ActiveQuerySet(QuerySet):
    def active(self):
        return self.filter(is_active=True)

class ActiveModelManager(CustomQuerySetManager):
    def __init__(self, *args, **kwargs):
        super(ActiveModelManager, self).__init__(query_set=ActiveQuerySet, *args, **kwargs)

class FilteredActiveObjectsManager(ActiveModelManager):
    def get_query_set(self):
        return super(FilteredActiveObjectsManager, self).get_query_set().filter(is_active=True)


class DefaultModelManager(ActiveModelManager):
    pass

class SlugModelManager(DefaultModelManager):
    def get_by_natural_key(self,slug):
        return self.get(slug=slug)



# class IsActiveSlugModelManager(IsActiveModelManager):
#     def get_by_slug(self, slug, cache_timeout=None):
#         return self.get_by("slug", slug, cache_timeout)

# class OnlyOneActiveModelManager(cachemodels.CacheModelManager):
#     def get_active(self):
#         cache_key = 'active_%s' % (self.model.__name__)
#         active = cache.get(cache_key)
#         if active is None:
#             active = self.filter(is_active=True).order_by('-updated_at')
#             if len(active) < 1:
#                 # no active one!... just pick the last one that was changed
#                 active = self.all().order_by('-updated_at')
#                 if len(active) < 1:
#                     return None
#             active = active[0]
#             cache.set(cache_key, active, getattr(settings, "DEFAULT_CACHE_TIMEOUT", 900))
#         return active


# # Adapted from: http://djangosnippets.org/snippets/734/ and http://seanmonstar.com/post/708862164/extending-django-models-managers-and-querysets
# class CustomQuerySetManagerMixin(object):
#     """
#     Allows you to define chainable queryset functions on a model inner class.

#     Example:

#     ```
#     from django.db.models.query import QuerySet

#     class Post(models.Model):
#         published_at = models.DateTimeField()
#         author = models.ForeignKey(User)

#         objects = CustomQuerySetManager()

#         class CustomQuerySet(BaseCustomQuerySet):
#             def published(self):
#                 return self.filter(published_at__lte=timezone.now(), is_active=True)

#             def by_author(self, author):
#                 return self.filter(author=author)
#     ```

#     You would now be able to do the following to chain the custom queries together:

#     ```
#     posts = Post.objects.published().by_author(self.request.user).exclude(id=1)
#     ```
#     """

#     def get_query_set(self):
#         if hasattr(self.model, 'CustomQuerySet'):
#             return self.model.CustomQuerySet(self.model)
#         else:
#             # If they haven't defined a CustomQuerySet internal class, then return a normal QuerySet to keep things rolling.
#             return QuerySet(self.model)

#     def __getattr__(self, attr, *args):
#         if attr.startswith('_'):
#             # Helps avoid problems when pickling a model.
#             raise AttributeError
#         # When an attribuet of the manager is requested, return the queryset's attribute of the same name to allow chaining.
#         return getattr(self.get_query_set(), attr, *args)


# class CustomQuerySetManager(CustomQuerySetManagerMixin, HasActiveModelManager):
#     pass


# class CustomQuerySetSlugManager(CustomQuerySetManagerMixin, SlugModelManager):
#     pass


# class IsActiveQuerySetMixin(object):
#     def active(self):
#         return self.filter(is_active=True)


# class BaseCustomQuerySet(IsActiveQuerySetMixin, QuerySet):
#     pass