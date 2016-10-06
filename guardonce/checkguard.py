# -*- coding: utf-8 -*-
# Copyright (C) 2016 Cordell Bloor
# Published under the MIT License

"""Find C or C++ header files with incorrect or missing include guards."""

from __future__ import print_function
import argparse
import sys
import os
import re
from fnmatch import fnmatch
from functools import partial
from .pattern_compiler import compilePattern, ParserError
from .util import guessGuard, indexGuardStart, indexGuardEnd, getFileContents, applyToHeaders, printError

__version__ = "1.0.0"

def isProtectedByGuard(contents, guardSymbol):
    try:
        if guardSymbol:
            indexGuardStart(contents, guardSymbol)
        else:
            guessGuard(contents)

        indexGuardEnd(contents)
        return True
    except ValueError:
        return False

def isProtectedByPragmaOnce(contents):
    try:
        indexPragmaOnce(contents)
        return True
    except ValueError:
        return False

def isProtected(contents, options):
    return (options.guardOk and isProtectedByGuard(contents, options.guard)
        or options.onceOk and isProtectedByPragmaOnce(contents))

def isFileProtected(fileName, options):
    contents = getFileContents(fileName)
    return isProtected(contents, options)

def processFile(filePath, fileName, options):
    class Context:
        pass
    ctx = Context()
    ctx.filePath = filePath
    ctx.fileName = fileName

    options.guard = options.createGuard(ctx)

    try:
        if not isFileProtected(filePath, options):
            print(filePath)
    except Exception as e:
        print(e, file=sys.stderr)

def processGuardPattern(guardPattern):
    createGuard = lambda ctx: None
    if guardPattern is not None:
        try:
            createGuard = compilePattern(guardPattern)
        except ParserError as e:
            printError(e)
            sys.exit(1)
    return createGuard

def main():
    parser = argparse.ArgumentParser(
            description='Find C or C++ header files with incorrect or missing '
            'include guards.')
    parser.add_argument('files',
            metavar='file',
            nargs='+',
            help='the file(s) to check; directories require the recursive '
            'option')
    parser.add_argument('-V','--version', action='version',
            version='%(prog)s ' + __version__)
    parser.add_argument('-v','--verbose',
            action='store_true',
            help='display more information about actions being taken')
    parser.add_argument('-r','--recursive',
            action='store_true',
            dest='recursive',
            help='recursively search directories for headers')
    parser.add_argument('-p','--pattern',
            default=None,
            metavar='pattern',
            help='check that include guards match the specified pattern')
    parser.add_argument('-e','--exclude',
            action='append',
            dest='exclusions',
            metavar='pattern',
            default=[],
            help='exclude files that match the given pattern')
    parser.add_argument('-o','--only',
            dest='type',
            metavar='type',
            default='any',
            choices=['guard','once','g','o'],
            help='only accept the specified type of include protection')
    args = parser.parse_args()

    class Options:
        pass
    options = Options()
    options.guardOk = args.type in ['g', 'guard', 'any']
    options.onceOk = args.type in ['o', 'once', 'any']
    options.createGuard = processGuardPattern(args.pattern)

    for f in args.files:
        if os.path.isdir(f):
            if args.recursive:
                process = partial(processFile, options=options)
                applyToHeaders(process, f, args.exclusions)
            else:
                printError('"%s" is a directory' % f)
                sys.exit(1)
        else:
            processFile(f, os.path.basename(f), options)
