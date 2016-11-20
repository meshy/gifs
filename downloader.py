import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


COL_CLEAR = '\033[0m'
COL_BLUE = '\033[94m'
COL_GREEN = '\033[92m'
COL_RED = '\033[91m'
INDENT = 4 * ' '

IMGUR_404 = '"d835884373f4d6c8f24742ceabe74946"'

FAILED_LOGFILE = 'failed.log'
INPUT_FILENAME = 'add_me_later!'


def error(url, filename, msg):
    with open(FAILED_LOGFILE, 'a') as f:
        print('{} {}'.format(url, filename), file=f)
    print(INDENT + COL_RED + msg + COL_CLEAR)


try:
    os.remove(FAILED_LOGFILE)
except FileNotFoundError:
    print(COL_BLUE + 'Fail log not found.' + COL_CLEAR)
else:
    print(COL_BLUE + 'Fail log cleared.' + COL_CLEAR)


with open(INPUT_FILENAME) as input_file:
    for line in input_file:
        line = line.strip()
        if ' ' in line:
            url, filename = line.rsplit(maxsplit=1)
        else:
            url = line
            filename = url.split('/')[-1]

        print(filename)

        if os.path.exists(filename):
            error(url, filename, 'File exists')
            continue

        try:
            img = urlopen(Request(url, headers={'User-Agent': 'Mozilla'}))
        except (HTTPError, URLError) as e:
            error(url, filename, str(e))
            continue

        response_code = img.getcode()
        if response_code != 200:
            error(url, filename, 'HTTP ' + str(response_code))
            continue

        if img.info().get('ETag') == IMGUR_404:
            error(url, filename, 'Removed from Imgur')
            continue

        content = img.read()
        try:
            content.decode()
        except UnicodeDecodeError:
            pass
        else:
            error(url, filename, 'Response is text')
            continue

        with open(filename, 'wb') as f:
            f.write(content)
        print(INDENT + COL_GREEN + 'Saved ok.' + COL_CLEAR)
