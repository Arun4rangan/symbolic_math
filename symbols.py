from arithmatic import ArithmaticsModel
from copy import deepcopy


class SymbolBaseModel():
    def __init__(self, symbol):
        self.function = None
        self.simplified_arithmatics = None
        self.expanded_arithmatics = None
        self.arithmatics = []
        self.symbol = symbol

    def base_arithmatics(self, value, **kwargs):
        if not self.arithmatics:
            self = deepcopy(self)
        return self, value

    def __radd__(self, value, **kwargs):
        self, value = self.base_arithmatics(value)
        self.arithmatics.append(
            ArithmaticsModel('+', value, 1)
        )
        return self
    def __add__(self, value, **kwargs):
        self, value = self.base_arithmatics(value)
        self.arithmatics.append(
            ArithmaticsModel('+', value, 0)
        )
        return self
    def __mul__(self, value, **kwargs):
        self, value = self.base_arithmatics(value)
        self.arithmatics.append(
            ArithmaticsModel('*', value, 0)
        )
        return self
    def __rmul__(self, value, **kwargs):
        self, value = self.base_arithmatics(value)
        self.arithmatics.append(
            ArithmaticsModel('*', value, 1)
        )
        return self
    def __truediv__(self, value, **kwargs):
        self, value = self.base_arithmatics(value)
        self.arithmatics.append(
            ArithmaticsModel('/', value, 0)
        )
        return self
    def __rtruediv__(self, value, **kwargs):
        self, value = self.base_arithmatics(value)
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
            x[1].symbol for x in self.arithmatics if type(x[1]) is type(self)
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

    def create_function(self, function_type=None):
        previous_arithmatic = None
        bracket = False
        arithmatics = self.find_arithmatics(function_type)
        function = self.symbol
        for arithmatic in arithmatics:
            bracket = True

            if previous_arithmatic and (
                arithmatic.operation in ['+', '-']
                or previous_arithmatic.operation == arithmatic.operation
            ):
                bracket = False

            if arithmatic.side:
                function = '{}{}{}'.format(
                    arithmatic.get_value(function_type),
                    arithmatic.operation,
                    '(' if bracket else ''
                ) + function + '{}'.format(')' if bracket else '')
            else:
                function = '{}'.format(
                    '(' if bracket else ''
                ) + function + '{}{}{}'.format(
                    ')' if bracket else '',
                    arithmatic.operation,
                    arithmatic.get_value(function_type)
                )
            previous_arithmatic = arithmatic
        return '(' + function + ')'



class ExpandingFactoringModel(SymbolBaseModel):
    def simplify(self):
        if not self.simplified_arithmatics:
            self.set_simplified_arithmatics()
        return super().create_function(
            function_type='simplify'
        )

    def set_simplified_arithmatics(self):
        simplified_arithmatics = []
        previous_arithmatic = None

        arithmatics = deepcopy(self.simplified_arithmatics or self.arithmatics)
        for arithmatic in arithmatics:
            result = arithmatic.simplify(previous_arithmatic)
            if result:
                simplified_arithmatics[-1] = result
            else:
                simplified_arithmatics.append(arithmatic)

            previous_arithmatic = arithmatic

        self.simplified_arithmatics = simplified_arithmatics

    def expand(self):
        if not self.expanded_arithmatics:
            self.set_expanded_arithmatics()
        return super().create_function(
            function_type='expand'
        )

    def set_expanded_arithmatics(self):
        import ipdb
        ipdb.set_trace()
        if not self.simplified_arithmatics:
            self.set_simplified_arithmatics()
        arithmatics = deepcopy(self.simplified_arithmatics)
        expanded_arithmatics = []
        for item, arithmatic in enumerate(arithmatics):
            if arithmatic.operation == '*':
                expanded_arithmatics.extend(
                    self.distribute_arithmatics(
                        expanded_arithmatics or arithmatics[:item],
                        arithmatic
                    )
                )
                break
        expanded_arithmatics.extend(
            arithmatics[item + 1 if arithmatic.operation == '*' else item:]
        )
        self.expanded_arithmatics = expanded_arithmatics

    def find_arithmatics(self, function_type):
        if function_type == 'simplify':
            if not self.simplified_arithmatics:
                self.set_simplified_arithmatics()
            return self.simplified_arithmatics
        elif function_type == 'expand':
            if not self.expanded_arithmatics:
                self.set_expanded_arithmatics()
            return self.expanded_arithmatics

        return self.arithmatics

    def distribute_arithmatics(self, arithmatic_array, arithmatic):
        import ipdb
        ipdb.set_trace
        distributed_array = []
        arithmatic_array = deepcopy(arithmatic_array)
        for item, target in enumerate(arithmatic_array):
            if target.operation == '**':
                distributed_array.extend([target, arithmatic])
            elif target.operation in ['+', '-']:
                distributed_array.extend(
                    [
                        arithmatic,
                        arithmatic.combine(target)
                    ]
                )
            elif target.operation in ['*', '/']:
                distributed_array.append(
                    target.combine(arithmatic)
                )
            else:
                raise ValueError(
                    'operation {} is not supported'.format(target.operation)
                )


        return distributed_array


class Symbol(ExpandingFactoringModel):
    pass
