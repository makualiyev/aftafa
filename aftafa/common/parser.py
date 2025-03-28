import sys

from aftafa.common.logger import logger


if len(sys.argv) > 1:
    ARGV_OK = sys.argv[1]

ARGV_OK = 'ok'

def main():
    if ARGV_OK:
        logger.info(msg=f"OK {ARGV_OK}")


    ok = {'ok': 1, 'okk': 2}
    try:
        a = ok['oka']
    except KeyError as e:
        logger.exception(e)



if __name__ == '__main__':
    main()