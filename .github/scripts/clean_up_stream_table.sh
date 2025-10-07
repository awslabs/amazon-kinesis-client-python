#!/bin/bash

aws kinesis delete-stream --stream-name $STREAM_NAME || true

# Reset the values of checkpoint, leaseCounter, ownerSwitchesSinceCheckpoint, and leaseOwner in DynamoDB table
echo "Resetting DDB table"
aws dynamodb update-item \
  --table-name $APP_NAME \
  --key '{"leaseKey": {"S": "shardId-000000000000"}}' \
  --update-expression "SET checkpoint = :checkpoint, leaseCounter = :counter, ownerSwitchesSinceCheckpoint = :switches, leaseOwner = :owner" \
  --expression-attribute-values '{
    ":checkpoint": {"S": "TRIM_HORIZON"},
    ":counter": {"N": "0"},
    ":switches": {"N": "0"},
    ":owner": {"S": "AVAILABLE"}
  }' \
  --return-values NONE