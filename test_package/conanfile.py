from conans import ConanFile, CMake, tools
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            fits_name = os.path.join(self.source_folder, "file011.fits")
            bin_path = os.path.join("bin", "test_package")
            command = "{0} {1}".format(bin_path, fits_name)
            self.run(command, run_environment=True)
