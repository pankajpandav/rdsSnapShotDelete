# Delete snapshots older than retention period

import boto3
import os
from botocore.exceptions import ClientError
from datetime import datetime,timedelta

def snapShotDeleteRDS(event, context):

    # Get current timestamp in UTC
    now = datetime.now()
	# Define retention period in days
    retention_days = 60

    # Create RDS client
    rds = boto3.client('rds')

    result = rds.describe_db_snapshots()

    for snapshot in result['DBSnapshots']:
        print "Checking snapshot %s which was created on %s" % (snapshot['DBSnapshotIdentifier'],snapshot['SnapshotCreateTime'])

        # Remove timezone info from snapshot in order for comparison to work below
        snapshot_time = snapshot['SnapshotCreateTime'].replace(tzinfo=None)
        DBSnapID = snapshot['DBSnapshotIdentifier']
        # Subtract snapshot time from now returns a timedelta
        # Check if the timedelta is greater than retention days
        if (now - snapshot_time) > timedelta(retention_days):
            print "Snapshot is older than configured retention of %d days..deleting it!" % (retention_days)
            rds.delete_db_snapshot(DBSnapshotIdentifier = DBSnapID)
        else:
            print "Snapshot is newer than configured retention of %d days so we keep it" % (retention_days)
