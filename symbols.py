from arithmatic import ArithmaticsModel
from functions import list_elements_equality, split_arithmatic_array_on_operation
from copy import deepcopy


class SymbolBaseModel():
    def __init__(self, symbol, **kwargs):
        self.function = None
        self.simplified_arithmatics = None
        self.expanded_arithmatics = None
        self.arithmatics = kwargs.get('arithmatics') or []
        self.symbol = symbol

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def base_arithmatics(self, value, **kwargs):
        if not self.arithmatics:
            self = deepcopy(self)
        return self, value

    def new_symbol(self, **kwargs):
        return Symbol(
            symbol=self.symbol,
            arithmatics=kwargs['arithmatics']
        )

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
        if type(value) != type(self) and value == 1:
            return self
        self.arithmatics.append(
            ArithmaticsModel('*', value, 0)
        )
        return self
    def __rmul__(self, value, **kwargs):
        self, value = self.base_arithmatics(value)
        if type(value) != type(self) and value == 1:
            return self
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



class ExpandingFactoringModel(SymbolBaseModel):
    def simplify(self):
        if self.simplified_arithmatics == None:
            self.set_simplified_arithmatics()
        return super().create_function(
            function_type='simplify'
        )
    def set_simplified_arithmatics(self):
        self.simplified_arithmatics = self.simplify_arithmatics()

    def simplify_arithmatics(self, **kwargs):
        simplified_arithmatics = kwargs.get('input_arithmatics', [])
        arithmatics = deepcopy(simplified_arithmatics or self.arithmatics)
        simplified_arithmatics = []
        for arithmatic in arithmatics:
            result = arithmatic.simplify(
                simplified_arithmatics[-1],
                **kwargs
            ) if simplified_arithmatics else None
            if result:
                simplified_arithmatics[-1] = result
            else:
                simplified_arithmatics.append(arithmatic)

        return simplified_arithmatics

    def expand(self):
        if self.expanded_arithmatics == None:
            self.set_expanded_arithmatics()
        print('___________')
        print(self)
        print(self.arithmatics)
        print(self.simplified_arithmatics)
        print(self.expanded_arithmatics)
        self.expanded_arithmatics = self.simplify_arithmatics(
            input_arithmatics=self.expanded_arithmatics,
            avoid_simplification=['+', '-']
        )
        print(self.expanded_arithmatics)
        return super().create_function(
            function_type='expand'
        )

    def set_expanded_arithmatics(self):
        step = None
        arithmatic = None
        expanded_arithmatics = []
        if not self.simplified_arithmatics:
            self.set_simplified_arithmatics()
        arithmatics = deepcopy(self.simplified_arithmatics)
        if not arithmatics:
            self.expanded_arithmatics = []
            return
        for step, arithmatic in enumerate(arithmatics):
            if arithmatic.operation == '*':
                expanded_arithmatics = self.distribute_arithmatics(
                    expanded_arithmatics[:step] or arithmatics[:step],
                    arithmatic
                )
            else:
                expanded_arithmatics.append(arithmatic)
        expanded_arithmatics.extend(
            arithmatics[
                step if step == None or step == len(arithmatics) else step + 1:
            ]
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
        if type(arithmatic.value) == type(self):
            return self.distribute_symbol_types(
                arithmatic_array,
                arithmatic
            )
        elif not arithmatic_array:
            return [arithmatic]
        else:
            return self.distribute_real_number_types(
                arithmatic_array,
                arithmatic
            )

    def distribute_symbol_types(self, arithmatic_array, arithmatic):
        arithmatic.value.expand()
        target_expanded = arithmatic.value.expanded_arithmatics
        target_splitted = split_arithmatic_array_on_operation(
            target_expanded,
            ['+', '-']
        )
        array_splitted = split_arithmatic_array_on_operation(
            arithmatic_array,
            ['+', '-']
        )
        symbol_1 = ArithmaticsModel(
            operation='*',
            value=self.new_symbol(
                arithmatics=array_splitted[0]
            ),
            side='1'
        )
        symbol_2 = ArithmaticsModel(
            operation='*',
            value=arithmatic.value.new_symbol(
                arithmatics=target_splitted[0]
            ),
            side='1'
        )
        d_a = deepcopy(array_splitted[0]) if array_splitted[0] else []
        for step, target in enumerate(target_splitted):
            if step == 0:
                symbol_2 = ArithmaticsModel(
                    operation='*',
                    value=arithmatic.value.new_symbol(
                        arithmatics=target
                    ),
                    side='1'
                )
                d_a.append(symbol_2)
                if array_splitted[1]:
                    d_a.append(symbol_2.combine(array_splitted[1]))
            else:
                if target:
                    d_a.append(
                        target.combine(
                            symbol_1,
                            result_operation='+',
                            operation_applied='*')
                    )
                    if array_splitted[1]:
                        d_a.append(
                            target.combine(
                                array_splitted[1],
                                result_operation='+',
                                operation_applied='*')
                        )
        import ipdb
        ipdb.set_trace()
        [x.update(side=0) for x in d_a if x]
        return [x for x in d_a if x]


    def distribute_real_number_types(self, arithmatic_array, arithmatic):
        distributed_array = []
        for step, target in enumerate(arithmatic_array):
            if target.operation == '**':
                distributed_array.extend([target, arithmatic])
            elif target.operation in ['+', '-']:
                if step == 0:
                    distributed_array.append(arithmatic)
                distributed_array.append(
                    arithmatic.combine(target)
                )
            elif target.operation in ['*', '/']:
                distributed_array.append(
                    target.combine(arithmatic)
                )
            else:
                raise ValueError(
                    'operation {} is not supported'.format(
                        target.operation)
                )

        return distributed_array


class Symbol(ExpandingFactoringModel):
    pass
