#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Allows you to query the database for search results.

Because of use of JPype, DocFetcher's scripting support is no longer insecure.
Its performance is improved because JVM is interfaced directly to python.

[JAbs](https://github.com/KOLANICH-libs/JAbs.py) is an abstraction layer
allowing you to use not only JPype + cpython, but also GraalPython.

You can get JPype [here](https://github.com/jpype-project/jpype).
GraalPython can be downloaded [here](https://github.com/oracle/graalpython/releases).

To use the python bindings you need to provide the path to DocFetcher lib dir
and the path to indexes.
"""

import typing
from pathlib import Path

import JAbs

from .constants import DF_PKG, DF_PKG_MODEL, DF_PKG_MODEL_IDX, DF_PKG_MODEL_IDX_TASK
from .defaults import ChosenDirManager
from .dir_managers import DirManager


class DocFetcher:
	__slots__ = ("ji", "dirManager", "MyDummyCancellable", "MyCancelHandler")

	def __init__(self, dirManager: typing.Optional[DirManager] = None):
		if dirManager is None:
			dirManager = ChosenDirManager(None)
		self.dirManager = dirManager
		libDir = dirManager.getClassPathDir()

		jars = dirManager.getClassPath()
		self.ji = JAbs.SelectedJVMInitializer(
			jars,
			[
				"java.io.File",
				DF_PKG_MODEL + ".IndexRegistry",
				DF_PKG_MODEL + ".Cancelable",
				DF_PKG_MODEL_IDX_TASK + ".CancelHandler",
				DF_PKG_MODEL_IDX_TASK + ".CancelAction",
			],
			libPaths=[libDir],
		)

		class MyDummyCancellable(self.ji.Cancelable, metaclass=self.ji._Implements):
			@self.ji._Override
			def isCanceled(self) -> bool:
				return False

		class MyCancelHandler(self.ji.CancelHandler, metaclass=self.ji._Implements):
			@self.ji._Override
			def cancel(self) -> "CancelAction":
				return self.ji.CancelAction.DISCARD

		self.MyCancelHandler = MyCancelHandler
		self.MyDummyCancellable = MyDummyCancellable

	def index(self, indexesDir: typing.Optional[Path] = None) -> "Index":
		if indexesDir is None:
			indexesDir = self.dirManager.getDefaultIndexDir()
		return Index(self, indexesDir)


class Index:
	__slots__ = ("parent", "problems", "indexRegistry", "searcher")

	def __init__(self, parent: DocFetcher, indexesDir: Path):
		self.parent = parent

		indexDir = parent.ji.File(str(indexesDir.absolute()))
		self.indexRegistry = parent.ji.IndexRegistry(indexDir, 1, 0)

		self.problems = self.indexRegistry.load(parent.MyDummyCancellable())
		self.searcher = None

	def __enter__(self):
		self.searcher = self.indexRegistry.getSearcher()
		self.indexRegistry.getQueue().shutdown(self.parent.MyCancelHandler())
		return self

	def __exit__(self, exc_type, exc_value, traceback):
		self.searcher.shutdown()

	@property
	def corruptedIndexes(self):
		return list(self.problems.corruptedIndexes)

	@property
	def obsoleteFiles(self):
		return list(self.problems.obsoleteFiles)

	@property
	def overflowIndexes(self):
		return list(self.problems.overflowIndexes)

	def search(self, query: str) -> typing.Iterator["ResultDocument"]:
		"""Search the given query string and return an iterator of result objects.

		The result objects provide the following getter methods for accessing their
		attributes:
		- getAuthors
		- getDateStr - e-mail send date
		- getFilename
		- getLastModifiedStr - last-modified date on files
		- getPathStr - file path
		- getScore - result score as int
		- getSender - e-mail sender
		- getSizeInKB - file size as int
		- getTitle
		- getType
		- isEmail - boolean indicating whether result object is e-mail or file"""
		return self.searcher.search(query)
