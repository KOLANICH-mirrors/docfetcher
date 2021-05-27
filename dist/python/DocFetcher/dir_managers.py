import typing
from abc import ABC, abstractmethod
from pathlib import Path

from .constants import DF_PKG, classPathDirName, indexesDirName, swtArchs, swtJarNameTemplate, swtPlatforms, swtSubdirName


class DirManager(ABC):
	__slots__ = ("libDir",)

	def __init__(self, libDir: Path = None):
		if libDir is None:
			libDir = self.getDefaultLibDir()
			if libDir is None:
				raise Exception("Default lib dir was not detected!")

		self.libDir = libDir

	@abstractmethod
	def getDefaultLibDir(self) -> typing.Optional[Path]:
		raise NotImplementedError

	@abstractmethod
	def getDefaultIndexDir(self) -> typing.Optional[Path]:
		raise NotImplementedError

	@abstractmethod
	def getSWTClassPath(self) -> typing.Iterable[Path]:
		raise NotImplementedError

	def getClassPathDir(self) -> Path:
		return self.libDir

	def getNonSWTClassPath(self) -> typing.Iterable[Path]:
		return self.libDir.glob("*.jar")

	def getClassPath(self) -> typing.Tuple[Path, ...]:
		return tuple(self.getNonSWTClassPath()) + tuple(self.getSWTClassPath())


class PortableDirManager(DirManager):
	"""Returns a path to an index for a partable installation"""

	__slots__ = ()

	def getDefaultLibDir(self) -> typing.Optional[Path]:
		packageRootDir = Path(__file__).parent
		portableRootDirCandidate = packageRootDir.parent.parent  # dist/python/DocFetcher/../../
		cwdDir = Path(".")
		candidates = [cwdDir, portableRootDirCandidate]
		for rootCandidate in candidates:
			candLibDir = rootCandidate / classPathDirName
			if candLibDir.is_dir():
				if len(list(candLibDir.glob(DF_PKG + "*.jar"))) == 1:
					return candLibDir
		return None

	def getSWTClassPath(self) -> typing.Iterable[Path]:
		import platform  # pylint:disable=import-outside-toplevel

		swtDir = self.libDir / swtSubdirName
		swtPlatform = swtPlatforms[platform.system()]
		swtArch = swtArchs[platform.machine()]
		foundSWTJars = tuple(swtDir.glob(swtJarNameTemplate.format(platform=swtPlatform, arch=swtArch)))
		if len(foundSWTJars) != 1:
			raise Exception("Found no/multiple jars for SWT, matching the criteria. Refuse to guess.", foundSWTJars)
		return foundSWTJars

	def getDefaultIndexDir(self) -> typing.Optional[Path]:
		candidate = self.libDir.parent / indexesDirName
		if candidate.is_dir():
			return candidate
		return None
