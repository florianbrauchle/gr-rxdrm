INCLUDE(FindPkgConfig)
PKG_CHECK_MODULES(PC_RXDRM rxdrm)

FIND_PATH(
    RXDRM_INCLUDE_DIRS
    NAMES rxdrm/api.h
    HINTS $ENV{RXDRM_DIR}/include
        ${PC_RXDRM_INCLUDEDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/include
          /usr/local/include
          /usr/include
)

FIND_LIBRARY(
    RXDRM_LIBRARIES
    NAMES gnuradio-rxdrm
    HINTS $ENV{RXDRM_DIR}/lib
        ${PC_RXDRM_LIBDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/lib
          ${CMAKE_INSTALL_PREFIX}/lib64
          /usr/local/lib
          /usr/local/lib64
          /usr/lib
          /usr/lib64
)

INCLUDE(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(RXDRM DEFAULT_MSG RXDRM_LIBRARIES RXDRM_INCLUDE_DIRS)
MARK_AS_ADVANCED(RXDRM_LIBRARIES RXDRM_INCLUDE_DIRS)

