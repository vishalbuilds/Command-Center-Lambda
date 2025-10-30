"""
S3Utils: A comprehensive utility class for AWS S3 operations.

This class provides high-level, descriptive methods for common S3 operations such as get, put, delete, and list objects.
All methods include logging and error handling for robust production use.
"""
from common.logger import Logger
from common.client_record import s3_client
from typing import Literal

logger = Logger(__name__)


def get_object(bucket, key,region_name):
    """
    Get an object from an S3 bucket.
    Args:
        bucket (str): The name of the S3 bucket.
        key (str): The object key.
    Returns:
        dict: The response from S3 get_object.
    Raises:
        Exception: If the operation fails.
    """
    try:
        logger.info(f"Getting object from bucket: {bucket}, key: {key}")
        return s3_client(region_name).get_object(Bucket=bucket, Key=key)
    except Exception as e:
        logger.error(f"Error getting object: {e}")
        raise

def put_object(bucket, key, body,region_name):
    """
    Put an object into an S3 bucket.
    Args:
        bucket (str): The name of the S3 bucket.
        key (str): The object key.
        body (bytes or str): The content to upload.
    Returns:
        dict: The response from S3 put_object.
    Raises:
        Exception: If the operation fails.
    """
    try:
        logger.info(f"Putting object to bucket: {bucket}, key: {key}")
        return s3_client(region_name).put_object(Bucket=bucket, Key=key, Body=body)
    except Exception as e:
        logger.error(f"Error putting object: {e}")
        raise

def delete_object( bucket, key,region_name):
    """
    Delete an object from an S3 bucket.
    Args:
        bucket (str): The name of the S3 bucket.
        key (str): The object key.
    Returns:
        dict: The response from S3 delete_object.
    Raises:
        Exception: If the operation fails.
    """
    try:
        logger.info(f"Deleting object from bucket: {bucket}, key: {key}")
        return s3_client(region_name).delete_object(Bucket=bucket, Key=key)
    except Exception as e:
        logger.error(f"Error deleting object: {e}")
        raise

def list_objects( prefix,bucket,region_name):
    """
    List objects in an S3 bucket, optionally filtered by prefix.
    Args:
        bucket (str): The name of the S3 bucket.
        prefix (str, optional): Prefix to filter objects.
    Returns:
        dict: The response from S3 list_objects_v2.
    Raises:
        Exception: If the operation fails.
    """
    try:
        logger.info(f"Listing objects in bucket: {bucket}, prefix: {prefix}")
        return s3_client(region_name).list_objects_v2(Bucket=bucket,Prefix=prefix)
    except Exception as e:
        logger.error(f"Error listing objects: {e}")
        raise 


def create_presigned_url(bucket,key,region_name,expiration=3600 ,operation :Literal["get_object", "put_object", "delete_object"] = "get_object"):
    """
    Generate a pre-signed URL for an S3 object.

    Args:
        bucket_name (str): S3 bucket name
        object_name (str): S3 object key
        operation (str): S3 operation ('get_object' or 'put_object')
        expiration (int): Time in seconds for the URL to remain valid

    Returns:
        str: Pre-signed URL as string, or None if error.
    """
    try:
        logger.info(f"Creating presign url for  {bucket}, prefix: {key}")
        return s3_client(region_name).generate_presigned_url(
            ClientMethod=operation,
            Params={"Bucket": bucket, "Key": key},
            ExpiresIn=expiration
        )
    except Exception as e:
        logger.error(f"Error listing objects: {e}")
        raise 

        
