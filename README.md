# RSS-Lambda

This is a simple Python lambda function for AWS
which scans an RSS feed and reports any new URLs
to a separate endpoint on https://ntfy.sh/
to generate notifications for new content.
It also sends a ping to https://healthchecks.io/
to allow that service to generate a warning if the lambda stops running.

The infrastructure for running as a lambda was copied from
https://github.com/aws-samples/aws-cdk-examples/tree/main/python/lambda-cron
and the simple `rss_lambda.py` is a very basic exercise of
the [`feedparser`](https://pypi.org/project/feedparser/) API.
In order to include the required dependencies (`feedparser` and `requests`)
I added the experimental
[`aws-cdk.aws-lambda-python-alpha`][1] package
and restructured the project to put the lambda code in a subdirectory
(otherwise `cdk deploy` would pick up its own `cdk.out` directory
and recurse indefinitely!)

  [1]: https://pypi.org/project/aws-cdk.aws-lambda-python-alpha/

The deployment script is a Github Action;
it and its infrastructure are built in accordance with
https://conermurphy.com/blog/automate-aws-cdk-stack-deployment-github-actions
but in order for that to work, you initially need to run `cdk bootstrap`
with significantly broader permissions
(in the end, I just used my AWS root account).

I doubt that this will be immediately useful to anybody else,
but I hope it can be helful as a template for other simple
Python lambda functions.

One of my goals was to make this self-contained and self-documenting,
but I had to perform some tasks locally.

* I created the `CDK_Deploy` IAM role manually in accordance with
  the CDK instructions from the blog.
* As noted above, `cdk bootstrap` requires significantly broader permissions.
  I ran the command locally with my main AWS account.
  (I tried to create a dedicated account with only the specific permissions
  that are required for this, but I gave up after some hours of bumping into
  yet more additional permission errors.)
* The generated lambda will write its logs into CloudWatch
  and the logs will not have any retention policy.
  I manually updated the CloudWatch seettings
  to flush out logs after 3 months.

In isolation, this should run comfortably within the free tier
according to my calculations so far.
Obviously, something which generates a lot of logs on every run
could run into CloudWatch quota issues.
