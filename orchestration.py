pipeline = {
    "StartAt": "Validate",
    "States": {
        "Validate": {
            "Type": "Task",
            "Resource": "arn:aws:lambda:us-east-1:000000000000:function:validate-fn",
            "Next": "CheckValidation",
            "Retry": [{"ErrorEquals": ["States.ALL"], "MaxAttempts": 2}]
        },
        "CheckValidation": {
            "Type": "Choice",
            "Choices": [{'Variable': '$.valid', 'BooleanEquals': True, 'Next': 'Transform'}],
            "Default": "NotifyError"
        },
        "Transform": {
            "Type": "Task",
            "Resource": "arn:aws:lambda:us-east-1:000000000000:function:transform-fn",
            "Next": "Cataloger",
        },
        "Cataloger": {
            "Type": "Task",
            "Resource": "arn:aws:lambda:us-east-1:000000000000:function:cataloger-fn",
            "Next": "NotifySuccess"
        },
        "NotifySuccess": {
            "Type": "Task",
            "Resource": "arn:aws:lambda:us-east-1:000000000000:function:notify-fn",
            "End": True
        },
        "NotifyError": {
            "Type": "Task",
            "Resource": "arn:aws:lambda:us-east-1:000000000000:function:notify-fn",
            "End": True
        }
    }
}

