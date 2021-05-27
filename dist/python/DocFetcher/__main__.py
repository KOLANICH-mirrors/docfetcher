#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import sys
from pathlib import Path

from . import DocFetcher
from .defaults import ChosenDirManager

__doc__ = """
This script uses the given command-line arguments as a query to DocFetcher
Search. The results returned by the latter are printed as filename-filepath
pairs on the standard output.
"""


def main():
	defaultDirs = ChosenDirManager()
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument("--libDir", type=str, default=defaultDirs.getClassPathDir(), help="Path to DocFetcher classpath")
	parser.add_argument("--indexesDir", type=str, default=defaultDirs.getDefaultIndexDir(), help="Path to index")
	parser.add_argument("query", metavar="query", type=str, nargs="+", help="Search query")
	args = parser.parse_args()

	if args.libDir:
		args.libDir = Path(args.libDir)
		if not args.libDir.is_dir():
			print(args.libDir, "is not a dir!")

	if args.indexesDir:
		args.indexesDir = Path(args.indexesDir)
		if not args.indexesDir.is_dir():
			print(args.indexesDir, "is not a dir!")

	query = " ".join(args.query)

	df = DocFetcher(ChosenDirManager(args.libDir))
	with df.index(args.indexesDir) as idx:
		try:
			result_docs = idx.search(query)
		except BaseException:  # pylint:disable=broad-except
			print("ERROR: " + str(sys.exc_info()[1]))
			return sys.exit(2)
		for doc in result_docs:
			print(doc.getFilename() + "\t" + str(doc.getScore()) + "\t" + doc.getPathStr())

	sys.exit(0)


if __name__ == "__main__":
	main()
