from threading import Thread
from unittest import TestCase

from iocs import IoC
from iocs.scope_based_strategy import Scope, InitScopesCommand


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

    def tearDown(self) -> None:
        IoC.resolve('Scopes.Current.Set', 'ROOT').execute()
        IoC.resolve('Scopes.Clear').execute()

    def test_root_scope_is_available(self):
        self.assertIsInstance(IoC.resolve('Scopes.Root'), Scope)

    def test_default_current_scope_is_root(self):
        root_scope = IoC.resolve('Scopes.Root')
        current_scope = IoC.resolve('Scopes.Current')
        self.assertEqual(root_scope, current_scope)

    def test_create_scopes_storage(self):
        self.assertEqual({}, IoC.resolve('Scopes.Storage'))

    def test_create_new_scope(self):
        new_scope = IoC.resolve('Scopes.New', 'scope-id')
        self.assertIsInstance(new_scope, Scope)
        self.assertNotEqual(IoC.resolve('Scopes.Root'), new_scope)

    def test_set_scope(self):
        new_scope = IoC.resolve('Scopes.New', 'scope-id')
        IoC.resolve('Scopes.Current.Set', 'scope-id').execute()
        self.assertEqual(new_scope, IoC.resolve('Scopes.Current'))

    def test_register_dependency(self):
        IoC.resolve('Scopes.New', 'scope-id')
        IoC.resolve('Scopes.Current.Set', 'scope-id').execute()

        IoC.resolve('IoC.Register', 'dependency', lambda: 1).execute()
        self.assertEqual(1, IoC.resolve('dependency'))

        with self.assertRaisesRegex(Exception, 'Dependency already registered'):
            IoC.resolve('IoC.Register', 'dependency', lambda: 2).execute()

    def test_resolving_dependency_depends_on_current_scope(self):
        IoC.resolve('Scopes.New', 'scope-id-1')
        IoC.resolve('Scopes.Current.Set', 'scope-id-1').execute()

        IoC.resolve('IoC.Register', 'dependency', lambda: 1).execute()
        self.assertEqual(1, IoC.resolve('dependency'))

        IoC.resolve('Scopes.New', 'scope-id-2')
        IoC.resolve('Scopes.Current.Set', 'scope-id-2').execute()

        IoC.resolve('IoC.Register', 'dependency', lambda: 2).execute()
        self.assertEqual(2, IoC.resolve('dependency'))

        IoC.resolve('Scopes.Current.Set', 'scope-id-1').execute()
        self.assertEqual(1, IoC.resolve('dependency'))

    def test_resolving_dependency_depends_on_scope_hierarchy(self):
        IoC.resolve('Scopes.New', 'scope-id-1')
        IoC.resolve('Scopes.Current.Set', 'scope-id-1').execute()

        IoC.resolve('IoC.Register', 'dependency_1', lambda: 1).execute()
        self.assertEqual(1, IoC.resolve('dependency_1'))

        with self.assertRaisesRegex(Exception, "Unknown dependency 'dependency_2'"):
            IoC.resolve('dependency_2')

        IoC.resolve('Scopes.New', 'scope-id-2')
        IoC.resolve('Scopes.Current.Set', 'scope-id-2').execute()
        IoC.resolve('IoC.Register', 'dependency_2', lambda: 2).execute()

        self.assertEqual(1, IoC.resolve('dependency_1'))
        self.assertEqual(2, IoC.resolve('dependency_2'))

        IoC.resolve('IoC.Register', 'dependency_1', lambda: 3).execute()
        self.assertEqual(3, IoC.resolve('dependency_1'))

        IoC.resolve('Scopes.Current.Set', 'scope-id-1').execute()
        self.assertEqual(1, IoC.resolve('dependency_1'))
        with self.assertRaisesRegex(Exception, "Unknown dependency 'dependency_2'"):
            IoC.resolve('dependency_2')

    def test_multithreading(self):
        IoC.resolve('Scopes.New', 'parent-scope-id')
        IoC.resolve('Scopes.Current.Set', 'parent-scope-id').execute()
        IoC.resolve('IoC.Register', 'dependency', lambda: 1).execute()

        def thread_logic(parent_scope_id, thread_number):
            scope_id = f'scope-id-{thread_number}'
            IoC.resolve('Scopes.New', scope_id, parent_scope_id)
            IoC.resolve('Scopes.Current.Set', scope_id).execute()
            self.assertEqual(1, IoC.resolve('dependency'))  # Проверяем, что можем читать из родительского скоупа

            # Проверяем, что каждый поток пользуется своим HierarchicalScopeBasedDependencyStrategy.current_scopes
            # благодаря threading.local()
            IoC.resolve('IoC.Register', 'thread_dependency', lambda: thread_number).execute()
            self.assertEqual(thread_number, IoC.resolve('thread_dependency'))

        threads = list()
        for i in range(100):
            thread = PropagateExceptionThread(target=thread_logic, args=('parent-scope-id', i))
            threads.append(thread)

        # start threads
        for thread in threads:
            thread.start()

        # wait for threads to finish
        for thread in threads:
            thread.join()

        with self.assertRaisesRegex(Exception, "Unknown dependency 'thread_dependency'"):
            IoC.resolve('thread_dependency')
