import sys, os, json

def eprint(*args, **kwargs):
    """
    Print to stderr - see https://stackoverflow.com/a/14981125/8545455
    """
    print(*args, file=sys.stderr, **kwargs)


def strip_end(h, s):
    """
    If string h ends with s, strip it off; return the result
    """
    if h.endswith(s):
        h = h[:-len(s)]
    return h


def strip_start(h, s):
    """
    If string h starts with s, strip it off; return the result
    """
    if h.startswith(s):
        h = h[len(s):]
    return h


def host_cleanup(host):
    """
    Condense URL into a standard form
    """
    if not host.startswith('https://'):
        host = 'https://' + host  # Add schema
    host = strip_end(host, '/')
    host = strip_end(host, '/api/v1')
    host = strip_end(host, '/')
    return host


def getenv_check(e):
    """
    Check environment variable is defined, and return the result
    """
    res = os.getenv(e)
    if res == None:
        print(e, 'environment variable not set - stopping.')
        exit(1)
    else:
        return res


def getenv(*args, **kwargs):
    """
    Get environment variable
    """
    return os.getenv(*args, **kwargs)


def xstr(s):
    """
    Return s as a string, mapping None value to an empty string
    """
    return str(s) if s else ''

# -----------------------------------------------------------------------------------------
# Argparse helper functions
# Each of these functions add flags from a list of tuples comprising (name, help string)
def add_str_args(group, flags):
    for f in flags:
        group.add_argument('--'+f[0], type=str, action='store', help=f[1])


def add_boolean_args(group, flags):
    bool_choices = [False, True]
    for f in flags:
        group.add_argument('--'+f[0], type=bool_option, action='store', default=None, choices=bool_choices, help=f[1])


def add_json_args(group, flags):
    for f in flags:
        group.add_argument('--'+f[0], type=json_option, action='store', help=f[1])


def bool_option(s):
    """
    Command-line option str which must resolve to [true|false]
    """
    s = s.lower()
    if s=='true':
        return True
    elif s=='false':
        return False
    else:
        raise TypeError # Let argparse know there's a problem


def json_option(s):
    """
    Command-line option str which must resolve to a valid JSON object
    """
    try:
        j = json.loads(s)
        return j
    except:
        raise TypeError # Let argparse know there's a problem