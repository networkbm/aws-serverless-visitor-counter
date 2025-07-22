# AWS Serverless Visitor Counter

A fully serverless visitor counter using AWS Lambda, API Gateway, DynamoDB, and S3.

## Features

- Real-time visitor tracking
- IP-based rate limiting (30 seconds)
- Hosted with API Gateway and S3
- Logs to CloudWatch
- Zero-cost with AWS Free Tier
- Billing alerts via AWS Budgets

## Technologies

- AWS Lambda (Python)
- Amazon API Gateway
- Amazon DynamoDB
- Amazon S3 (static hosting)
- IAM Roles
- CloudWatch Logs

## Sample Output

```json
{
  "count": 82,
  "message": "Rate limit enforced"
}
```

## Architecture

```
Visitor --> API Gateway --> Lambda (Python) --> DynamoDB Tables
                                      ↳ CloudWatch Logs
```

## Notes

Budget set to $0.01 for zero-cost monitoring. Free Tier only resources used.
