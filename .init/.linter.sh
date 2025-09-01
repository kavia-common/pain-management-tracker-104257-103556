#!/bin/bash
cd /home/kavia/workspace/code-generation/pain-management-tracker-104257-103556/pain_management_api
source venv/bin/activate
flake8 .
LINT_EXIT_CODE=$?
if [ $LINT_EXIT_CODE -ne 0 ]; then
  exit 1
fi

