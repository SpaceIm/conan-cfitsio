import glob
import os

from conans import ConanFile, CMake, tools

class CfitsioConan(ConanFile):
    name = "cfitsio"
    description = "C library for reading and writing data files in FITS " \
                  "(Flexible Image Transport System) data format"
    license = "ISC"
    topics = ("conan", "cfitsio", "fits", "image", "nasa", "astronomy", "astrophysics", "space")
    homepage = "https://heasarc.gsfc.nasa.gov/fitsio/"
    url = "https://github.com/conan-io/conan-center-index"
    exports_sources = "CMakeLists.txt"
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "threadsafe": [True, False],
        "with_bzip2": [True, False],
        "with_curl": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "threadsafe": False,
        "with_bzip2": False,
        "with_curl": True
    }

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _suffix_source_file(self):
        return {
            "3.470": "3.47"
        }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.settings.os == "Windows":
            del self.options.with_bzip2
            del self.options.with_curl

    def requirements(self):
        self.requires.add("zlib/1.2.11")
        if self.options.threadsafe and self.settings.compiler == "Visual Studio":
            self.requires.add("pthreads4w/3.0.0")
        if self.options.get_safe("with_bzip2"):
            self.requires.add("bzip2/1.0.8")
        if self.settings.get_safe("with_curl"):
            self.requires.add("libcurl/7.68.0")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self._suffix_source_file.get(str(self.version))
        os.rename(extracted_dir, self._source_subfolder)

    def build(self):
        self._remove_embedded_zlib()
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def _remove_embedded_zlib(self):
        for zlib_file in glob.glob(os.path.join(self._source_subfolder, "zlib", "*")):
            if not zlib_file.endswith(("zcompress.c", "zuncompress.c")):
                os.remove(zlib_file)

    def _patch_sources(self):
        tools.replace_in_file(os.path.join(self._source_subfolder, "fitsio2.h"),
                              "#define ffstrtok(str, tok, save) strtok_r(str, tok, save)",
                              "#ifdef _WIN32\n" \
                              "#define ffstrtok(str, tok, save) strtok_s(str, tok, save)\n" \
                              "#else\n" \
                              "#define ffstrtok(str, tok, save) strtok_r(str, tok, save)\n" \
                              "#endif")

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["USE_PTHREADS"] = self.options.threadsafe
        if self.settings.os != "Windows":
            self._cmake.definitions["USE_BZIP2"] = self.options.with_bzip2
            self._cmake.definitions["USE_CURL"] = self.options.with_curl
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def package(self):
        self.copy("License.txt", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        # tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.includedirs.append(os.path.join("include", "cfitsio"))
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("m")
            if self.options.threadsafe:
                self.cpp_info.system_libs.append("pthread")
