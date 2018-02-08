#!/bin/bash

. secret
cd $1
AWS_PROFILE=vizlab lambda deploy_s3 --use-requirements
