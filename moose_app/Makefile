MOOSE_DIR ?= $(CURDIR)/../.agent-runtime/moose
FRAMEWORK_DIR := $(MOOSE_DIR)/framework

include $(FRAMEWORK_DIR)/build.mk
include $(FRAMEWORK_DIR)/moose.mk

ALL_MODULES := no
SOLID_MECHANICS := yes

include $(MOOSE_DIR)/modules/modules.mk

APPLICATION_DIR := $(CURDIR)
APPLICATION_NAME := nonlinear_biot_ad
BUILD_EXEC := yes
GEN_REVISION := no

include $(FRAMEWORK_DIR)/app.mk
