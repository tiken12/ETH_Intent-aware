#!/usr/bin/env bash
export INTENT_GUARD_CONFIG=${INTENT_GUARD_CONFIG:-config.yaml}
uvicorn main:app --reload --port 8000
