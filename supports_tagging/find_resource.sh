#!/usr/bin/env bash

grep "func Resource" $1 | cut -d'(' -f1 | awk '{print $2}' | xargs -I{} grep {} internal/provider/provider.go
