from pathlib import PurePosixPath
from typing import (
    Dict,
    Union,
)
from urllib.parse import (
    unquote,
    urlparse,
)

from tri_declarative import (
    EMPTY,
    Refinable,
    dispatch,
)
from tri_struct import Struct

from iommi.base import Part
from iommi._web_compat import (
    Template,
)
from iommi.base import (
    bind_members,
    collect_members,
    EvaluatedRefinable,
    path_join,
)
from iommi.page import Fragment
from iommi.render import Attrs


class MenuBase(Part):
    tag: str = EvaluatedRefinable()
    sort: bool = EvaluatedRefinable()  # only applies for submenu items
    sub_menu: Dict = Refinable()
    attrs: Attrs = Refinable()
    template: Union[str, Template] = EvaluatedRefinable()

    @dispatch(
        sort=True,
        attrs__class__nav=True,  # TODO: style!
        attrs__class={'nav-pills': True},  # TODO: style!
        tag='ul',  # TODO: style!
        sub_menu=EMPTY,
    )
    def __init__(self, sub_menu, **kwargs):
        super(MenuBase, self).__init__(**kwargs)

        collect_members(
            self,
            name='sub_menu',
            items=sub_menu,
            # TODO: cls=self.get_meta().menu_item_class,
            cls=MenuItem,
        )

    def __repr__(self):
        r = '%s -> %s\n' % (self._name, self.url)
        for items in self.sub_menu.values():
            r += '    ' + repr(items)
        return r

    def on_bind(self):
        bind_members(self, name='sub_menu')

        # TODO:
        if self.sort:
            self.sub_menu = Struct({
                item._name: item
                for item in sorted(self.sub_menu.values(), key=lambda x: x.display_name)
            })

    def own_evaluate_parameters(self):
        return dict(menu_item=self)


class MenuItem(MenuBase):
    """
    Class that is used for the clickable menu items in a menu.

    See :doc:`Menu` for more complete examples.
    """

    display_name: str = EvaluatedRefinable()
    url: str = EvaluatedRefinable()
    regex: str = EvaluatedRefinable()
    group: str = EvaluatedRefinable()

    @dispatch(
        display_name=lambda menu_item, **_: menu_item._name.title().replace('_', ' '),
        regex=lambda menu_item, **_: '^' + menu_item.url if menu_item.url else None,
        url=lambda menu_item, **_: '/' + path_join(getattr(menu_item._parent, 'url', None), menu_item._name) + '/',
        tag='li',
    )
    def __init__(self, **kwargs):
        super(MenuItem, self).__init__(**kwargs)
        self.fragment = None
        self.a = None

    def on_bind(self):
        super(MenuItem, self).on_bind()

        # If this is a section header, and all sub-parts are hidden, hide myself
        if not self.url and not self.sub_menu:
            self.include = False

        self.a = Fragment(
            tag='a',
            attrs__href=self.url,
            attrs__class={'nav-link': True},  # TODO: style!
            child=self.display_name,
        ).bind(parent=self)
        self.fragment = Fragment(
            tag=self.tag,
            template=self.template,
            attrs=self.attrs,
            child=self.a,
            children=self.sub_menu.values(),
        ).bind(parent=self)

    def __html__(self, *, context=None, render=None):
        return self.fragment.__html__()


class MenuException(Exception):
    pass


class Menu(MenuBase):
    """
    Class that describes menus.

    Example:

    .. code:: python

        menu = Menu(
            sub_menu=dict(
                root=MenuItem(url='/'),

                albums=MenuItem(url='/albums/'),

                # url defaults to /<name>/ so we
                # don't need to write /musicians/ here
                musicians=MenuItem(),
            ),
        )
    """

    @dispatch(
        sort=False
    )
    def __init__(self, **kwargs):
        super(Menu, self).__init__(**kwargs)
        self.fragment = None

    def __html__(self, *, context=None, render=None):
        return self.fragment.__html__()

    def on_bind(self):
        super(Menu, self).on_bind()
        self.validate_and_set_active(current_path=self.get_request().path)

        self.fragment = Fragment(
            tag=self.tag,
            template=self.template,
            attrs=self.attrs,
            children=self.sub_menu.values(),
        ).bind(parent=self)

    def validate_and_set_active(self, current_path: str):

        # verify there is no ambiguity for the MenuItems
        paths = set()
        for item in self.sub_menu.values():
            if '://' in item.url:
                continue

            path = urlparse(item.url).path
            if path in paths:
                raise MenuException(f'MenuItem paths are ambiguous; several non-external MenuItems have the path: {path}')

            paths.add(path)

        current = None
        current_parts_matching = 0
        path_parts = PurePosixPath(current_path).parts

        items = [(item, urlparse(item.url)) for item in self.sub_menu.values()]
        for (item, parsed_url) in items:
            if '://' in item.url:
                continue

            if current_path.startswith(parsed_url.path):
                parts = PurePosixPath(unquote(parsed_url.path)).parts
                matching_parts = 0
                for i in range(min(len(parts), len(path_parts))):
                    if parts[i] is path_parts[i]:
                        matching_parts += 1

                if matching_parts > current_parts_matching:
                    current = (item, parsed_url)
                    current_parts_matching = matching_parts

        if current:
            current[0].a.attrs['class']['active'] = True