cmake_minimum_required(VERSION 3.1.2)
PROJECT(CFITSIO)

if(EXISTS "${CMAKE_BINARY_DIR}/conanbuildinfo.cmake")
  include("${CMAKE_BINARY_DIR}/conanbuildinfo.cmake")
else()
  include(conanbuildinfo.cmake)
endif()
conan_basic_setup(TARGETS)

SET(CMAKE_LEGACY_CYGWIN_WIN32 0)

# Allow @rpath token in target install name on Macs.
# See "cmake --help-policy CMP0042" for more information.
IF(POLICY CMP0042)
  CMAKE_POLICY(SET CMP0042 NEW)
ENDIF()

INCLUDE (${CMAKE_ROOT}/Modules/CheckLibraryExists.cmake)
INCLUDE (${CMAKE_ROOT}/Modules/CheckFunctionExists.cmake)

OPTION (USE_PTHREADS "Thread-safe build (using pthreads)" OFF)

set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} "${CMAKE_SOURCE_DIR}")
set (LIB_DESTINATION "${CMAKE_INSTALL_PREFIX}/lib${LIB_SUFFIX}")
set (INCLUDE_INSTALL_DIR "${CMAKE_INSTALL_PREFIX}/include/")

# Define project version
SET(${PROJECT_NAME}_MAJOR_VERSION 3)
SET(${PROJECT_NAME}_MINOR_VERSION 47)
SET(${PROJECT_NAME}_VERSION ${${PROJECT_NAME}_MAJOR_VERSION}.${${PROJECT_NAME}_MINOR_VERSION})
SET(LIB_NAME cfitsio)

# Microsoft Visual Studio:
IF(MSVC OR BORLAND)
    # Define
    ADD_DEFINITIONS(-D_CRT_SECURE_NO_DEPRECATE)
    # Need an empty unistd.h in MSVC for flex-generated eval_l.c:
    FILE(WRITE ${CMAKE_SOURCE_DIR}/unistd.h "")
    INCLUDE_DIRECTORIES(${CMAKE_SOURCE_DIR})
ENDIF()

IF(BORLAND)
    # Suppress spurious Borland compiler warnings about "Suspicious
    # pointer arithmetic", "Possibly incorrect assignment", and
    # "Comparing signed and unsigned values".
    ADD_DEFINITIONS(-w-spa)
    ADD_DEFINITIONS(-w-pia)
    ADD_DEFINITIONS(-w-csu)
ENDIF()

#add_subdirectory (src)

SET (LIB_TYPE STATIC)
IF (BUILD_SHARED_LIBS)
  SET (LIB_TYPE SHARED)
ENDIF (BUILD_SHARED_LIBS)

FILE(GLOB H_FILES "source_subfolder/*.h")

SET(CFITSIO_LINK_LIBS "")

LIST(APPEND CFITSIO_LINK_LIBS "CONAN_PKG::zlib")

IF (USE_PTHREADS)
    LIST(APPEND CFITSIO_LINK_LIBS "CONAN_PKG::pthreads4w")
    ADD_DEFINITIONS(-D_REENTRANT)
ENDIF()

# Math library (not available in MSVC or MINGW)
IF (MSVC OR MINGW)
    SET(M_LIB "")
ELSE()
    FIND_LIBRARY(M_LIB m)
ENDIF()

# Support for remote file drivers is not implemented for native Windows:
IF (NOT MSVC)
    # Find library needed for gethostbyname:
    CHECK_FUNCTION_EXISTS("gethostbyname" CMAKE_HAVE_GETHOSTBYNAME)
    IF(NOT CMAKE_HAVE_GETHOSTBYNAME)
       CHECK_LIBRARY_EXISTS("nsl" "gethostbyname" "" CMAKE_HAVE_GETHOSTBYNAME)
    ENDIF()

    # Find library needed for connect:
    CHECK_FUNCTION_EXISTS("connect" CMAKE_HAVE_CONNECT)
    IF(NOT CMAKE_HAVE_CONNECT)
       CHECK_LIBRARY_EXISTS("socket" "connect" "" CMAKE_HAVE_CONNECT)
    ENDIF()

    # Define HAVE_NET_SERVICES if gethostbyname & connect were found:
    IF (CMAKE_HAVE_GETHOSTBYNAME AND CMAKE_HAVE_CONNECT)
        ADD_DEFINITIONS(-DHAVE_NET_SERVICES)
    ENDIF ()

    # Find curl library, for HTTPS support:
    LIST(APPEND CFITSIO_LINK_LIBS "CONAN_PKG::libcurl")
    ADD_DEFINITIONS(-DCFITSIO_HAVE_CURL)
ENDIF()

SET(SRC_FILES
    source_subfolder/buffers.c source_subfolder/cfileio.c source_subfolder/checksum.c
    source_subfolder/drvrfile.c source_subfolder/drvrmem.c source_subfolder/drvrnet.c
    source_subfolder/editcol.c source_subfolder/edithdu.c source_subfolder/eval_f.c source_subfolder/eval_l.c source_subfolder/eval_y.c
    source_subfolder/f77_wrap1.c source_subfolder/f77_wrap2.c source_subfolder/f77_wrap3.c source_subfolder/f77_wrap4.c
    source_subfolder/fits_hcompress.c source_subfolder/fits_hdecompress.c source_subfolder/fitscore.c
    source_subfolder/getcol.c source_subfolder/getcolb.c source_subfolder/getcold.c source_subfolder/getcole.c source_subfolder/getcoli.c source_subfolder/getcolj.c source_subfolder/getcolk.c
    source_subfolder/getcoll.c source_subfolder/getcols.c source_subfolder/getcolsb.c source_subfolder/getcolui.c source_subfolder/getcoluj.c source_subfolder/getcoluk.c
    source_subfolder/getkey.c source_subfolder/group.c source_subfolder/grparser.c source_subfolder/histo.c source_subfolder/imcompress.c source_subfolder/iraffits.c source_subfolder/modkey.c
    source_subfolder/pliocomp.c
    source_subfolder/putcol.c source_subfolder/putcolb.c source_subfolder/putcold.c source_subfolder/putcole.c source_subfolder/putcoli.c source_subfolder/putcolj.c source_subfolder/putcolk.c
    source_subfolder/putcoll.c source_subfolder/putcols.c source_subfolder/putcolsb.c source_subfolder/putcolu.c source_subfolder/putcolui.c source_subfolder/putcoluj.c source_subfolder/putcoluk.c
    source_subfolder/putkey.c source_subfolder/quantize.c source_subfolder/region.c source_subfolder/ricecomp.c source_subfolder/scalnull.c source_subfolder/simplerng.c source_subfolder/swapproc.c
    source_subfolder/wcssub.c source_subfolder/wcsutil.c source_subfolder/zlib/zcompress.c source_subfolder/zlib/zuncompress.c
)

ADD_LIBRARY(${LIB_NAME} ${LIB_TYPE} ${H_FILES} ${SRC_FILES})
TARGET_LINK_LIBRARIES(${LIB_NAME} ${M_LIB} ${CFITSIO_LINK_LIBS})

SET_TARGET_PROPERTIES(${LIB_NAME} PROPERTIES VERSION ${${PROJECT_NAME}_VERSION} SOVERSION ${${PROJECT_NAME}_MAJOR_VERSION})
install(TARGETS ${LIB_NAME} DESTINATION ${LIB_DESTINATION})
install(TARGETS ${LIB_NAME}
                            RUNTIME DESTINATION bin
                            LIBRARY DESTINATION lib
                            ARCHIVE DESTINATION lib)
install(FILES ${H_FILES} DESTINATION ${INCLUDE_INSTALL_DIR} COMPONENT Devel)
