# AWS OIDC Setup Checklist

Use this checklist to set up OIDC authentication for GitHub Actions with AWS.

## ✅ Pre-Setup

- [ ] Have AWS account with IAM admin access
- [ ] Know your AWS Account ID: `_______________`
- [ ] Know your GitHub repo: `owner/repo-name`
- [ ] Have AWS CLI installed (optional)

## ✅ Step 1: AWS IAM - Create OIDC Provider

- [ ] Open AWS Console → IAM → Identity Providers
- [ ] Click "Add Provider"
- [ ] Select "OpenID Connect"
- [ ] Enter Provider URL: `https://token.actions.githubusercontent.com`
- [ ] Enter Audience: `sts.amazonaws.com`
- [ ] Click "Get thumbprint" (or use: `6938fd4d98bab03faadb97b34396831e3780aea1`)
- [ ] Click "Add provider"
- [ ] **Save the provider ARN**: `_________________________________`

**OR via AWS CLI:**
```bash
aws iam create-open-id-connect-provider \
  --url https://token.actions.githubusercontent.com \
  --client-id-list sts.amazonaws.com \
  --thumbprint-list 6938fd4d98bab03faadb97b34396831e3780aea1
```

## ✅ Step 2: AWS IAM - Create Role

### 2.1 Basic Role Setup

- [ ] Open AWS Console → IAM → Roles
- [ ] Click "Create role"
- [ ] Select "Web identity"
- [ ] Choose identity provider: `token.actions.githubusercontent.com`
- [ ] Choose audience: `sts.amazonaws.com`
- [ ] Click "Next"

### 2.2 Configure Trust Policy

- [ ] Click "Edit trust policy"
- [ ] Replace with this policy (update `<ACCOUNT_ID>` and `<ORG>/<REPO>`):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
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
    }
  ]
}
```

- [ ] Click "Next"

### 2.3 Attach Permissions

- [ ] Create or select a policy with required permissions
- [ ] For S3 access, use this policy (update bucket name):

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
        "arn:aws:s3:::your-bucket-name",
        "arn:aws:s3:::your-bucket-name/*"
      ]
    }
  ]
}
```

- [ ] Attach the policy to the role
- [ ] Click "Next"

### 2.4 Name and Create

- [ ] Enter role name: `GitHubActionsRole-ProjectBoard`
- [ ] Enter description: "Role for GitHub Actions OIDC authentication"
- [ ] Click "Create role"
- [ ] **Save the role ARN**: `_________________________________`

## ✅ Step 3: Update GitHub Workflow

- [ ] Open your workflow file (e.g., `.github/workflows/deploy.yml`)
- [ ] Add permissions section at the top:

```yaml
permissions:
  id-token: write
  contents: read
```

- [ ] Add AWS credentials configuration step:

```yaml
- name: Configure AWS Credentials
  uses: aws-actions/configure-aws-credentials@v4
  with:
    role-to-assume: arn:aws:iam::ACCOUNT_ID:role/GitHubActionsRole-ProjectBoard
    aws-region: us-east-1
```

- [ ] Commit and push the workflow changes

## ✅ Step 4: Configure GitHub Secrets (Optional but Recommended)

- [ ] Go to GitHub repo → Settings → Secrets and variables → Actions
- [ ] Click "New repository secret"
- [ ] Name: `AWS_ROLE_ARN`
- [ ] Value: (paste your role ARN)
- [ ] Click "Add secret"
- [ ] Update workflow to use: `role-to-assume: ${{ secrets.AWS_ROLE_ARN }}`

### Remove Old Credentials (if they exist)

- [ ] Delete secret: `AWS_ACCESS_KEY_ID`
- [ ] Delete secret: `AWS_SECRET_ACCESS_KEY`

## ✅ Step 5: Test Your Setup

- [ ] Push a commit to trigger the workflow
- [ ] Go to Actions tab in GitHub
- [ ] Watch the workflow run
- [ ] Check "Configure AWS Credentials" step - should show:
  - ✅ "Requesting token"
  - ✅ "Assuming role with OIDC"
  - ✅ "Successfully configured AWS credentials"

### Verify AWS Identity

Add this step to your workflow to verify:

```yaml
- name: Verify AWS Identity
  run: aws sts get-caller-identity
```

Expected output:
```json
{
  "UserId": "AROAXXXXXXXXX:GitHubActions-...",
  "Account": "123456789012",
  "Arn": "arn:aws:sts::123456789012:assumed-role/GitHubActionsRole-ProjectBoard/..."
}
```

## ✅ Troubleshooting

If something doesn't work, check:

- [ ] Trust policy `sub` condition exactly matches your repo name
- [ ] OIDC provider exists in IAM
- [ ] Role ARN is correct in workflow
- [ ] `permissions: id-token: write` is in workflow
- [ ] Audience is `sts.amazonaws.com` (not `sts.amazonaws.com.cn`)
- [ ] Role has required AWS permissions
- [ ] GitHub Actions has permission to run workflows

## ✅ Security Best Practices

- [ ] Use specific branch conditions in trust policy (not `*`)
- [ ] Use least privilege for IAM permissions
- [ ] Enable AWS CloudTrail for audit logging
- [ ] Review IAM role usage regularly
- [ ] Use session names for better audit trails
- [ ] Consider using GitHub Environments for production

## 📚 Additional Resources

- **Full Guide**: [AWS_OIDC_SETUP.md](../AWS_OIDC_SETUP.md)
- **Quick Start**: [OIDC_QUICK_START.md](./OIDC_QUICK_START.md)
- **Example Workflow**: [deploy-example.yml.disabled](./workflows/deploy-example.yml.disabled)
- **Project README**: [README.md](../README.md)

## ✅ Done!

Once all checkboxes are checked, your GitHub Actions workflows can securely authenticate to AWS using OIDC! 🎉

**Remember**: You do NOT need to configure anything in GitHub repository settings. All OIDC configuration is done in AWS IAM.
