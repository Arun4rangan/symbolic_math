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
        self.arithmatics.append(['+', value, 1])
        return self
    def __add__(self, value, **kwargs):
        self, value = self.base_arithmatics(value)
        self.arithmatics.append(['+', value, 0])
        return self
    def __mul__(self, value, **kwargs):
        self, value = self.base_arithmatics(value)
        self.arithmatics.append(['*', value, 0])
        return self
    def __rmul__(self, value, **kwargs):
        self, value = self.base_arithmatics(value)
        self.arithmatics.append(['*', value, 1])
        return self
    def __truediv__(self, value, **kwargs):
        self, value = self.base_arithmatics(value)
        self.arithmatics.append(['/', value, 0])
        return self
    def __rtruediv__(self, value, **kwargs):
        self, value = self.base_arithmatics(value)
        self.arithmatics.append(['/', value, 1])
        return self
    def __sub__(self, value, **kwargs):
        self, value = self.base_arithmatics(value)
        self.arithmatics.append(['-', value, 0])
        return self
    def __rsub__(self, value, **kwargs):
        self, value = self.base_arithmatics(value)
        self.arithmatics.append(['-', value, 1])
        return self

    def __pow__(self, value, **kwargs):
        self, value = self.base_arithmatics(value)
        self.arithmatics.append(['**', value, 0])
        return self

    def __rpow__(self, value, **kwargs):
        self, value = self.base_arithmatics(value)
        self.arithmatics.append(['**', value, 1])
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
        bracket = False
        arithmatics = self.find_arithmatics(function_type)
        function = self.symbol
        for arithmatic in arithmatics:
            bracket = False
            operation = arithmatic[0]
            value = arithmatic[1]
            side = arithmatic[2]

            if type(value) == type(self):
                value = value.create_function(function_type)

            if operation in ['+', '-']:
                bracket = True

            if side:
                function = '{}{}{}'.format(
                    '(' if bracket else '',
                    value,
                    operation
                ) + function + '{}'.format(')' if bracket else '')
            else:
                function = '{}'.format(
                    '(' if bracket else ''
                ) + function + '{}{}{}'.format(
                    operation,
                    value,
                    ')' if bracket else ''
                )

        return '(' + function + ')' if not bracket else function


class ExpandingFactoringModel(SymbolBaseModel):
    def simplify(self):
        if not self.simplified_arithmatics:
            self.set_simplified_arithmatics()
        return super().create_function(
            function_type='simplify'
        )

    def expand(self):
        if not self.expanded_arithmatics:
            self.set_expanded_arithmatics()
        return super().create_function(
            function_type='expand'
        )

    def set_expanded_arithmatics(self):
        if self.simplified_arithmatics is None:
            self.set_simplified_arithmatics()
        arithmatics = deepcopy(self.simplified_arithmatics)
        for arithmatic in arithmatics:
            operation = arithmatic[0]
            value = arithmatic[1]
            if type(value) == type(self):
                pass

    def set_simplified_arithmatics(self):
        simplified_arithmatics = []
        previous_operation = None
        arithmatics = deepcopy(self.simplified_arithmatics or self.arithmatics)
        for arithmatic in arithmatics:
            operation = arithmatic[0]
            value = arithmatic[1]
            if operation == previous_operation:
                if operation == '+':
                    simplified_arithmatics[-1][1] += value
                elif operation == '*':
                    simplified_arithmatics[-1][1] *= value
                elif operation == '/':
                    simplified_arithmatics[-1][1] /= value
                elif operation == '**':
                    simplified_arithmatics[-1][1] **= value
                else:
                    raise ValueError('operation %s is not supported')
            else:
                simplified_arithmatics.append(arithmatic)

            previous_operation = operation

        self.simplified_arithmatics = simplified_arithmatics

    def find_arithmatics(self, function_type):
        if function_type == 'simplify':
            if not self.simplified_arithmatics:
                self.set_simplified_arithmatics()
            return self.simplified_arithmatics

        return self.arithmatics

    def distribute_operation(self, arithmatic_array, operation):
        for arithmatic in arithmatic_array:
            operation = arithmatic[0]
            value = arithmatic[1]



class Symbol(ExpandingFactoringModel):
    pass
