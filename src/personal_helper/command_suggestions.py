"""Match normalized command names against registered names."""


def is_one_edit_apart(token: str, name: str) -> bool:
    """Check for one insertion, deletion, substitution, or adjacent swap."""
    if len(token) > len(name):
        token, name = name, token

    length_difference = len(name) - len(token)
    if length_difference > 1:
        return False

    mismatches = (index for index, (left, right) in enumerate(zip(token, name))
                  if left != right)
    first = next(mismatches, None)
    if length_difference == 1:
        return first is None or token[first:] == name[first + 1:]

    if first is None:
        return False
    second = next(mismatches, None)
    return second is None or (
        second == first + 1
        and token[first] == name[second]
        and token[second] == name[first]
        and next(mismatches, None) is None
    )
