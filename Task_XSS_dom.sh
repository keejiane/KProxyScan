#!/usr/bin/env bash
export C_FORCE_ROOT=1
/usr/local/bin/celery -A Task_XSS_dom worker --loglevel=info