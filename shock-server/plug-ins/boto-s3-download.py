#!/usr/bin/python

# boto3 python client to download files from S3 and check md5
# AWS_ACCESS_KEY_ID .. The access key for your AWS account.
# AWS_SECRET_ACCESS_KEY .. The secret key for your AWS account.

# folker@anl.gov

import sys, getopt, boto3, hashlib, io
import argparse

def md5sum(src, length=io.DEFAULT_BUFFER_SIZE):
    md5 = hashlib.md5()
    with io.open(src, mode="rb") as fd:
        for chunk in iter(lambda: fd.read(length), b''):
            md5.update(chunk)
    return md5.hexdigest()


def usage():
   print ('test.py --md5 <MD5 checksum> ---access_key <AWS_ACCESS_KEY> --key_id <AWS_KEY_ID> --tmpfile <FILENAME> --objectname <OBJECT> --bucket <BUCKET> --md5 <MD5>')


def main():

   parser = argparse.ArgumentParser()
   parser.add_argument("-a","--keyid", default="None", help=" aws_access_key_id")
   parser.add_argument("-b","--bucket", default="None", help="AWS bucket")
   parser.add_argument("-t","--tmpfile",  default="None",help="filename to create")
   parser.add_argument("-o","--objectname",  default="None",help="object to download")
   parser.add_argument("-m","--md5",  default="None", help="md5 hash")
   parser.add_argument("-k","--accesskey",  default="None", help="aws_secret_access_key")
   parser.add_argument("-v", "--verbose", action="count", default=0, help="increase output verbosity")
   parser.add_argument("-r","--region", default="None", help="AWS region")
   parser.add_argument("-s","--s3endpoint",  default="https://s3.it.anl.gov:18082") 
   args = parser.parse_args()

    
   if args.verbose:
      print ('keyId  is =', args.keyid)
      print ('accessKey is =', args.accesskey)
      print ('bucket is =', args.bucket)
      print ('tmpfile is =', args.tmpfile)
      print ('md5 is =', args.md5)
      print ('region is=', args.region)
      print ('object is =', args.objectname)

   if args.tmpfile is None:
      usage
      print ('we need a filename')
      sys.exit(2)  


   # if passed use credentials to establish connection
   if args.accesskey is "None":
      if args.verbose:
         print ('using existing credentials from ENV vars or files')
      s3 = boto3.client('s3',
            endpoint_url=args.s3endpoint,
            region_name=args.region
            )
   else:
   # use env. default for connection details --> see  https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html
      if args.verbose:
         print ('using credentials from cmd-line')
      s3 = boto3.client('s3',
         endpoint_url=args.s3endpoint,
         region_name=args.region,
         aws_access_key_id=args.keyid,
         aws_secret_access_key=args.accesskey
      )

   with open(args.tmpfile, 'wb') as f:
      s3.download_fileobj(args.bucket, args.objectname, f)
   
   md5_new = md5sum(args.tmpfile)

   # check md5
   if args.md5 is None:
      #if args.verbose:
      print ('exiting without checking md5, md5_new=', md5_new)
      sys.exit(0)

   # Finally compare original MD5 with freshly calculated
   if (args.md5 == md5_new):
      if args.verbose:
         print ("MD5 verified.")
      sys.exit(0)
   else:
      if args.verbose:
         print ("MD5 verification failed!.")
         print ('MD5=', args.md5, "NEW_MD5=", md5_new)

      sys.exit(1)


main()