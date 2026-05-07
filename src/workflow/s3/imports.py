from workflow.s3.status_checker_s3 import StatusCheckerS3
from workflow.s3.s3_remove_pii import S3RemovePii
from workflow.s3.s3_get_file import S3GetFile


#invocation source class
S3 = ["StatusCheckerS3", "S3RemovePii", "S3GetFile"]