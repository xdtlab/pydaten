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
