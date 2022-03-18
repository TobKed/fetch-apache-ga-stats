#!/usr/bin/env bash
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

set -e

echo "This script checks for presence of variables."

function check_vars() {
  ret=true
  for var in "$@"; do
    if [ -n "${!var}" ]; then
      echo "$var is set"
    else
      echo >&2 "$var is not set"
      ret=false
    fi
  done
  $ret
}

echo "::set-output name=are-variables-set::true"

if ! check_vars ${@}; then
  echo "::set-output name=are-variables-set::false"
  echo >&2 "!!! WARNING !!!"
  echo >&2 "Not all variables are set. Jobs which require them will be skipped."
fi
