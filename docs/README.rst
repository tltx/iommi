iommi
=====

.. raw:: html

    <h3 class="pun">Your first pick for a django power cord</h3>

.. image:: https://github.com/TriOptima/iommi/workflows/tests/badge.svg
    :target: https://github.com/TriOptima/iommi/actions?query=workflow%3Atests+branch%3Amaster

.. image:: https://codecov.io/gh/TriOptima/iommi/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/TriOptima/iommi

.. image:: https://repl.it/badge/github/boxed/iommi-repl.it
    :target: https://repl.it/github/boxed/iommi-repl.it

.. image:: https://img.shields.io/discord/773470009795018763
    :target: https://discord.gg/ZyYRYhf7Pd


iommi is a Django-based framework that magically create pages, forms and tables with advanced out-of-the-box functionality based on your applications models - without sacrificing flexibility and control.

Major features:

- A system to project django model definitions into more high level definitions
- :doc:`Forms <forms>`: view models, data validation, and parsing
- :doc:`Queries <queries>`: filtering lists/query sets
- :doc:`Tables <tables>`: view models for lists/query sets, html tables, and CSV reports
- :doc:`Pages <pages>`: compose pages from parts like forms, tables and html fragments

All the components are written with the same philosophy of:

* Everything has a name
* Traversing a namespace is done with `__` when `.` can't be used in normal python syntax
* Callables for advanced usage, values for the simple cases
* Late binding
* Declarative/programmatic hybrid API
* Prepackaged commonly used patterns (that can still be customized!)
* Single point customization with *no* boilerplate
* Escape hatches included

See :doc:`philosophy <philosophy>` for explanations of all these.

Example:


.. code:: python

    class IndexPage(Page):
        title = html.h1('Supernaut')
        welcome_text = 'This is a discography of the best acts in music!'

        artists = Table(auto__model=Artist, page_size=5)
        albums = Table(
            auto__model=Album,
            page_size=5,
        )
        tracks = Table(auto__model=Album, page_size=5)


    urlpatterns = [
        path('', IndexPage().as_view()),
    ]


This creates a page with three separate tables, a header and some text:

.. image:: README-screenshot.png

For more examples, see the `examples project <https://github.com/TriOptima/iommi/tree/master/examples/examples>`_.


Usage
------

See :doc:`usage <usage>`.


Running tests
-------------

We use hammett for tests, so `pip install hammett` then run `hammett`.

There's a `make test-live` target for running tests interactively. You first need to `pip install watchdog pyyaml argh`.

For running the full tests on all supported environments: install tox then :code:`make test-all`.


License
-------

BSD
