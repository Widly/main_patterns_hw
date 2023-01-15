from features.base.interfaces import ICommand


class IoC:
    @classmethod
    def resolve(cls, key, *args, **kwargs):
        return cls.strategy(key, *args, **kwargs)

    @staticmethod
    def default_strategy(key, *args, **kwargs):
        """
        Дефолтная стратегия разрешения зависимостей.
        Имеет внутри только одну зависимость - IoC.SetupStrategy, которая служит только для того,
        чтобы для этого IoC можно было установить произвольную реализацию стратегии разрешения зависимостей.
        """
        if key == 'IoC.SetupStrategy':
            return SetupStrategyCommand(args[0])
        else:
            raise KeyError(f"Unknown dependency '{key}'")

    strategy = default_strategy


class SetupStrategyCommand(ICommand):
    """Устанавливает стратегию разрешения зависимостей для IoC."""

    def __init__(self, new_strategy):
        self.new_strategy = new_strategy

    def execute(self) -> None:
        IoC.strategy = self.new_strategy
