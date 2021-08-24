#!/bin/bash
# Copyright (c) 2021 Oracle and/or its affiliates.
# Unset current variables and reset TNS_ADMIN and LD_LIBRARY_PATH.
unset TNS_ADMIN
unset LD_LIBRARY_PATH

export LD_LIBRARY_PATH=/home/$USER/git/devrel-esports/pkg/instantclient_21_1:$LD_LIBRARY_PATH
export TNS_ADMIN=/home/$USER/git/devrel-esports/pkg/instantclient_21_1/network/admin

source ~/.bashrc