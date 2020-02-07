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
        "with_pthread": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_pthread": False
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
            "3.470": "-3.47"
        }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        self.requires.add("libcurl/7.68.0")
        self.requires.add("zlib/1.2.11")
        if self.options.with_pthread and self.settings.os == "Windows":
            self.requires.add("pthreads4w/3.0.0")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + self._suffix_source_file.get(str(self.version))
        os.rename(extracted_dir, self._source_subfolder)

    def build(self):
        for zlib_file in glob.glob(os.path.join(self._source_subfolder, "zlib", "*")):
            if not zlib_file.endswith(("zcompress.c", "zuncompress.c")):
                os.remove(zlib_file)
        cmake = self._configure_cmake()
        cmake.build()

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["USE_PTHREADS"] = self.options.with_pthread
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def package(self):
        self.copy("License.txt", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        # tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("m")
            if self.options.with_pthread:
                self.cpp_info.system_libs.append("pthread")
