#!/usr/bin/env python
# from webscraper.utils.logutils import init_log

# logger = init_log(__name__, __file__)


def main():
    try:
        exit_code = 0
    except AssertionError as e:
        exit_code = 1
    return exit_code


if __name__ == '__main__':
    retcode = main()
    print(retcode)
