import string, random
def random_name(length = 16):
    chars = string.ascii_lowercase + string.digits
    return ''.join([random.choice(chars) for _ in range(length)])

def median(lst):
    n = len(lst)
    lst = sorted(lst)
    if n < 1:
        return None
    if n % 2 == 1:
        return lst[n // 2]
    else:
        return (lst[n // 2 - 1] + lst[n // 2]) // 2

import requests
def get_public_ip():
    return requests.get('https://api.ipify.org/?format=json').json()['ip']

def get_contrib_nodes():
    nodes = requests.get('https://raw.githubusercontent.com/xdtlab/list/master/list.txt').text
    nodes = nodes.split('\n')
    nodes = [n for n in nodes if len(n) > 0 and not n.startswith('#')]
    return set(nodes)
