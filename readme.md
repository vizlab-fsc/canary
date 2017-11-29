## Setup

Using [`python-lambda`](https://github.com/nficano/python-lambda)

- Create an IAM role called `lambda_basic_execution` with the policies:
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
- See your [Lambda service here](https://console.aws.amazon.com/lambda/home?region=us-east-1#)

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
