# GitHub Actions OIDC Configuration for AWS

## Overview

This guide explains how to configure GitHub Actions to authenticate with AWS using OpenID Connect (OIDC) instead of storing long-lived AWS credentials (AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY) as secrets.

## Why Use OIDC?

**Benefits of OIDC over long-lived credentials:**
- ✅ **No credential rotation**: No need to manage and rotate AWS access keys
- ✅ **Enhanced security**: Credentials are short-lived tokens that expire automatically
- ✅ **Fine-grained permissions**: Use IAM role session tags and conditions for precise access control
- ✅ **Audit trail**: Better tracking of which GitHub workflows accessed AWS resources
- ✅ **No secret storage**: Eliminates the risk of leaked credentials in GitHub Secrets

## Prerequisites

- AWS account with IAM administrative access
- GitHub repository where you want to use AWS services
- AWS CLI installed (optional, for verification)

## Configuration Steps

### Step 1: Create an OIDC Identity Provider in AWS IAM

1. **Navigate to IAM Console** → Identity Providers → Add Provider

2. **Configure the Identity Provider:**
   - **Provider Type**: OpenID Connect
   - **Provider URL**: `https://token.actions.githubusercontent.com`
   - **Audience**: `sts.amazonaws.com`

3. **Using AWS CLI (Alternative):**
   ```bash
   aws iam create-open-id-connect-provider \
     --url https://token.actions.githubusercontent.com \
     --client-id-list sts.amazonaws.com \
     --thumbprint-list 6938fd4d98bab03faadb97b34396831e3780aea1
   ```

   > **Note**: The thumbprint `6938fd4d98bab03faadb97b34396831e3780aea1` is GitHub's OIDC thumbprint (verified November 2025). AWS can also automatically retrieve the thumbprint when you click "Get thumbprint" in the console. Always verify the current thumbprint in [GitHub's official documentation](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-amazon-web-services) before using.

### Step 2: Create an IAM Role for GitHub Actions

1. **Navigate to IAM Console** → Roles → Create Role

2. **Select Trusted Entity:**
   - **Trusted entity type**: Web identity
   - **Identity provider**: Select the OIDC provider you created (`token.actions.githubusercontent.com`)
   - **Audience**: `sts.amazonaws.com`

3. **Configure Trust Policy:**
   
   Replace the default trust policy with the following (customize for your repository):

   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Principal": {
           "Federated": "arn:aws:iam::<YOUR_AWS_ACCOUNT_ID>:oidc-provider/token.actions.githubusercontent.com"
         },
         "Action": "sts:AssumeRoleWithWebIdentity",
         "Condition": {
           "StringEquals": {
             "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
           },
           "StringLike": {
             "token.actions.githubusercontent.com:sub": "repo:<YOUR_GITHUB_ORG>/<YOUR_REPO_NAME>:*"
           }
         }
       }
     ]
   }
   ```

   **Important**: Replace:
   - `<YOUR_AWS_ACCOUNT_ID>` with your AWS account ID (e.g., `123456789012`)
   - `<YOUR_GITHUB_ORG>/<YOUR_REPO_NAME>` with your repository (e.g., `ahkazak23/projectboard`)

   **More restrictive condition examples:**

   - **Specific branch only:**
     ```json
     "token.actions.githubusercontent.com:sub": "repo:ahkazak23/projectboard:ref:refs/heads/main"
     ```

   - **Specific environment:**
     ```json
     "token.actions.githubusercontent.com:sub": "repo:ahkazak23/projectboard:environment:production"
     ```

   - **Pull requests:**
     ```json
     "token.actions.githubusercontent.com:sub": "repo:ahkazak23/projectboard:pull_request"
     ```

4. **Attach Permissions Policy:**

   For this project (S3 document storage), attach or create a policy like:

   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Action": [
           "s3:GetObject",
           "s3:PutObject",
           "s3:DeleteObject",
           "s3:ListBucket"
         ],
         "Resource": [
           "arn:aws:s3:::projectboard-docs-381293813799-dev",
           "arn:aws:s3:::projectboard-docs-381293813799-dev/*"
         ]
       }
     ]
   }
   ```

5. **Name your role** (e.g., `GitHubActionsRole-ProjectBoard`)

6. **Save the Role ARN** - You'll need this for your GitHub workflow:
   ```
   arn:aws:iam::<YOUR_AWS_ACCOUNT_ID>:role/GitHubActionsRole-ProjectBoard
   ```

### Step 3: Configure GitHub Workflow

Update your GitHub Actions workflow to use OIDC authentication:

```yaml
name: Deploy to AWS

on:
  push:
    branches:
      - main

# Required for OIDC authentication
permissions:
  id-token: write
  contents: read

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Configure AWS Credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::<YOUR_AWS_ACCOUNT_ID>:role/GitHubActionsRole-ProjectBoard
          aws-region: us-east-1
          # Optional: role session name for better audit trails
          role-session-name: GitHubActions-${{ github.run_id }}

      - name: Verify AWS Identity
        run: aws sts get-caller-identity

      - name: Test S3 Access
        run: |
          aws s3 ls s3://projectboard-docs-381293813799-dev/
```

### Step 4: GitHub Repository Configuration

**Important**: You do **NOT** need to configure anything in GitHub repository settings for basic OIDC to work. The OIDC provider is configured entirely on the AWS side.

However, you may want to:

1. **Remove old AWS credentials** from GitHub Secrets:
   - Go to repository Settings → Secrets and variables → Actions
   - Delete `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` if they exist

2. **Store the Role ARN as a secret** (optional, for easier management):
   - Add a new repository secret: `AWS_ROLE_ARN`
   - Value: `arn:aws:iam::<YOUR_AWS_ACCOUNT_ID>:role/GitHubActionsRole-ProjectBoard`
   - Update workflow to use: `role-to-assume: ${{ secrets.AWS_ROLE_ARN }}`

## Testing Your Configuration

1. **Push a commit** to trigger your workflow

2. **Check the workflow logs** for the "Configure AWS Credentials" step

3. **Verify successful authentication** in the "Verify AWS Identity" step output

4. **Look for this in logs:**
   ```
   Requesting token
   Assuming role with OIDC
   Successfully configured AWS credentials
   ```

## Troubleshooting

### Error: "Not authorized to perform sts:AssumeRoleWithWebIdentity"

**Causes:**
- Trust policy doesn't match your repository
- OIDC provider not configured correctly in AWS
- Wrong audience in trust policy

**Solution:**
- Verify the trust policy `sub` condition matches your repo exactly
- Check that audience is `sts.amazonaws.com`
- Ensure OIDC provider exists in IAM

### Error: "Missing required permissions"

**Cause:** The IAM role doesn't have the necessary permissions

**Solution:**
- Review and update the role's permissions policy
- Ensure the S3 bucket name is correct
- Check for typos in resource ARNs

### Error: "Unable to get OIDC token"

**Cause:** Missing `id-token: write` permission in workflow

**Solution:**
```yaml
permissions:
  id-token: write
  contents: read
```

### Error: "Access Denied" when accessing S3

**Causes:**
- Bucket name mismatch
- Missing S3 permissions in IAM role
- Bucket policy blocking access

**Solution:**
- Verify bucket name in environment variables
- Check IAM role has S3 permissions
- Review S3 bucket policy

## Security Best Practices

1. **Use least privilege**: Grant only the minimum permissions needed
2. **Restrict by branch/environment**: Use specific conditions in trust policy
3. **Enable CloudTrail**: Monitor all AWS API calls from GitHub Actions
4. **Regular audits**: Review IAM roles and their usage periodically
5. **Session tags**: Use role session names for better audit trails
6. **Time-based conditions**: Add time restrictions if workflows run on schedule

## Example: Full Workflow with OIDC

```yaml
name: CI/CD with OIDC

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

permissions:
  id-token: write
  contents: read

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.10"
      
      - name: Install dependencies
        run: |
          pip install poetry
          poetry install
      
      - name: Run tests
        run: poetry run pytest

  deploy:
    needs: test
    runs-on: ubuntu-latest
    # Only deploy from main branch
    if: github.ref == 'refs/heads/main'
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Configure AWS Credentials via OIDC
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ secrets.AWS_ROLE_ARN }}
          aws-region: us-east-1
          role-session-name: Deploy-${{ github.run_number }}
      
      - name: Verify S3 access
        run: |
          echo "Testing S3 bucket access..."
          aws s3 ls s3://projectboard-docs-381293813799-dev/
      
      - name: Deploy application
        run: |
          echo "Deployment steps here..."
```

## Additional Resources

- [GitHub OIDC Documentation](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/about-security-hardening-with-openid-connect)
- [AWS IAM OIDC Documentation](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_providers_create_oidc.html)
- [aws-actions/configure-aws-credentials](https://github.com/aws-actions/configure-aws-credentials)

## Summary

**Do you need to configure anything on the GitHub side?**

**Answer**: **NO** - You do **not** need to configure anything in GitHub repository settings for OIDC to work. All OIDC configuration is done on the AWS side (IAM Identity Provider and IAM Role). 

However, you **do** need to:
1. ✅ Update your GitHub Actions workflow file to include `permissions: id-token: write`
2. ✅ Use the `aws-actions/configure-aws-credentials` action with `role-to-assume`
3. ✅ (Optional) Store the role ARN as a GitHub secret for easier management
4. ✅ (Recommended) Remove old AWS access keys from GitHub Secrets

The GitHub Actions runner will automatically request an OIDC token from GitHub's OIDC provider, and AWS will validate it based on your IAM trust policy configuration.
