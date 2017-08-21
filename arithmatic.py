from copy import deepcopy


class ArithmaticsModel():
    connected_operations = {
        '+': '-',
        '-': '+',
        '*': '/',
        '/': '*',
    }
    def __init__(self, operation, value, side):
        self.operation = operation
        self.value = value
        self.side = side

    def __repr__(self):
        return '[%s,%s,%s]' % (self.operation, self.value, self.side)

    def get_value(self, function_type):
        symbol_type = getattr(self.value, 'create_function', None)
        if symbol_type:
            return self.value.create_function(function_type)
        return self.value

    def simplify(self, target):
        if target and (
                self.operation == target.operation or
                self.connected_operations[target.operation] == self.operation
        ):
            return self.combine(target)

    def combine(self, target):
        if self.operation == '+':
            result = target.value + self.value
        elif self.operation == '-':
            result = target.value - self.value
        elif self.operation == '*':
            result = target.value * self.value
        elif self.operation == '/':
            result = target.value / self.value
        elif self.operation == '**':
            result = target.value ** self.value
        else:
            raise ValueError(
                'operation {} is not supported'.format(self.operation)
            )

        return ArithmaticsModel(
            operation=target.operation,
            value=result,
            side=target.side
        )
