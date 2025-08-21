import re
def _parse(v): return tuple(int(x) for x in re.findall(r"\d+", v))
def require_version(current, spec):
    cur = _parse(current)
    for part in spec.split(','):
        part = part.strip()
        if not part: continue
        if part.startswith('>='):
            if cur < _parse(part[2:]): raise RuntimeError('ada-ui-kit too old; need %s' % part)
        elif part.startswith('>'):
            if cur <= _parse(part[1:]): raise RuntimeError('ada-ui-kit too old; need %s' % part)
        elif part.startswith('<='):
            if cur > _parse(part[2:]): raise RuntimeError('ada-ui-kit too new; need %s' % part)
        elif part.startswith('<'):
            if cur >= _parse(part[1:]): raise RuntimeError('ada-ui-kit too new; need %s' % part)
        elif part.startswith('=='):
            if cur != _parse(part[2:]): raise RuntimeError('ada-ui-kit must be %s' % part)
        else:
            if cur < _parse(part): raise RuntimeError('ada-ui-kit too old; need >= %s' % part)
