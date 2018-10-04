import boto3
import os
from datetime import datetime
import time
import logging
import re
from snapshots_tool_utils import *


#Initialize everything
#DEST_REGION = os.getenv('DEST_REGION', os.getenv('region')).strip()
LOGLEVEL = os.getenv('LOG_LEVEL', 'ERROR').strip()
PATTERN = os.getenv('PATTERN', 'ALL_INSTANCES')
RETENTION_DAYS =  int(os.getenv('RETENTION_DAYS','60'))
TIMESTAMP_FORMAT = '%Y-%m-%d-%H-%M'

#if os.getenv('REGION_OVERRIDE', 'NO') != 'NO' :
#    REGION = os.getenv('REGION_OVERRIDE').strip()
#else:
#    REGION = os.getenv('AWS_DEFAULT_REGION')

logger = logging.getLogger()
logger.setLevel(LOGLEVEL.upper())


def snapShotDeleteRDS(event, context):
    pending_delete = 0
    #search for all snapshots
    client = boto3.client('rds')
    response = paginate_api_call(client, 'describe_db_snapshots', 'DBSnapshots')
    filtered_list = get_own_snapshots_source(PATTERN, response)

    for snapshot in filtered_list.keys():
        creation_date = get_timestamp(snapshot, filtered_list)
        if creation_date:
            difference = datetime.now() - creation_date
            days_difference = difference.total_Seconds() / 3600 / 24
            logger.debug('%s created %s days ago' % (snapshot, days_difference))

            # if we are past RETENTION_DAYS
            if days_difference > RETENTION_DAYS:
                #delete it
                logger.info('Deleting %s' % snapShotDeleteRDS)

                try:
                    client.delete_db_snapshot(DBSnapshotIdentifier=snapshot)

                except Exception:
                    pending_delete += 1
                    logger.info('Could not delete %s ' % snapshot)

        else:
            logger.info('Not deleting %s . Creaed only %s ' % (snapshot, days_difference))

    if pending_delete > 0:
        message = 'Snapshots pending delete: %s ' % pending_delete
        logger.error(message)
        #raise SnapshotToolException(message)
