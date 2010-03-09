# This file is a part of MediaCore, Copyright 2009 Simple Station Inc.
#
# MediaCore is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# MediaCore is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from tg import config, request, response, tmpl_context
from sqlalchemy import orm, sql
from repoze.what.predicates import has_permission

from mediacore.lib.base import (BaseController, url_for, redirect,
    expose, expose_xhr, validate, paginate)
from mediacore.lib import helpers
from mediacore.model import (DBSession, fetch_row, get_available_slug,
    Category)
from mediacore.forms.categories import CategoryForm


category_form = CategoryForm()

class CategoryadminController(BaseController):
    allow_only = has_permission('admin')

    @expose('mediacore.templates.admin.categories.index')
    @paginate('categories', items_per_page=25)
    def index(self, page=1, **kwargs):
        """List categories with pagination.

        :param page: Page number, defaults to 1.
        :type page: int
        :rtype: Dict
        :returns:
            categories
                The list of :class:`~mediacore.model.categories.Category`
                instances for this page.
            category_form
                The :class:`~mediacore.forms.categories.CategoryForm` instance.

        """
        categories = DBSession.query(Category)\
            .options(orm.undefer('media_count'))\
            .order_by(Category.name)

        return dict(
            categories = categories,
            category_form = category_form,
        )


    @expose('json')
    @validate(category_form)
    def save(self, id, delete, **kwargs):
        """Save changes or create a category.

        See :class:`~mediacore.forms.categories.CategoryForm` for POST vars.

        :param id: Category ID
        :param delete: If true the category is deleted rather than saved.
        :type delete: bool
        :rtype: JSON dict
        :returns:
            success
                bool

        """
        cat = fetch_row(Category, id)

        if delete:
            DBSession.delete(cat)
            data = dict(success=True)
        else:
            cat.name = kwargs['name']
            cat.slug = get_available_slug(Category, kwargs['slug'], cat)
            DBSession.add(cat)
            data = dict(success=True, name=cat.name, slug=cat.slug)

        if request.is_xhr:
            return data
        else:
            redirect(action='index')
