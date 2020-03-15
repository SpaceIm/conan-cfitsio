cmake_minimum_required(VERSION 3.1.2)
project(CFITSIO)

if(EXISTS "${CMAKE_BINARY_DIR}/conanbuildinfo.cmake")
  include("${CMAKE_BINARY_DIR}/conanbuildinfo.cmake")
else()
  include(conanbuildinfo.cmake)
endif()
conan_basic_setup(TARGETS)

set(CMAKE_LEGACY_CYGWIN_WIN32 0)

# Allow @rpath token in target install name on Macs.
# See "cmake --help-policy CMP0042" for more information.
if(POLICY CMP0042)
  cmake_policy(SET CMP0042 NEW)
endif()

include(${CMAKE_ROOT}/Modules/CheckLibraryExists.cmake)
include(${CMAKE_ROOT}/Modules/CheckFunctionExists.cmake)

set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} "${CMAKE_SOURCE_DIR}")
set(INCLUDE_INSTALL_DIR "${CMAKE_INSTALL_PREFIX}/include/cfitsio")

# Define project version
set(${PROJECT_NAME}_MAJOR_VERSION 3)
set(${PROJECT_NAME}_MINOR_VERSION 47)
set(${PROJECT_NAME}_VERSION ${${PROJECT_NAME}_MAJOR_VERSION}.${${PROJECT_NAME}_MINOR_VERSION})
set(LIB_NAME cfitsio)

# Microsoft Visual Studio:
if(MSVC OR BORLAND)
  # Define
  add_definitions(-D_CRT_SECURE_NO_DEPRECATE)
  # Need an empty unistd.h in MSVC for flex-generated eval_l.c:
  file(WRITE ${CMAKE_SOURCE_DIR}/unistd.h "")
  include_directories(${CMAKE_SOURCE_DIR})
endif()

if(WIN32 AND BUILD_SHARED_LIBS)
  add_definitions(-Dcfitsio_EXPORTS)
endif()

if(BORLAND)
  # Suppress spurious Borland compiler warnings about "Suspicious
  # pointer arithmetic", "Possibly incorrect assignment", and
  # "Comparing signed and unsigned values".
  add_definitions(-w-spa)
  add_definitions(-w-pia)
  add_definitions(-w-csu)
endif()

set(CFITSIO_LINK_LIBS "")

list(APPEND CFITSIO_LINK_LIBS "CONAN_PKG::zlib")

option(USE_PTHREADS "Thread-safe build (using pthreads)" OFF)
if(USE_PTHREADS)
  if(MSVC)
    list(APPEND CFITSIO_LINK_LIBS "CONAN_PKG::pthreads4w")
  else()
    set(CMAKE_THREAD_PREFER_PTHREAD TRUE)
    find_package(Threads REQUIRED)
    list(APPEND CFITSIO_LINK_LIBS "Threads::Threads")
  endif()
  add_definitions(-D_REENTRANT)
endif()

if(NOT WIN32)
  option(USE_BZIP2 "" OFF)
  if(USE_BZIP2)
    list(APPEND CFITSIO_LINK_LIBS "CONAN_PKG::bzip2")
    add_definitions(-DHAVE_BZIP2)
  endif()
endif()

# Support for remote file drivers is not implemented for native Windows:
if(NOT WIN32)
  option(USE_CURL "" ON)
  if(USE_CURL)
    # Find library needed for gethostbyname:
    CHECK_FUNCTION_EXISTS("gethostbyname" CMAKE_HAVE_GETHOSTBYNAME)
    if(NOT CMAKE_HAVE_GETHOSTBYNAME)
      CHECK_LIBRARY_EXISTS("nsl" "gethostbyname" "" CMAKE_HAVE_GETHOSTBYNAME)
    endif()

    # Find library needed for connect:
    CHECK_FUNCTION_EXISTS("connect" CMAKE_HAVE_CONNECT)
    if(NOT CMAKE_HAVE_CONNECT)
      CHECK_LIBRARY_EXISTS("socket" "connect" "" CMAKE_HAVE_CONNECT)
    endif()

    # Define HAVE_NET_SERVICES if gethostbyname & connect were found:
    if(CMAKE_HAVE_GETHOSTBYNAME AND CMAKE_HAVE_CONNECT)
      add_definitions(-DHAVE_NET_SERVICES)
    endif()

    # Find curl library, for HTTPS support:
    list(APPEND CFITSIO_LINK_LIBS "CONAN_PKG::libcurl")
    add_definitions(-DCFITSIO_HAVE_CURL)
  endif()
endif()

set(SOURCE_DIR "source_subfolder")
set(SRC_FILES
  ${SOURCE_DIR}/buffers.c
  ${SOURCE_DIR}/cfileio.c
  ${SOURCE_DIR}/checksum.c
  ${SOURCE_DIR}/drvrfile.c
  ${SOURCE_DIR}/drvrmem.c
  ${SOURCE_DIR}/drvrnet.c
  ${SOURCE_DIR}/editcol.c
  ${SOURCE_DIR}/edithdu.c
  ${SOURCE_DIR}/eval_f.c
  ${SOURCE_DIR}/eval_l.c
  ${SOURCE_DIR}/eval_y.c
  ${SOURCE_DIR}/f77_wrap1.c
  ${SOURCE_DIR}/f77_wrap2.c
  ${SOURCE_DIR}/f77_wrap3.c
  ${SOURCE_DIR}/f77_wrap4.c
  ${SOURCE_DIR}/fits_hcompress.c
  ${SOURCE_DIR}/fits_hdecompress.c
  ${SOURCE_DIR}/fitscore.c
  ${SOURCE_DIR}/getcol.c
  ${SOURCE_DIR}/getcolb.c
  ${SOURCE_DIR}/getcold.c
  ${SOURCE_DIR}/getcole.c
  ${SOURCE_DIR}/getcoli.c
  ${SOURCE_DIR}/getcolj.c
  ${SOURCE_DIR}/getcolk.c
  ${SOURCE_DIR}/getcoll.c
  ${SOURCE_DIR}/getcols.c
  ${SOURCE_DIR}/getcolsb.c
  ${SOURCE_DIR}/getcolui.c
  ${SOURCE_DIR}/getcoluj.c
  ${SOURCE_DIR}/getcoluk.c
  ${SOURCE_DIR}/getkey.c
  ${SOURCE_DIR}/group.c
  ${SOURCE_DIR}/grparser.c
  ${SOURCE_DIR}/histo.c
  ${SOURCE_DIR}/imcompress.c
  ${SOURCE_DIR}/iraffits.c
  ${SOURCE_DIR}/modkey.c
  ${SOURCE_DIR}/pliocomp.c
  ${SOURCE_DIR}/putcol.c
  ${SOURCE_DIR}/putcolb.c
  ${SOURCE_DIR}/putcold.c
  ${SOURCE_DIR}/putcole.c
  ${SOURCE_DIR}/putcoli.c
  ${SOURCE_DIR}/putcolj.c
  ${SOURCE_DIR}/putcolk.c
  ${SOURCE_DIR}/putcoll.c
  ${SOURCE_DIR}/putcols.c
  ${SOURCE_DIR}/putcolsb.c
  ${SOURCE_DIR}/putcolu.c
  ${SOURCE_DIR}/putcolui.c
  ${SOURCE_DIR}/putcoluj.c
  ${SOURCE_DIR}/putcoluk.c
  ${SOURCE_DIR}/putkey.c
  ${SOURCE_DIR}/quantize.c
  ${SOURCE_DIR}/region.c
  ${SOURCE_DIR}/ricecomp.c
  ${SOURCE_DIR}/scalnull.c
  ${SOURCE_DIR}/simplerng.c
  ${SOURCE_DIR}/swapproc.c
  ${SOURCE_DIR}/wcssub.c
  ${SOURCE_DIR}/wcsutil.c
  ${SOURCE_DIR}/zlib/zcompress.c
  ${SOURCE_DIR}/zlib/zuncompress.c
)
if(UNIX)
  list(APPEND SRC_FILES ${SOURCE_DIR}/drvrsmem.c)
endif()

add_library(${LIB_NAME} ${SRC_FILES})
target_link_libraries(${LIB_NAME} ${M_LIB} ${CFITSIO_LINK_LIBS})
find_library(M_LIB m)
if(M_LIB)
  target_link_libraries(${LIB_NAME} ${M_LIB})
endif()
set_target_properties(${LIB_NAME} PROPERTIES VERSION ${${PROJECT_NAME}_VERSION} SOVERSION ${${PROJECT_NAME}_MAJOR_VERSION})

install(TARGETS ${LIB_NAME}
  RUNTIME DESTINATION bin
  LIBRARY DESTINATION lib
  ARCHIVE DESTINATION lib
)

file(GLOB H_FILES source_subfolder/fitsio.h source_subfolder/longnam.h)
if(UNIX)
  list(APPEND SRC_FILES drvrsmem.h)
endif()
install(FILES ${H_FILES} DESTINATION ${INCLUDE_INSTALL_DIR} COMPONENT Devel)
