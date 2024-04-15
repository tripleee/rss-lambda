from aws_cdk import (
    aws_events as events,
    aws_lambda_python_alpha as py_lambda,
    aws_events_targets as targets,
    App, Duration, Stack
)


class LambdaCronStack(Stack):
    def __init__(self, app: App, id: str) -> None:
        super().__init__(app, id)

        lambdaFn = py_lambda.Function(
            self, "rss-lambda",
            code=py_lambda.Code.from_asset("rss_lambda.py"),
            entry=".",
            handler="rss_lambda.main",
            timeout=Duration.seconds(300),
            runtime=py_lambda.Runtime.PYTHON_3_12,
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


app = App()
LambdaCronStack(app, "LambdaCronExample")
app.synth()
