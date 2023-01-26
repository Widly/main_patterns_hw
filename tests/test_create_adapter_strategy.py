from unittest import TestCase
from unittest.mock import Mock, patch

from features.base.commands import InitCreateCommandAdapterStrategy
from features.base.interfaces import UObject
from iocs import IoC
from iocs.scope_based_strategy import InitScopesCommand


class IActionable:
    def get_field_1(self):
        ...

    def set_field_1(self, value):
        ...

    def get_field_2(self):
        ...


class IAnotherActionable:
    def get_field_1(self):
        ...

    def get_field_3(self):
        ...


class TestCreateCommandAdapterStrategy(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        InitScopesCommand().execute()

    def setUp(self) -> None:
        # Создаем новый скоуп чтобы не вносить зависимости в Root скоуп
        IoC.resolve('Scopes.New', 'scope-id')
        IoC.resolve('Scopes.Current.Set', 'scope-id').execute()

        # Инициализация стратегии
        InitCreateCommandAdapterStrategy().execute()

    def tearDown(self) -> None:
        IoC.resolve('Scopes.Current.Set', 'ROOT').execute()
        IoC.resolve('Scopes.Clear').execute()

    def test_interface_getter_method(self):
        obj = Mock(UObject)
        actionable = IoC.resolve("Adapter", IActionable, obj)

        with patch('iocs.base.IoC.resolve') as mocked_resolve:
            mocked_resolve_return = Mock()
            mocked_resolve.return_value = mocked_resolve_return

            output = actionable.get_field_1()
            self.assertEqual(mocked_resolve_return, output)  # Возвращается результат геттера
            mocked_resolve.assert_called_with('IActionable:field_1.get', obj)
            mocked_resolve_return.execute.assert_not_called()

    def test_interface_setter_method(self):
        obj = Mock(UObject)
        actionable = IoC.resolve("Adapter", IActionable, obj)

        with patch('iocs.base.IoC.resolve') as mocked_resolve:
            mocked_resolve_return = Mock()
            mocked_resolve.return_value = mocked_resolve_return

            output = actionable.set_field_1('value 1')
            self.assertEqual(None, output)  # Вызов сеттера ничего не возвращает
            mocked_resolve.assert_called_with('IActionable:field_1.set', obj, 'value 1')
            mocked_resolve_return.execute.assert_called_with()  # Внутри адаптера выполняется возвращаемая IoC команда

    def test_create_two_diffrent_adapters(self):
        """Тестируем создание двух адаптеров подряд для двух различных интерфейсов"""
        obj = Mock(UObject)
        actionable = IoC.resolve("Adapter", IActionable, obj)

        # Проверяем, что вызовы методов адаптера транслируются в вызовы IoC
        with patch('iocs.base.IoC.resolve') as mocked_resolve:
            actionable.get_field_1()
            mocked_resolve.assert_called_with('IActionable:field_1.get', obj)

            actionable.set_field_1('value 1')
            mocked_resolve.assert_called_with('IActionable:field_1.set', obj, 'value 1')

            actionable.get_field_2()
            mocked_resolve.assert_called_with('IActionable:field_2.get', obj)

        # Проверяем, что для нового интерфейса создается совершенно новый адаптер,
        # вызовы которого транслируются в другие вызовы IoC
        another_actionable = IoC.resolve("Adapter", IAnotherActionable, obj)
        self.assertNotEqual(actionable.__class__, another_actionable.__class__)

        with patch('iocs.base.IoC.resolve') as mocked_resolve:
            another_actionable.get_field_1()
            mocked_resolve.assert_called_with('IAnotherActionable:field_1.get', obj)

            with self.assertRaises(AttributeError):
                # Этого метода нет в IAnotherActionable -> ошибка
                another_actionable.get_field_2()

            another_actionable.get_field_3()
            mocked_resolve.assert_called_with('IAnotherActionable:field_3.get', obj)
