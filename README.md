# RSS-Lambda

This is a simple Python lambda function for AWS
which scans an RSS feed and reports any new URLs
to a separate endpoint on https://ntfy.sh/
to generate notifications for new content.

The infrastructure for running as a lambda was copied from
https://github.com/aws-samples/aws-cdk-examples/tree/main/python/lambda-cron
and the simple `rss_lambda.py`
is a very basic exercise of
the [`feedparser`](https://pypi.org/project/feedparser/) API.
The deployment script and infrastructure is built in accordance with
https://conermurphy.com/blog/automate-aws-cdk-stack-deployment-github-actions
but in order for that to work, you need to run `cdk bootstrap`
with significantly broader permissions
(in the end, I just used my root account after struggling for hours).

I doubt that this will be immediately useful to anybody else,
but I hope it can be helful as a template for other simple
Python lambda functions.
