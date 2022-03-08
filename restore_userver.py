import boto3
from datetime import date, timedelta

resource = boto3.resource('s3')
client = boto3.client('s3')
glacier_names = ["DEEP_ARCHIVE", 'GLACIER'] # The name changed at some point. I can't be bothered to figure out what the new and correct one is.


# Copied (and adapted) from https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Object.restore_object
def restore_object(bucket, key, keep_restored_days, restore_tier):
    obj = resource.Object(bucket, key)
    if obj.storage_class in glacier_names:
        # Try to restore the object if the storage class is glacier and
        # the object does not have a completed or ongoing restoration
        # request.
        if obj.restore is None:
            print('Submitting restoration request: %s' % obj.key)
            obj.restore_object(RestoreRequest={'Days': keep_restored_days,
                                               'GlacierJobParameters': {
                                                   'Tier': restore_tier
                                               },
                                               'Type': 'SELECT',
                                               'Tier': restore_tier})
            quit()
        # Print out objects whose restoration is on-going
        elif 'ongoing-request="true"' in obj.restore:
            print('Restoration in-progress: %s' % obj.key)
        # Print out objects whose restoration is complete
        elif 'ongoing-request="false"' in obj.restore:
            print('Restoration complete: %s' % obj.key)


# Config:
bucket = "ssp-userver-logs-virginia"
log_types = ["imp", "noad", "click"]
log_date = date(2021, 1, 1)
end_date = date.today() - timedelta(days=99)  # Objects are moved to glacier after 100 days, plus a bit of buffer
keep_restored_days = 25
restore_tier = "Standard"


paginator = client.get_paginator('list_objects_v2')

delta = timedelta(days=1)
while log_date <= end_date:
    for log_type in log_types:

        log_date_str = log_date.strftime("%Y-%m-%d")
        log_date += delta

        print(f"Iterating over: {log_type} {log_date_str} ")
        pages = paginator.paginate(Bucket=bucket,
                                   Prefix=f'{log_type}/{log_date_str}',
                                   )
        for page in pages:
            for obj in page['Contents']:
                print(obj["Key"], obj['StorageClass'])
                if obj['StorageClass'] in glacier_names:
                    restore_object(bucket, obj["Key"], keep_restored_days, restore_tier)
