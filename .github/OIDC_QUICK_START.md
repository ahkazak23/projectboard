# AWS OIDC Quick Start Guide

**Quick answer**: "Do I need to configure anything on the GitHub side for OIDC with AWS?"

**NO** - All OIDC configuration is done in AWS IAM. You only need to update your workflow file.

## 5-Minute Setup

### 1. AWS IAM - Create OIDC Provider (One-time)

```bash
aws iam create-open-id-connect-provider \
  --url https://token.actions.githubusercontent.com \
  --client-id-list sts.amazonaws.com \
  --thumbprint-list 6938fd4d98bab03faadb97b34396831e3780aea1
```

### 2. AWS IAM - Create Role with Trust Policy

**Trust Policy** (replace `<ACCOUNT_ID>` and `<ORG>/<REPO>`):

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {
      "Federated": "arn:aws:iam::<ACCOUNT_ID>:oidc-provider/token.actions.githubusercontent.com"
    },
    "Action": "sts:AssumeRoleWithWebIdentity",
    "Condition": {
      "StringEquals": {
        "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
      },
      "StringLike": {
        "token.actions.githubusercontent.com:sub": "repo:<ORG>/<REPO>:*"
      }
    }
  }]
}
```

**Permissions Policy** (S3 example):

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": ["s3:*"],
    "Resource": [
      "arn:aws:s3:::your-bucket",
      "arn:aws:s3:::your-bucket/*"
    ]
  }]
}
```

### 3. GitHub Workflow - Update Your YAML

```yaml
name: Deploy

on:
  push:
    branches: [main]

# ⚠️ REQUIRED for OIDC
permissions:
  id-token: write
  contents: read

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789012:role/YourRoleName
          aws-region: us-east-1
      
      - run: aws s3 ls  # Test it works!
```

### 4. GitHub Secrets (Optional)

- Add `AWS_ROLE_ARN` secret with your role ARN
- Use `role-to-assume: ${{ secrets.AWS_ROLE_ARN }}`
- Remove old `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`

## That's It! 

No GitHub repository settings changes needed. The magic happens through:
1. GitHub generates an OIDC token automatically
2. Your workflow requests AWS credentials using that token
3. AWS validates the token against your trust policy
4. AWS returns temporary credentials to your workflow

## Full Documentation

For detailed guide, troubleshooting, and best practices, see [AWS_OIDC_SETUP.md](../AWS_OIDC_SETUP.md)

## Common Issues

| Issue | Fix |
|-------|-----|
| "Not authorized to perform sts:AssumeRoleWithWebIdentity" | Check trust policy `sub` matches your repo exactly |
| "Unable to get OIDC token" | Add `permissions: id-token: write` to workflow |
| "Access Denied" on AWS resources | Update role's permissions policy |

## Links

- [Full Setup Guide](../AWS_OIDC_SETUP.md)
- [Example Workflow](../workflows/deploy-example.yml.disabled)
- [GitHub OIDC Docs](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/about-security-hardening-with-openid-connect)
