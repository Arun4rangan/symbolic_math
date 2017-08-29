from copy import deepcopy

from arithmatic import ArithmaticsModel
from functions import split_arithmatic_array_on_operation


class SymbolBaseModel():
    def __init__(self, symbol, **kwargs):
        self.function = None
        self.simplified_arithmatics = None
        self.expanded_arithmatics = None
        self.arithmatics = kwargs.get('arithmatics') or []
        self.symbol = symbol

    def __eq__(self, other):
        if other is None or type(self) != type(other):
            return False
        return self.__dict__ == other.__dict__

    def base_arithmatics(self, value, **kwargs):
        if not self.arithmatics:
            self = deepcopy(self)
        return self, value

    def new_symbol(self, **kwargs):
        return self.__class__(
            symbol=self.symbol,
            arithmatics=deepcopy(kwargs['arithmatics'])
        )

    def apply_operation(self, arithmatic):
        operations = {
            '+': self.__add__,
            '-': self.__sub__,
            '*': self.__mul__,
            '/': self.__truediv__,
            '**': self.__pow__
        }
        return operations[arithmatic.operation](arithmatic.value)

    def common_adding(self, value):
        if type(value) == type(self) and value.symbol == self.symbol:
            array = split_arithmatic_array_on_operation(
                self.arithmatics,
                ['-', '+']
            )[0]
            target = split_arithmatic_array_on_operation(
                value.arithmatics,
                ['-', '+']
            )[0]
            if array is None or target is None:
                return
            max_lng = max(len(array), len(target))
            min_lng = min(len(array), len(target))
            if value.arithmatics == self.arithmatics:
                return self.__mul__(2)
            if (
                min_lng + 1 >= max_lng
                and array[:max_lng - 1] == target[:max_lng - 1]
            ):
                l_o = array[-1] if array else None
                l_ot = target[-1] if target else None
                if max_lng == min_lng:
                    if l_o.operation == '*' and l_ot.operation == '*':
                        l_o.value = l_o.value + l_ot.value
                        return self
                else:
                    if len(array) > len(target) and l_o.operation == '*':
                        l_o.value = l_o.value + 1
                        return self
                    elif l_ot and l_ot.operation == '*':
                        return self.arithmatics[0].value.__mul__(l_ot.value + 1)

    def common_multiple(self, value):
        if type(value) == type(self) and value.symbol == self.symbol:
            array = split_arithmatic_array_on_operation(
                self.arithmatics,
                ['-', '+']
            )
            target = split_arithmatic_array_on_operation(
                value.arithmatics,
                ['-', '+']
            )
            if array[-1] != None or target[-1] != None:
                return
            first_arith = self.arithmatics[0] if self.arithmatics else None
            target_arith = value.arithmatics[0] if value.arithmatics else None
            skip_first = False

            if not first_arith and not target_arith:
                return self.__pow__(2)
            elif (
                target_arith
                and target_arith.operation == '**'
                and (not first_arith
                     or first_arith.operation != '**')
            ):
                self.arithmatics.insert(
                    0,
                    ArithmaticsModel(
                        operation='**',
                        value=target_arith.value + 1,
                        side=0
                    )
                )
                skip_first = True
            elif (
                first_arith
                and first_arith.operation == '**'
                and (not target_arith
                     or target_arith.operation != '**')
            ):
                first_arith.value = first_arith.value + 1
            elif (
                first_arith
                and target_arith
                and first_arith.operation == '**'
                and target_arith.operation == '**'
            ):
                first_arith.value = first_arith.value + target_arith.value
                skip_first = True
            else:
                self.arithmatics.insert(
                    0,
                    ArithmaticsModel(
                        operation='**',
                        value=2,
                        side=0
                    )
                )

            for x in value.arithmatics[1 if skip_first else 0:]:
                self = self.apply_operation(x)

            return self


    def __radd__(self, value, **kwargs):
        self, value = self.base_arithmatics(value)

        result = self.common_adding(value)

        if result:
            return result
        self.arithmatics.append(
            ArithmaticsModel('+', value, 1)
        )
        return self

    def __add__(self, value, **kwargs):
        self, value = self.base_arithmatics(value)

        result = self.common_adding(value)

        if result:
            return result

        self.arithmatics.append(
            ArithmaticsModel('+', value, 0)
        )
        return self

    def __mul__(self, value, **kwargs):
        self, value = self.base_arithmatics(value)
        if type(value) != type(self) and value == 1:
            return self

        result = self.common_multiple(value)

        if result:
            return result

        self.arithmatics.append(
            ArithmaticsModel('*', value, 0)
        )
        return self
    def __rmul__(self, value, **kwargs):
        self, value = self.base_arithmatics(value)

        if type(value) != type(self) and value == 1:
            return self

        result = self.common_multiple(value)

        if result:
            return result

        self.arithmatics.append(
            ArithmaticsModel('*', value, 1)
        )
        return self
    def __truediv__(self, value, **kwargs):
        self, value = self.base_arithmatics(value)
        if type(value) != type(self) and value == 1:
            return self
        self.arithmatics.append(
            ArithmaticsModel('/', value, 0)
        )
        return self
    def __rtruediv__(self, value, **kwargs):
        self, value = self.base_arithmatics(value)
        if type(value) != type(self) and value == 1:
            return self
        self.arithmatics.append(
            ArithmaticsModel('/', value, 1)
        )
        return self
    def __sub__(self, value, **kwargs):
        self, value = self.base_arithmatics(value)
        self.arithmatics.append(
            ArithmaticsModel('-', value, 0)
        )
        return self
    def __rsub__(self, value, **kwargs):
        self, value = self.base_arithmatics(value)
        self.arithmatics.append(
            ArithmaticsModel('-', value, 1)
        )
        return self

    def __pow__(self, value, **kwargs):
        self, value = self.base_arithmatics(value)
        self.arithmatics.append(
            ArithmaticsModel('**', value, 0)
        )
        return self

    def __rpow__(self, value, **kwargs):
        self, value = self.base_arithmatics(value)
        self.arithmatics.append(
            ArithmaticsModel('**', value, 1)
        )
        return self

    def __repr__(self):
        return self.create_function()

    def set_function(self):
        variables = set(
            x.value.symbol for x in self.arithmatics
            if type(x.value) is type(self)
        )
        variables.add(self.symbol)
        self.function = eval(
            'lambda ' + ','.join(variables) + ':' + self.create_function()
        )
        return

    def evaluate(self, **kwargs):
        if self.function is None:
            self.set_function()
        return self.function(**kwargs)

    def find_arithmatics(self, function_type):
        pass

    def create_function(self, function_type=None, **kwargs):
        previous_arithmatic = None
        bracket = False
        arithmatics = self.find_arithmatics(function_type)
        function = self.symbol
        for step, arithmatic in enumerate(arithmatics):
            bracket = True
            if (
                arithmatic.operation in ['+', '-']
                or step == 0
            ):
                bracket = False

            if arithmatic.side:
                function = '{}{}{}'.format(
                    arithmatic.get_value(function_type, bracket=bracket),
                    arithmatic.operation,
                    '(' if bracket else ''
                ) + function + '{}'.format(')' if bracket else '')
            else:
                function = '{}'.format(
                    '(' if bracket else ''
                ) + function + '{}{}{}'.format(
                    ')' if bracket else '',
                    arithmatic.operation,
                    arithmatic.get_value(function_type, bracket=bracket)
                )
            previous_arithmatic = arithmatic
        return '(' + function + ')' if kwargs.get('bracket') else function
