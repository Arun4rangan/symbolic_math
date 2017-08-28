def list_elements_equality(list_1, list_2):
    if len(list_1) != len(list_2):
        return False
    return all([list_1[x] == list_2[x] for x in range(len(list_1))])


def split_arithmatic_array_on_operation(array, types):
    spliting_step = [
        x for x in range(len(array))
        if array[x].operation in types
    ]
    if spliting_step == []:
        return (array, None)
    previous_step = None
    split_array = []
    split_array.append(array[0:spliting_step[0]] or None)
    for x in spliting_step:
        split_array.append(array[x])
    return split_array
