## Setup

Using [`python-lambda`](https://github.com/nficano/python-lambda)

- Create an IAM Lambda role called `lambda_basic_execution` with the policies:
    - `AWSLambdaExecute`
    - `AWSLambdaBasicExecutionRole`
- Create a new Lambda project: `lambda init`
- Edit the files accordingly
    - `config.yaml` needs
        - update function name and description as needed
        - `role: lambda_basic_execution` should be uncommented
        - add your access key id and secret access key (better that these are at `~/.aws/credentials` under the `[default]` section)
    - `event.json` contains test data for when using `invoke` (see below)
    - `service.py` defines the actual function.
    - You can create a subpackage `lib` (or others, just add them to `build: source_directions:` in `config.yaml`)
- Create a `requirements.txt` with the requirements needed for your function.
- Test your function with `lambda invoke -v`.
- Deploy with `lambda deploy --use-requirements`
    - Note: if the lambda package is too large, you can upload to S3 and deploy that way.
    - First, create an S3 bucket.
    - Add the S3 Full Access policy to your lambda role.
    - In `config.yaml`, add:
        - `bucket_name: <YOUR BUCKET NAME>`
        - `s3_key_prefix: <LAMBDA NAME>/`
    - Then do `lambda deploy_s3 --use-requirements`
- In the AWS Lambda dashboard for your function, make sure to place it in an appropriate subnet (a private one, see below) and include the security groups for your VPC, and one to communicate externally too
- See your [Lambda service here](https://console.aws.amazon.com/lambda/home?region=us-east-1#)

If you want your lambda function to access the internet, you also need:

- the lambda role to have full VPC access (`AWSLambdaVPCAccessExecutionRole`)
- a VPC with a public and private subnet
    - a public subnet is one that, in its route table, has a `0.0.0.0/0 -> igw-<ID>` route (i.e. a route to an internet gateway)
    - a private subnet is one that doesn't have such a route
        - note you may need to create a separate route table for the private subnet if you don't already have one
- your lambda function must be on the private subnet
- a NAT gateway created on the public subnet
    - in the VPC management console, choose "NAT Gateways"
    - create a new NAT gateway
        - choose your public subnet
        - then choose or create a new ElasticIP (EIP) address
- edit the route tables for your private subnet
    - select the route table associated with your VPC
    - then select the "Routes" tab below
    - then add a route with destination `0.0.0.0/0` and choose your NAT gateway as the target

In the end, the roles on our `lambda_basic_execution` role were:

- AmazonS3FullAccess
- AWSLambdaExecute
- AWSLambdaBasicExecutionRole
- AWSLambdaVPCAccessExecutionRole
- AmazonSNSFullAccess

Note on `psycopg2` -- it has to be manually included. The package can be acquired through this repo:

```
git clone git@github.com:jkehler/awslambda-psycopg2.git
mv awslambda-psycopg2/psycopg2-3.6 lambda/pkgs/psycopg2

# e.g.
cd arbiter
ln -s ../pkgs/psycopg2 psycopg2
```

Then make sure to include it in `config.yaml` under `build: source_directories:`:

```
build:
  source_directories: lib, psycopg2
```

For `PIL` we encounter a similar issue. There isn't a pre-prepared package available, so we have to it ourselves.

1. Install `docker-ce` (you can do it on a Digital Ocean box, for example)
2. Run this to launch the container meant to simulate an AWS Python 3.6 environment: `docker run --rm -it -v "/path/to/host/folder:/code" lambci/lambda:build-python3.6 sh`
3. You should be dropped into a shell in the container. Run `cd /code`
4. Then create a virtual env: `virtualenv env`
5. Activate it: `source env/bin/activate`
6. Install `Pillow`: `pip install pillow`
7. Disconnect from the container. You should see the env in `/path/to/host/folder/env`. Grab `env/lib/python3.6/site-packages/PIL` and then use it like the `psycopg2` package.

Repeat for `numpy`


## SNS Setup

- Create [an SNS topic here](https://console.aws.amazon.com/sns/v2/home?region=us-east-1)
- Subscribing a function to a topic:
    - Select your topic
    - Click "Create Subscription"
    - Change the "Protocol" to "AWS Lambda"
    - For "Endpoint", select your lambda function
- Publishing from a function to a topic:
    - Ensure that the Lambda role you're using has permission to publish to SNS topics

## Logging

```python
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
```

- [Reference](http://docs.aws.amazon.com/lambda/latest/dg/python-logging.html)
- [View logs here](https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#logs:)

## Scheduling

- Create a ["Schedule" rule here](https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#rules:action=create)
- Select your function as the "Target"

- [Reference](http://docs.aws.amazon.com/AmazonCloudWatch/latest/events/RunLambdaSchedule.html)


