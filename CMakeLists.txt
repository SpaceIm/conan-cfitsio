cmake_minimum_required(VERSION 3.1.2)
project(CFITSIO C)

include(conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

set(CMAKE_LEGACY_CYGWIN_WIN32 0)

option(CFITSIO_USE_PTHREADS "Thread-safe build (using pthreads)" OFF)
option(CFITSIO_USE_SSE2 "Enable use of instructions in the SSE2 extended instruction set" OFF)
option(CFITSIO_USE_SSSE3 "Enable use of instructions in the SSSE3 extended instruction set" OFF)

include(CheckSymbolExists)
include(CheckCSourceCompiles)

# Define project version
set(${PROJECT_NAME}_MAJOR_VERSION ${MAJOR_VERSION})
set(${PROJECT_NAME}_MINOR_VERSION ${MINOR_VERSION})
set(${PROJECT_NAME}_VERSION ${${PROJECT_NAME}_MAJOR_VERSION}.${${PROJECT_NAME}_MINOR_VERSION})

set(SOURCE_DIR "source_subfolder")
set(SRC_FILES
  ${SOURCE_DIR}/buffers.c
  ${SOURCE_DIR}/cfileio.c
  ${SOURCE_DIR}/checksum.c
  ${SOURCE_DIR}/drvrfile.c
  ${SOURCE_DIR}/drvrmem.c
  ${SOURCE_DIR}/drvrnet.c
  ${SOURCE_DIR}/drvrsmem.c
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

add_library(cfitsio ${SRC_FILES})

if(MSVC OR BORLAND)
  target_compile_definitions(cfitsio PRIVATE "_CRT_SECURE_NO_DEPRECATE")
  # Need an empty unistd.h in MSVC for flex-generated eval_l.c:
  file(WRITE ${CMAKE_SOURCE_DIR}/unistd.h "")
  target_include_directories(cfitsio PRIVATE ${CMAKE_SOURCE_DIR})
endif()

if(BORLAND)
  # Suppress spurious Borland compiler warnings about "Suspicious
  # pointer arithmetic", "Possibly incorrect assignment", and
  # "Comparing signed and unsigned values".
  target_compile_options(cfitsio PRIVATE -w-spa -w-pia -w-csu)
endif()

find_library(M_LIB m)
if(M_LIB)
  target_link_libraries(cfitsio PRIVATE ${M_LIB})
endif()

target_link_libraries(cfitsio PRIVATE CONAN_PKG::zlib)

if(CFITSIO_USE_PTHREADS)
  if(MSVC)
    target_link_libraries(cfitsio PRIVATE CONAN_PKG::pthreads4w)
  else()
    set(CMAKE_THREAD_PREFER_PTHREAD TRUE)
    find_package(Threads REQUIRED)
    target_link_libraries(cfitsio PRIVATE Threads::Threads)
  endif()
  target_compile_definitions(cfitsio PRIVATE "_REENTRANT")
endif()

if(CFITSIO_USE_SSE2)
  if("${CMAKE_CXX_COMPILER_ID}" STREQUAL "GNU" OR
     "${CMAKE_CXX_COMPILER_ID}" STREQUAL "Clang" OR
     "${CMAKE_CXX_COMPILER_ID}" STREQUAL "AppleClang")
      target_compile_options(cfitsio PRIVATE -msse2)
  endif()
  if(MSVC)
    target_compile_definitions(cfitsio PRIVATE "__SSE2__=1")
  endif()
endif()

if(CFITSIO_USE_SSSE3)
  if("${CMAKE_CXX_COMPILER_ID}" STREQUAL "GNU" OR
     "${CMAKE_CXX_COMPILER_ID}" STREQUAL "Clang" OR
     "${CMAKE_CXX_COMPILER_ID}" STREQUAL "AppleClang")
      target_compile_options(cfitsio PRIVATE -mssse3)
  endif()
  if(MSVC)
    target_compile_definitions(cfitsio PRIVATE "__SSE2__=1;__SSSE3__=1")
  endif()
endif()

if(NOT WIN32)
  option(CFITSIO_USE_BZIP2 "Enable bzip2 support" OFF)
  if(CFITSIO_USE_BZIP2)
    target_link_libraries(cfitsio PRIVATE CONAN_PKG::bzip2)
    target_compile_definitions(cfitsio PRIVATE "HAVE_BZIP2=1")
  endif()
endif()

# Support for remote file drivers is not implemented for native Windows:
if(NOT WIN32)
  option(CFITSIO_USE_CURL "Enable remote file i/o support" ON)
  if(CFITSIO_USE_CURL)
    check_symbol_exists(gethostbyname "netdb.h" CMAKE_HAVE_GETHOSTBYNAME)
    check_symbol_exists(connect "sys/types.h;sys/socket.h" CMAKE_HAVE_CONNECT)
    if(CMAKE_HAVE_GETHOSTBYNAME AND CMAKE_HAVE_CONNECT)
      target_compile_definitions(cfitsio PRIVATE "HAVE_NET_SERVICES")
    endif()

    target_link_libraries(cfitsio PRIVATE CONAN_PKG::libcurl)
    target_compile_definitions(cfitsio PRIVATE "CFITSIO_HAVE_CURL")
  endif()
endif()

# Test for the unix ftruncate function
check_symbol_exists(ftruncate "unistd.h" HAVE_FTRUNCATE)
target_compile_definitions(cfitsio PRIVATE "$<$<BOOL:${HAVE_FTRUNCATE}>:HAVE_FTRUNCATE>")

# Some systems define long long for 64-bit ints
check_c_source_compiles("
#include <stdlib.h>
int main() {
  long long filler;
  return 0;
}" HAVE_LONGLONG)
target_compile_definitions(cfitsio PRIVATE "$<$<BOOL:${HAVE_LONGLONG}>:HAVE_LONGLONG>")

# Check is System V IPC is supported on this machine
check_c_source_compiles("
#include <sys/ipc.h>
#include <sys/shm.h>
#include <sys/sem.h>
int main() {
  shmat(0,0,0);
  shmdt(0);
  shmget(0, 0, 0);
  semget(0, 0, 0);
  return 0;
}" HAVE_SHMEM_SERVICES)
target_compile_definitions(cfitsio PRIVATE "$<$<BOOL:${HAVE_SHMEM_SERVICES}>:HAVE_SHMEM_SERVICES>")

# Some systems define flock_t, for others we have to define it ourselves
check_c_source_compiles("
#include <sys/flock.h>
int main() {
  flock_t filler;
  return 0;
}" HAVE_FLOCK_T)
target_compile_definitions(cfitsio PRIVATE "$<$<BOOL:${HAVE_FLOCK_T}>:HAVE_FLOCK_T>")

# Check union semun
check_c_source_compiles("
#include <sys/ipc.h>
#include <sys/shm.h>
#include <sys/sem.h>
int main() {
  union semun filler;
  return 0;
}" HAVE_UNION_SEMUN)
target_compile_definitions(cfitsio PRIVATE "$<$<BOOL:${HAVE_UNION_SEMUN}>:HAVE_UNION_SEMUN>")

# Check fmemopen
check_symbol_exists(fmemopen "stdio.h" HAVE_FMEMOPEN)
target_compile_definitions(cfitsio PRIVATE "$<$<BOOL:${HAVE_FMEMOPEN}>:HAVE_FMEMOPEN>")

if(WIN32 AND BUILD_SHARED_LIBS)
  target_compile_definitions(cfitsio PRIVATE "cfitsio_EXPORTS")
endif()

set_target_properties(cfitsio
  PROPERTIES
    VERSION ${${PROJECT_NAME}_VERSION}
    SOVERSION ${${PROJECT_NAME}_MAJOR_VERSION}
)

install(TARGETS cfitsio
  RUNTIME DESTINATION bin
  LIBRARY DESTINATION lib
  ARCHIVE DESTINATION lib
)

set(HEADER_FILES ${SOURCE_DIR}/fitsio.h ${SOURCE_DIR}/longnam.h)
install(FILES ${HEADER_FILES} DESTINATION include/cfitsio)
