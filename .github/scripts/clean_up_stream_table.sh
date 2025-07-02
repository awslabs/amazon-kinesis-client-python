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

# Delete all tables
#for i in {1..5}; do
#  aws dynamodb delete-table --table-name $APP_NAME && break ||
#  echo "Retrying DynamoDB Table deletion in 10s" && sleep 10
#done
#for SUFFIX in "-CoordinatorState" "-WorkerMetricStats" "-LeaseManagement"; do
#  if aws dynamodb describe-table --table-name $APP_NAME$SUFFIX &>/dev/null; then
#    echo "Deleting table $APP_NAME$SUFFIX"
#    aws dynamodb delete-table --table-name $APP_NAME$SUFFIX || true
#  fi
#done