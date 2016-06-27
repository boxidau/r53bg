#!/usr/bin/env bash

ZONEID=$1
RECORD=$2

aws route53 list-resource-record-sets --hosted-zone-id $ZONEID --query "ResourceRecordSets[?Name=='$RECORD'][].{ID:SetIdentifier,Weight:Weight,Name:Name}" --output table