from django.conf import settings
from django.test.client import Client

from funfactory.urlresolvers import reverse
from mock import patch
from nose.tools import eq_

from mozorg.hierarchy import PageNode, requires_parent
from mozorg.tests import TestCase


class MyNode(object):
        def __init__(self, parent=None):
            self.parent = parent

        @requires_parent
        def myfunc(self):
            return True


class TestRequiresParent(TestCase):
    def test_requires_parent(self):
        """
        If a method requires the parent attribute, it should return None when
        the attribute is not set.
        """
        mynode = MyNode()
        eq_(mynode.myfunc(), None)

        mynode = MyNode(True)
        eq_(mynode.myfunc(), True)


class TestPageNode(TestCase):
    def test_children_parents(self):
        """
        If a node is given children in the constructor, the children must mark
        the node as their parent.
        """
        children = [PageNode('test'), PageNode('test2')]
        parent = PageNode('parent', children=children)
        for child in children:
            eq_(child.parent, parent)

    def test_full_path(self):
        """
        full_path should return the path of this node and all of its parents
        joined by slashes.
        """
        child = PageNode('test', path='asdf')
        PageNode('test', path='blah', children=[
                 PageNode('test', path='whoo', children=[child])
        ])
        eq_(child.full_path, 'blah/whoo/asdf')

    def test_full_path_empty(self):
        """
        If one of a node's parents have an empty path, they should not be
        included in the full path.
        """
        child = PageNode('test', path='asdf')
        PageNode('', path='blah', children=[PageNode('', children=[child])])
        eq_(child.full_path, 'blah/asdf')

    @patch('mozorg.hierarchy.page')
    def test_page(self, page):
        """
        If a pagenode is given a template, it should provide a page for
        inclusion in a urlconf.
        """
        page.return_value = 'testreturn'
        eq_(PageNode('test').page, None)

        node = PageNode('test', path='blah', template='test.html')
        parent = PageNode('testparent', path='yo', children=[node])
        eq_(node.page, 'testreturn')
        page.assert_called_with('yo/blah', 'test.html', node_root=parent,
                                node=node)

    def test_path_to_root(self):
        """
        path_to_root should return an iterable of nodes following the route from
        the child node to the root of the tree.
        """
        child1 = PageNode('test')
        child2 = PageNode('test', children=[child1])
        root = PageNode('test', children=[child2, PageNode('test')])
        eq_(list(child1.path_to_root, [child1, child2, root]))

    def test_breadcrumbs(self):
        """
        breadcrumbs should return a list of nodes following the path from the
        root to the child node.
        """
        child1 = PageNode('test')
        child2 = PageNode('test', children=[child1])
        root = PageNode('test', children=[child2, PageNode('test')])
        eq_(list(child1.breadcrumbs, [root, child2, child1]))

    def test_root(self):
        """root should return the root of the page tree."""
        child1 = PageNode('test')
        child2 = PageNode('test', children=[child1])
        root = PageNode('test', children=[child2, PageNode('test')])
        eq_(child1.root, root)
