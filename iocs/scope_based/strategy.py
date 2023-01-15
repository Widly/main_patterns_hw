import threading

from features.base.interfaces import ICommand
from iocs.base import IoC


class Scope:
    def __init__(self, dependencies, parent=None):
        self.dependencies = dependencies
        self.parent = parent

    def resolve(self, key, *args, **kwargs):
        if key in self.dependencies:
            return self.dependencies[key](*args, **kwargs)
        elif self.parent:
            return self.parent.resolve(key, *args, **kwargs)
        else:
            raise KeyError(f"Unknown dependency '{key}'")


class HierarchicalScopeBasedDependencyStrategy:
    """
    Стратегия разрешения зависимостей использующая Скоупы между которыми установлена иерархия.
    В случае отсутствия зависимости в текущем Скоупе поиск ведется в родительском Скоупе и так далее
    """

    root: Scope = None
    current_scopes = threading.local()

    @classmethod
    def get_current_scope(cls):
        return getattr(cls.current_scopes, 'value', None)

    @classmethod
    def get_default_scope(cls):
        return cls.root

    @classmethod
    def resolve(cls, key, *args, **kwargs):
        if key == 'Scopes.Root':
            return cls.root

        scope = cls.get_current_scope()
        if scope is None:
            scope = cls.get_default_scope()

        return scope.resolve(key, *args, **kwargs)


class SetCurrentScopeCommand(ICommand):
    """
    Устанавливает Scope для текущего потока. По итогу разные потоки могут иметь различный активный Scope.
    Работает благодаря threading.local() в HierarchicalScopeBasedDependencyStrategy.current_scopes
    """

    def __init__(self, scope):
        self.scope = scope

    def execute(self) -> None:
        HierarchicalScopeBasedDependencyStrategy.current_scopes.value = self.scope


class RegisterIoCDependencyCommand(ICommand):
    """Регистрация зависимости"""

    def __init__(self, key, strategy):
        self.key = key
        self.strategy = strategy

    def execute(self) -> None:
        scope = HierarchicalScopeBasedDependencyStrategy.current_scopes.value
        if scope:
            if self.key in scope.dependencies:
                raise Exception('Dependency already registered')
            else:
                scope.dependencies[self.key] = self.strategy
        else:
            raise Exception('Cannot register dependency - unknown scope')


class InitScopesCommand(ICommand):
    """Инициализация стратегии HierarchicalScopeBasedDependencyStrategy"""

    def execute(self) -> None:
        if HierarchicalScopeBasedDependencyStrategy.root is not None:
            return

        IoC.resolve("IoC.SetupStrategy", HierarchicalScopeBasedDependencyStrategy.resolve).execute()

        root_dependencies = {}
        root_scope = Scope(root_dependencies)

        root_dependencies['Scopes.Storage'] = lambda: {}
        root_dependencies['Scopes.New'] = lambda parent_scope: Scope(IoC.resolve('Scopes.Storage'), parent_scope)

        root_dependencies['Scopes.Current'] = HierarchicalScopeBasedDependencyStrategy.get_current_scope
        root_dependencies['Scopes.Current.Set'] = lambda scope: SetCurrentScopeCommand(scope)

        root_dependencies['IoC.Register'] = lambda key, strategy: RegisterIoCDependencyCommand(key, strategy)

        HierarchicalScopeBasedDependencyStrategy.root = root_scope
        SetCurrentScopeCommand(root_scope).execute()
