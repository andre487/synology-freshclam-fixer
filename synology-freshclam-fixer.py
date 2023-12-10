#!/usr/bin/env python3
import argparse
import re
from collections import OrderedDict
from typing import List, NamedTuple, Optional, Union


def main():
    args = get_args()
    config = ParsedConfig.read(args.config)

    config.replace_config_values('DNSDatabaseInfo', args.dns_database_info)
    config.replace_config_values('DatabaseMirror', args.database_mirror)
    config.replace_config_values('PrivateMirror', args.private_mirror)
    config.replace_custom_values(args.custom_value)

    config.write(args.result or args.config)


def get_args():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument(
        '--config', '-c', required=True,
        help='Path to freshclam.conf',
    )
    arg_parser.add_argument(
        '--result', '-r',
        help='Path to result config, if empty it will be value of `--config`',
    )
    arg_parser.add_argument(
        '--dns-database-info', '-d',
        help='Value for replace DNSDatabaseInfo option with another domain with TXT record about components',
    )
    arg_parser.add_argument(
        '--database-mirror', '-m',
        action='append',
        help='Database mirror, can be multiple',
    )
    arg_parser.add_argument(
        '--private-mirror', '-p',
        action='append',
        help='Private mirror, can be multiple',
    )
    arg_parser.add_argument(
        '--custom-value', '-s',
        action='append',
        help='Custom config value, example: -s "Checks 12" -s "TestDatabases yes"',
    )
    return arg_parser.parse_args()


class ParsedConfigItem(NamedTuple):
    type: str
    left: str
    right: Optional[str]
    comment: Optional[str]


class ParsedConfig(List[ParsedConfigItem]):
    """
    List of ParsedConfigItem named tuples
    It's not effective but simple
    """
    LINE_CONF = 'conf'
    LINE_OTHER = 'other'

    separator_re = re.compile(r'\s+')

    @classmethod
    def read(cls, config_path: str) -> 'ParsedConfig':
        cfg = cls()
        with open(config_path) as fp:
            for line in fp:
                cfg.add_line(line)
        return cfg

    def write(self, result_path: str):
        with open(result_path, 'w') as fp:
            fp.write(self.serialize())

    def serialize(self) -> str:
        res = []
        for item in self:
            if item.type == self.LINE_CONF:
                line = f'{item.left} {item.right}'
                if item.comment:
                    line += f'  # {item.comment}'
                res.append(line)
            elif item.type == self.LINE_OTHER:
                res.append(item.left)
            else:
                raise RuntimeError(f'Unknown type: {item.type}')
        if res[-1] != '':
            res.append('')
        return '\n'.join(res)

    def add_line(self, line: str):
        line = line.strip()
        if line.startswith('#'):
            return self.append(ParsedConfigItem(self.LINE_OTHER, line, None, None))

        parts = self.separator_re.split(line, 1)
        if len(parts) == 1:
            return self.append(ParsedConfigItem(self.LINE_OTHER, line, None, None))

        name, value = parts
        comment = None
        if '#' in value:
            value, comment = [x.strip() for x in value.split('#', 1)]
        self.append(ParsedConfigItem(self.LINE_CONF, name, value, comment))

    def get_config_values(self, name: str) -> List[str]:
        res = []
        for item in self:
            if item.type == self.LINE_CONF and item.left == name:
                res.append(item.right)
        return res

    def replace_config_values(self, name: str, values: Optional[Union[str, List[str]]]):
        if not values:
            return

        val_indexes = []
        for idx, item in enumerate(self):
            if item.type == self.LINE_CONF and item.left == name:
                val_indexes.insert(0, idx)

        for idx in val_indexes:
            del self[idx]

        if not isinstance(values, (list, tuple)):
            values = (values,)

        insert_idx = val_indexes[-1] if val_indexes else len(self)
        for val in reversed(values):
            self.insert(insert_idx, ParsedConfigItem(self.LINE_CONF, name, val, None))

    def replace_custom_values(self, custom_values: Optional[str]):
        if not custom_values:
            return

        to_replace = OrderedDict()
        for raw_value in custom_values:
            parts = self.separator_re.split(raw_value.strip(), 1)
            if len(parts) != 2:
                raise ValueError(f'Invalid custom value: {raw_value}')
            to_replace.setdefault(parts[0], []).append(parts[1])

        for name, values in to_replace.items():
            self.replace_config_values(name, values)


if __name__ == '__main__':
    main()
