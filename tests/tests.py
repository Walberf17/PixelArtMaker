a = (0, 0, 0, 0)


def make_it_darker(color):
    print(color)
    dark_val = -10
    new_color = list()
    for val in color[:3]:
        new_color.append(val + dark_val)
    new_color.append(color[-1])
    return new_color


def make_it_lighter(color):
    print(color)
    light_val = 10
    new_color = list()
    for val in color[:3]:
        new_color.append(val + light_val)
    new_color.append(color[-1])
    return new_color

print(make_it_lighter(a))