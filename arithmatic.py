from copy import deepcopy


class ArithmaticsModel():
    connected_operations = {
        '+': '-',
        '-': '+',
        '*': '/',
        '/': '*',
        '**': None
    }
    def __init__(self, operation, value, side):
        self.operation = operation
        self.value = value
        self.side = side

    def update(self, **kwargs):
        self.operation = kwargs.get('operation', self.operation)
        self.value = kwargs.get('value', self.value)
        self.side = kwargs.get('side', self.side)

    def __eq__(self, other):
        if other is None:
            return False
        return self.__dict__ == other.__dict__

    def __repr__(self):
        return '[%s,%s,%s]' % (self.operation, self.value, self.side)

    def get_value(self, function_type, **kwargs):
        symbol_type = getattr(self.value, 'create_function', None)
        if symbol_type:
            return self.value.create_function(function_type, **kwargs)
        return self.value

    def simplify(self, target, **kwargs):
        r_s = kwargs.get('restricted_simplification', [])
        if target.operation in r_s:
            if type(self.value) != type(target.value):
                return

        if target and (
                self.operation == target.operation or
                self.connected_operations[target.operation] == self.operation
        ):
            return self.combine(target)

    def combine(self, target, **kwargs):
        if not target:
            return None
        target_value = deepcopy(target.value)
        value = deepcopy(self.value)
        operation = kwargs.get('operation_applied') or self.operation
        result_operation = kwargs.get('result_operation') or target.operation
        if operation == '+':
            result = target_value + value
        elif operation == '-':
            result = target_value - value
        elif operation == '*':
            result = target_value * value
        elif operation == '/':
            result = target_value / value
        elif operation == '**':
            result = target_value ** value
        else:
            raise ValueError(
                'operation {} is not supported'.format(self.operation)
            )

        return ArithmaticsModel(
            operation=result_operation,
            value=result,
            side=target.side
        )
