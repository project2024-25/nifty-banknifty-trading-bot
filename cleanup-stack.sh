#!/bin/bash

# Force cleanup script for DELETE_FAILED CloudFormation stack
# Run this manually in GitHub Actions or locally with AWS CLI configured

STACK_NAME="nifty-banknifty-trading-bot-dev"
REGION="ap-south-1"

echo "🚨 Starting DELETE_FAILED stack recovery for $STACK_NAME..."

# Check current stack status
STACK_STATUS=$(aws cloudformation describe-stacks --stack-name $STACK_NAME --region $REGION --query 'Stacks[0].StackStatus' --output text 2>/dev/null || echo "DOES_NOT_EXIST")
echo "Current stack status: $STACK_STATUS"

if [ "$STACK_STATUS" = "DELETE_FAILED" ]; then
    echo "🗑️ Stack is in DELETE_FAILED state, performing manual resource cleanup..."
    
    # 1. Delete Lambda functions
    echo "⚡ Deleting Lambda functions..."
    for func in mainTrading preMarketAnalysis postMarketReporting healthCheck youtubeAnalysis; do
        FULL_NAME="$STACK_NAME-$func"
        echo "Deleting function: $FULL_NAME"
        aws lambda delete-function --function-name "$FULL_NAME" --region $REGION 2>/dev/null || echo "Function $FULL_NAME not found"
    done
    
    # 2. Delete S3 buckets
    echo "🗂️ Deleting S3 buckets..."
    aws s3api list-buckets --query "Buckets[?contains(Name, '$STACK_NAME')].Name" --output text 2>/dev/null | tr '\t' '\n' | while read bucket; do
        if [ ! -z "$bucket" ]; then
            echo "Processing bucket: $bucket"
            aws s3 rm s3://$bucket --recursive --region $REGION 2>/dev/null || echo "Bucket empty or inaccessible"
            aws s3api delete-bucket --bucket "$bucket" --region $REGION 2>/dev/null || echo "Could not delete bucket"
        fi
    done
    
    # 3. Delete CloudWatch Log Groups
    echo "📋 Deleting CloudWatch Log Groups..."
    aws logs describe-log-groups --log-group-name-prefix "/aws/lambda/$STACK_NAME" --region $REGION --query 'logGroups[*].logGroupName' --output text 2>/dev/null | tr '\t' '\n' | while read log_group; do
        if [ ! -z "$log_group" ]; then
            echo "Deleting log group: $log_group"
            aws logs delete-log-group --log-group-name "$log_group" --region $REGION 2>/dev/null || echo "Log group already deleted"
        fi
    done
    
    # 4. Delete IAM Role and Policies
    echo "🔐 Deleting IAM resources..."
    ROLE_NAME="$STACK_NAME-$REGION-lambdaRole"
    
    # List and detach managed policies
    aws iam list-attached-role-policies --role-name "$ROLE_NAME" --query 'AttachedPolicies[*].PolicyArn' --output text 2>/dev/null | tr '\t' '\n' | while read policy_arn; do
        if [ ! -z "$policy_arn" ]; then
            echo "Detaching policy: $policy_arn"
            aws iam detach-role-policy --role-name "$ROLE_NAME" --policy-arn "$policy_arn" 2>/dev/null || echo "Policy already detached"
        fi
    done
    
    # List and delete inline policies
    aws iam list-role-policies --role-name "$ROLE_NAME" --query 'PolicyNames' --output text 2>/dev/null | tr '\t' '\n' | while read policy_name; do
        if [ ! -z "$policy_name" ]; then
            echo "Deleting inline policy: $policy_name"
            aws iam delete-role-policy --role-name "$ROLE_NAME" --policy-name "$policy_name" 2>/dev/null || echo "Policy already deleted"
        fi
    done
    
    # Delete the role itself
    echo "Deleting IAM role: $ROLE_NAME"
    aws iam delete-role --role-name "$ROLE_NAME" 2>/dev/null || echo "Role not found or already deleted"
    
    # 5. Delete CloudWatch Alarms
    echo "⏰ Deleting CloudWatch Alarms..."
    aws cloudwatch describe-alarms --alarm-name-prefix "$STACK_NAME" --region $REGION --query 'MetricAlarms[*].AlarmName' --output text 2>/dev/null | tr '\t' '\n' | while read alarm_name; do
        if [ ! -z "$alarm_name" ]; then
            echo "Deleting alarm: $alarm_name"
            aws cloudwatch delete-alarms --alarm-names "$alarm_name" --region $REGION 2>/dev/null || echo "Alarm already deleted"
        fi
    done
    
    # 6. Delete SQS Queues
    echo "📨 Deleting SQS Queues..."
    aws sqs list-queues --queue-name-prefix "$STACK_NAME" --region $REGION --query 'QueueUrls' --output text 2>/dev/null | tr '\t' '\n' | while read queue_url; do
        if [ ! -z "$queue_url" ]; then
            echo "Deleting queue: $queue_url"
            aws sqs delete-queue --queue-url "$queue_url" --region $REGION 2>/dev/null || echo "Queue already deleted"
        fi
    done
    
    # 7. Wait and force delete the stack
    echo "⏳ Waiting 30 seconds before stack deletion..."
    sleep 30
    
    echo "🗑️ Attempting to delete CloudFormation stack..."
    aws cloudformation delete-stack --stack-name $STACK_NAME --region $REGION 2>/dev/null || echo "Stack deletion initiated"
    
    # 8. Wait and check final status
    echo "⏳ Waiting 60 seconds to check final status..."
    sleep 60
    
    FINAL_STATUS=$(aws cloudformation describe-stacks --stack-name $STACK_NAME --region $REGION --query 'Stacks[0].StackStatus' --output text 2>/dev/null || echo "DELETED")
    echo "Final stack status: $FINAL_STATUS"
    
    if [ "$FINAL_STATUS" = "DELETED" ] || [ "$FINAL_STATUS" = "DOES_NOT_EXIST" ]; then
        echo "✅ Stack successfully deleted!"
    else
        echo "⚠️ Stack still exists with status: $FINAL_STATUS"
        echo "Manual intervention may be required via AWS Console"
    fi
    
else
    echo "✅ Stack status is $STACK_STATUS - no cleanup needed"
fi

echo "🎯 Cleanup process completed"