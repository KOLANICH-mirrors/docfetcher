indexesDirName = "indexes"
classPathDirName = "lib"

DF_PKG = "net.sourceforge.docfetcher"
DF_PKG_MODEL = DF_PKG + ".model"
DF_PKG_MODEL_IDX = DF_PKG_MODEL + ".index"
DF_PKG_MODEL_IDX_TASK = DF_PKG_MODEL_IDX + ".Task"


swtPlatforms = {
	"Windows": "win32",
	"Linux": "linux",
	"Darwin": "macosx",
}
swtArchs = {"i386": "x86", "i686": "x86", "x86_64": "x86_64"}
swtSubdirName = "swt"
swtJarNameTemplate = "swt-*-{platform}-{arch}.jar"
