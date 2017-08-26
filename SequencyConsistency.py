#!/usr/bin/env python3

from __future__ import print_function, division

import argparse
import os
import re
import sys

class SequencyConsistency():
    def __init__(self, sequence):

        self.sequence = sequence

        if self.sequence:
            self.missing_sequencies = self.__missing_number_sequence()

        self.missing = sorted(self.__missing_number_sequence())

    def __missing_number_sequence(self):
        try:
            max_range = max(int(match) for match in self.sequence)
        except ValueError:
            print('Regex must match a integer.', end='\n\n')
            raise

        full_range = set(str(num).rjust(len(str(max_range)), '0') 
                         for num in range(1, max_range + 1))
        return full_range.difference(self.sequence)
        
    def print_missing_sequencies(self, reverse=False):
        if getattr(self, 'missing_sequencies', None):
            return sorted(self.__missing_number_sequence(), reverse=reverse)


class SequencyConsistencyRegex(SequencyConsistency):
    def __init__(self, sequence, regex_def_grp=None):
        if regex_def_grp:
            self.regex_compiled, self.regex_group_num = regex_def_grp
        else:
            self.regex_compiled, self.regex_group_num = (re.compile('(\d+)'), 1)

        self.sequence = {str(self.regex_compiled.search(sequence).group(self.regex_group_num))
                        for sequence in self.sequence
                        if self.regex_compiled.search(sequence) is not None}

        SequencyConsistency.__init__(self, self.sequence)



class DirectoryConsistency(SequencyConsistencyRegex):
    def __init__(self, directory, regex_def_grp=None):
        try:
            self.sequence = os.listdir(directory)
        except (FileNotFoundError, NotADirectoryError, PermissionError) as err:
            # Exit class if directory indicated is incorrect
            print(err, file=sys.stderr)
            return None

        SequencyConsistencyRegex.__init__(self, self.sequence, regex_def_grp)

def main():
    # Create commandline flags
    parser = argparse.ArgumentParser(description='Detect missing portion of sequency in given sequency')
    parser.add_argument('-e', '--regexp',
            type=str,
            required=False,
            default='(\d+)',
            help='Set regex. Defaults to (\d+)')
    parser.add_argument('-g', '--group',
            type=int,
            required=False,
            default=1,
            help='Set regex matching group to identify sequence. --group 3 will match (\d+) in regexp of (\w)(-)(\d+). Each () identifies a group')
    args, other_args = parser.parse_known_args()

    directories = (other_args if other_args else (line for line in sys.stdin))
    for directory in directories:
        current_dir = DirectoryConsistency(directory.strip(),
                                           regex_def_grp=(re.compile(args.regexp), args.group))

        missing_in_dir = current_dir.missing
        if missing_in_dir:
            print('Missing from {directory}:'.format(directory=repr(os.path.abspath(directory.strip()))))
            print('{sequences}'.format(sequences='\n'.join(seq for seq in missing_in_dir)))

if __name__ == '__main__':
    main()
