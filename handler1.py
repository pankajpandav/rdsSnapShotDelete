# Delete snapshots older than retention period

import boto3
import os
from botocore.exceptions import ClientError

from datetime import datetime,timedelta

def delete_snapshot(snapshot_id):
    print "Deleting snapshot %s " % (snapshot_id)
    try:
        rdsresource = boto3.resource('rds')
        snapshot = rdsresource.Snapshot(snapshot_id)
        snapshot.delete()
    except ClientError as e:
        print "Caught exception: %s" % e

    return

def snapShotDeleteRDS(event, context):

    # Get current timestamp in UTC
    now = datetime.now()
	# Define retention period in days
    retention_days = 60

    # Create EC2 client
    rds = boto3.client('rds')

    # Get list of regions
    #regions = ['ap-southeast-2']

    # Iterate over regions

    #reg='ap-southeast-2'

    # Connect to region
    #rds = boto3.client('ec2', region_name=reg)

    # Filtering by snapshot timestamp comparison is not supported
    # So we grab all snapshot id's
    result = rds.describe_db_snapshots( OwnerIds=[os.environ['ACNT_ID']] )

    for snapshot in result['Snapshots']:
        print "Checking snapshot %s which was created on %s" % (snapshot['SnapshotId'],snapshot['StartTime'])

        # Remove timezone info from snapshot in order for comparison to work below
        snapshot_time = snapshot['StartTime'].replace(tzinfo=None)

        # Subtract snapshot time from now returns a timedelta
        # Check if the timedelta is greater than retention days
        if (now - snapshot_time) > timedelta(retention_days):
            if snapshot.tags is None:
                print "Snapshot is older than configured retention of %d days" % (retention_days)
                delete_snapshot(snapshot['SnapshotId'], reg)
        else:
            print "Snapshot is newer than configured retention of %d days so we keep it" % (retention_days)
