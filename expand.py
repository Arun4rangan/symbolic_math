from copy import deepcopy

from arithmatic import ArithmaticsModel
from functions import split_arithmatic_array_on_operation
from symbols_base import SymbolBaseModel


class ExpandModel(SymbolBaseModel):
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

        self.expanded_arithmatics = self.simplify_arithmatics(
            input_arithmatics=self.expanded_arithmatics,
            restricted_simplification=['+', '-']
        )

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
        arithmatic.value.set_expanded_arithmatics()
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
        d_a = []
        for step, target in enumerate(target_splitted):
            if step == 0:
                symbol_2 = ArithmaticsModel(
                    operation='*',
                    value=arithmatic.value.new_symbol(
                        arithmatics=target
                    ),
                    side='1'
                )
                d_a.extend(
                    (self.new_symbol(
                        arithmatics=array_splitted[0]
                    ) * arithmatic.value.new_symbol(
                        arithmatics=target
                    )).arithmatics
                )
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
