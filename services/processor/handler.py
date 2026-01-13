def handle(event, context):
    for record in event["Records"]:
        print("Processing message:", record["body"])
