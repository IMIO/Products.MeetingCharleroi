#!/bin/sh
/srv/archgenxml/bin/archgenxml --cfg generate.conf MeetingCharleroi.zargo -o tmp

# only keep workflows
cp -rf tmp/profiles/default/workflows ../profiles/default
rm -rf tmp
