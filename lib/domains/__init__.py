from .chan import FourChan, EightChan


def domain_for_name(name):
    if '4chan' in name:
        _, board = name.split(':')
        return FourChan(board)
    elif '8chan' in name:
        _, board = name.split(':')
        return EightChan(board)
