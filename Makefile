# ****************************************************************************
#    Neo Ledger App
#    (c) 2023 Ledger SAS.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
# ****************************************************************************

ifeq ($(BOLOS_SDK),)
$(error Environment variable BOLOS_SDK is not set)
endif

include $(BOLOS_SDK)/Makefile.defines

########################################
#        Mandatory configuration       #
########################################

# Enabling DEBUG flag will enable PRINTF and disable optimizations
#DEBUG = 1

# Application name
APPNAME = "NEO"

# Application version
APPVERSION_M= 1
APPVERSION_N= 3
APPVERSION_P= 8
APPVERSION = "$(APPVERSION_M).$(APPVERSION_N).$(APPVERSION_P)"

# Application source files
APP_SOURCE_PATH += src

# Application icons
ICON_NANOS = nanos_app_neo.gif
ICON_STAX = stax_app_neo.gif
ICON_NANOX = nanox_app_neo.gif
ICON_NANOSP = nanox_app_neo.gif

# Application allowed derivation curves.
CURVE_APP_LOAD_PARAMS = secp256r1

# Application allowed derivation paths.
PATH_APP_LOAD_PARAMS = "44'/888'" "44'/1024'"

# Setting to allow building variant applications
VARIANT_PARAM = COIN
VARIANT_VALUES = neo

########################################
#     Application custom permissions   #
########################################
# See SDK `include/appflags.h` for the purpose of each permission
HAVE_APPLICATION_FLAG_BOLOS_SETTINGS = 1
HAVE_APPLICATION_FLAG_GLOBAL_PIN = 1

# U2F
DEFINES   += HAVE_IO_U2F U2F_PROXY_MAGIC=\"NEO\"
SDK_SOURCE_PATH  += lib_stusb lib_stusb_impl lib_u2f 

########################################
# Application communication interfaces #
########################################
ENABLE_BLUETOOTH = 1

########################################
#         NBGL custom features         #
########################################
ENABLE_NBGL_QRCODE = 1

# Use only specific files from standard app
DISABLE_STANDARD_APP_FILES = 1
APP_SOURCE_FILES += ${BOLOS_SDK}/lib_standard_app/io.c
APP_SOURCE_FILES += ${BOLOS_SDK}/lib_standard_app/crypto_helpers.c
INCLUDES_PATH += ${BOLOS_SDK}/lib_standard_app

ifeq ($(TARGET_NAME), TARGET_NANOS)
DISABLE_STANDARD_BAGL_UX_FLOW = 1
endif

include $(BOLOS_SDK)/Makefile.standard_app

