from threading import Thread
from unittest import TestCase

from iocs import IoC
from iocs.scope_based.strategy import Scope, InitScopesCommand


class PropagateExceptionThread(Thread):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ex = None

    def run(self):
        try:
            super().run()
        except BaseException as e:
            self.ex = e

    def join(self, *args, **kwargs):
        super().join(*args, **kwargs)
        if self.ex is not None:
            raise self.ex


class TestScopeBasedIoC(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        InitScopesCommand().execute()

    @classmethod
    def tearDownClass(cls) -> None:
        IoC.resolve('Scopes.Current.Set', IoC.resolve('Scopes.Root')).execute()

    def test_root_scope_is_available(self):
        self.assertIsInstance(IoC.resolve('Scopes.Root'), Scope)

    def test_default_current_scope_is_root(self):
        root_scope = IoC.resolve('Scopes.Root')
        current_scope = IoC.resolve('Scopes.Current')
        self.assertEqual(root_scope, current_scope)

    def test_create_scopes_storage(self):
        self.assertEqual({}, IoC.resolve('Scopes.Storage'))

    def test_create_new_scope(self):
        root_scope = IoC.resolve('Scopes.Root')
        new_scope = IoC.resolve('Scopes.New', root_scope)
        self.assertIsInstance(new_scope, Scope)
        self.assertNotEqual(root_scope, new_scope)

    def test_set_scope(self):
        root_scope = IoC.resolve('Scopes.Root')
        new_scope = IoC.resolve('Scopes.New', root_scope)
        IoC.resolve('Scopes.Current.Set', new_scope).execute()
        self.assertEqual(new_scope, IoC.resolve('Scopes.Current'))

    def test_register_dependency(self):
        root_scope = IoC.resolve('Scopes.Root')
        new_scope = IoC.resolve('Scopes.New', root_scope)
        IoC.resolve('Scopes.Current.Set', new_scope).execute()

        IoC.resolve('IoC.Register', 'dependency', lambda: 1).execute()
        self.assertEqual(1, IoC.resolve('dependency'))

        with self.assertRaisesRegex(Exception, 'Dependency already registered'):
            IoC.resolve('IoC.Register', 'dependency', lambda: 2).execute()

    def test_resolving_dependency_depends_on_current_scope(self):
        root_scope = IoC.resolve('Scopes.Root')
        scope_1 = IoC.resolve('Scopes.New', root_scope)
        IoC.resolve('Scopes.Current.Set', scope_1).execute()

        IoC.resolve('IoC.Register', 'dependency', lambda: 1).execute()
        self.assertEqual(1, IoC.resolve('dependency'))

        scope_2 = IoC.resolve('Scopes.New', root_scope)
        IoC.resolve('Scopes.Current.Set', scope_2).execute()

        IoC.resolve('IoC.Register', 'dependency', lambda: 2).execute()
        self.assertEqual(2, IoC.resolve('dependency'))

        IoC.resolve('Scopes.Current.Set', scope_1).execute()
        self.assertEqual(1, IoC.resolve('dependency'))

    def test_resolving_dependency_depends_on_scope_hierarchy(self):
        root_scope = IoC.resolve('Scopes.Root')
        scope_1 = IoC.resolve('Scopes.New', root_scope)
        IoC.resolve('Scopes.Current.Set', scope_1).execute()

        IoC.resolve('IoC.Register', 'dependency_1', lambda: 1).execute()
        self.assertEqual(1, IoC.resolve('dependency_1'))

        with self.assertRaisesRegex(Exception, "Unknown dependency 'dependency_2'"):
            IoC.resolve('dependency_2')

        scope_2 = IoC.resolve('Scopes.New', scope_1)
        IoC.resolve('Scopes.Current.Set', scope_2).execute()
        IoC.resolve('IoC.Register', 'dependency_2', lambda: 2).execute()

        self.assertEqual(1, IoC.resolve('dependency_1'))
        self.assertEqual(2, IoC.resolve('dependency_2'))

        IoC.resolve('IoC.Register', 'dependency_1', lambda: 3).execute()
        self.assertEqual(3, IoC.resolve('dependency_1'))

        IoC.resolve('Scopes.Current.Set', scope_1).execute()
        self.assertEqual(1, IoC.resolve('dependency_1'))
        with self.assertRaisesRegex(Exception, "Unknown dependency 'dependency_2'"):
            IoC.resolve('dependency_2')

    def test_multithreading(self):
        scope = IoC.resolve('Scopes.New', IoC.resolve('Scopes.Root'))
        IoC.resolve('Scopes.Current.Set', scope).execute()
        IoC.resolve('IoC.Register', 'dependency', lambda: 1).execute()

        def thread_logic(parent_scope, thread_number):
            thread_scope = IoC.resolve('Scopes.New', parent_scope)
            IoC.resolve('Scopes.Current.Set', thread_scope).execute()
            self.assertEqual(1, IoC.resolve('dependency'))  # Проверяем, что можем читать из родительского скоупа

            # Проверяем, что каждый поток пользуется своим HierarchicalScopeBasedDependencyStrategy.current_scopes
            # благодаря threading.local()
            IoC.resolve('IoC.Register', 'thread_dependency', lambda: thread_number).execute()
            self.assertEqual(thread_number, IoC.resolve('thread_dependency'))

        threads = list()
        for i in range(100):
            thread = PropagateExceptionThread(target=thread_logic, args=(scope, i))
            threads.append(thread)

        # start threads
        for thread in threads:
            thread.start()

        # wait for threads to finish
        for thread in threads:
            thread.join()

        with self.assertRaisesRegex(Exception, "Unknown dependency 'thread_dependency'"):
            IoC.resolve('thread_dependency')
