import argparse
from configparser import ConfigParser
from operator import itemgetter
from pathlib import Path
import re


def _read_config():
    config = ConfigParser()
    config.read('.version_upgrader.ini')
    return config['version_file']


def _version_up(current_version: str, level: int):
    version_levels = list(int(part) for part in current_version.split('.'))
    version_levels[level] += 1
    return '.'.join(str(part) for part in version_levels)


def main(level: int):
    file_name, line, pattern = itemgetter('file_name', 'line', 'pattern')(_read_config())

    with open(Path() / file_name, 'r') as file:
        file_content = file.readlines()
        line_with_version = file_content[int(line)]
        found = re.findall(pattern, line_with_version)

        if not found:
            raise ValueError(f'There is no match for pattern {pattern!r} in file {file_name!r}')

        current_version = found[0]
        new_version = _version_up(current_version, level)
        file_content[int(line)] = re.sub(pattern, new_version, line_with_version)

    with open(Path() / file_name, 'w') as file:
        file.writelines(file_content)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--level', type=int, default=2, choices=range(0, 3))
    parser.add_argument('--major', '--MAJOR', dest='level', action='store_const', const=0)
    parser.add_argument('--minor', '--MINOR',  dest='level', action='store_const', const=1)
    parser.add_argument('--patch', '--PATCH',  dest='level', action='store_const', const=2)

    level = vars(parser.parse_args()).get('level')
    SystemExit(main(level))
