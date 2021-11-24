#!/bin/bash
# -*- coding: utf-8 -*-
#
# Build lambda deployment package in container locally

dir_here="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
dir_project_root="$(dirname "${dir_here}")"

rm -r "${dir_project_root}/app/vendor/pgr"
cp -r "${dir_project_root}/pgr" "${dir_project_root}/app/vendor/pgr"

${bin_chalice} deploy
