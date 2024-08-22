import logging

from aws_cdk import (
    aws_events as events,
    aws_lambda,
    aws_lambda_python_alpha as py_lambda,
    aws_events_targets as targets,
    App, Duration, Stack
)


class LambdaCronStack(Stack):
    def __init__(self, app: App, id: str) -> None:
        super().__init__(app, id)

        lambdaFn = py_lambda.PythonFunction(
            self, "rss-lambda",
            entry="rss_lambda",
            runtime=aws_lambda.Runtime.PYTHON_3_12,
            index="rss_lambda.py",
            handler="main",
            timeout=Duration.seconds(300),
        )

        # Run every five minutes
        # See https://docs.aws.amazon.com/lambda/latest/dg/tutorial-scheduled-events-schedule-expressions.html
        rule = events.Rule(
            self, "Rule",
            schedule=events.Schedule.cron(
                minute='*/5',
                hour='*',
                month='*',
                week_day='*',
                year='*'),
        )
        rule.add_target(targets.LambdaFunction(lambdaFn))


logging.getLogger().setLevel(logging.INFO)
app = App()
LambdaCronStack(app, "LambdaCronExample")
app.synth()
