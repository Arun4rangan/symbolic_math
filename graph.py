from itertools import product
from matplotlib import cm
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

from symbols_base import SymbolBaseModel


class GraphModel(SymbolBaseModel):
    def graph(self):
        if not self.function:
            self.set_function()

        var_count = self.function.__code__.co_argcount
        variables = self.function.__code__.co_varnames
        step_array = [step for step in range(-25, 25)]
        result = [
            (*d, self.function(*d))
            for d in product(step_array, repeat=var_count)
        ]
        fig = plt.figure()
        if var_count == 2:
            ax = fig.add_subplot(111, projection='3d')
            ax.scatter(
                *zip(*result),
                c=cm.autumn([x for x in zip(*result)][-1]),
            )
            ax.set_xlabel(variables[0] + ' axis')
            ax.set_ylabel(variables[1] + ' axis')
        elif var_count == 1:
            ax = fig.add_subplot(111)
            ax.scatter(
                *zip(*result),
                c=cm.autumn([x for x in zip(*result)][-1]),
            )
            ax.set_xlabel(variables[0] + ' axis')
        else:
            raise NotImplementedError(
                'Can only create graphs for two '
                + 'or one variable function\n Cannot create function'
                + ' for {} variable function'.format(
                    var_count)
            )

        plt.title(self.create_function())
        plt.show()
