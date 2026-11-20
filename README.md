# Serverless RAG Application using AWS

A starter project for asking questions about PDF documents using Amazon S3, Amazon Bedrock Knowledge Bases, AWS Lambda, API Gateway, and Terraform.

## Architecture

1. Upload PDF documents to the configured S3 bucket (the Knowledge Base data source uses this bucket).
2. Sync the Bedrock Knowledge Base data source to ingest/chunk/embed documents into its configured vector store.
3. The browser sends a question to API Gateway.
4. API Gateway invokes the Python Lambda function.
5. Lambda calls `bedrock-agent-runtime:RetrieveAndGenerate` and returns an answer plus source citations.

> This repository is an infrastructure-and-application starter, not a pre-provisioned AWS deployment. You must create/configure a Bedrock Knowledge Base and vector store, enable model access where required, and provide the IDs in Terraform variables. AWS charges may apply.

## Prerequisites

- AWS account and credentials configured locally (`aws configure` or an AWS profile)
- Terraform >= 1.5
- Python 3.11 (for local checks/package preparation)
- An Amazon Bedrock model and embedding model available in your chosen AWS region
- A Bedrock Knowledge Base with an S3 data source and vector store

## 1. Configure the Knowledge Base

In the AWS Console:
1. Open Amazon Bedrock → Knowledge Bases.
2. Create a Knowledge Base.
3. Select an S3 data source and point it to the S3 bucket created for your documents (or create the bucket first).
4. Choose an embedding model and configure a supported vector store.
5. Finish setup and copy the Knowledge Base ID.
6. Upload PDF/TXT/Markdown documents to the data source prefix (default `documents/`).
7. Run **Sync** on the data source after uploading documents.
8. Copy the data source ID as well if you want to automate sync separately (this starter does not automate sync).

The Knowledge Base's service role must be allowed to read the S3 data source and access its embedding model/vector store. Follow the Bedrock console setup wizard and AWS documentation for the selected vector store.

## 2. Configure Terraform

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars` and set:
- `aws_region`
- `knowledge_base_id`
- `model_arn` (the generation model ARN supported by Bedrock in your region)
- `allowed_origin` (your frontend origin; for local testing this may be `*`, but restrict it before production)

The Terraform creates the documents bucket, Lambda execution role/function, API Gateway HTTP API, and CloudWatch log group. If you already created a bucket for your Knowledge Base, either import/adapt the bucket resource or configure the Knowledge Base to use the bucket created by this project before creating the Knowledge Base. For the simplest sequence, create the bucket first using Terraform, then create the Knowledge Base using that bucket, then apply Terraform again with the Knowledge Base ID.

### Deploy

```bash
terraform init
terraform plan
terraform apply
```

Copy the `api_url` output.

## 3. Upload documents and sync

Upload files to the bucket's `documents/` prefix:

```bash
aws s3 cp ./sample-docs/company-policy.txt s3://YOUR_BUCKET_NAME/documents/company-policy.txt
```

Then open the Bedrock Knowledge Base in the AWS Console and run **Sync** on its data source. Wait until ingestion completes before asking questions.

## 4. Run the frontend

Edit `frontend/config.js` and set `API_URL` to the Terraform `api_url` output (include the `/ask` route if needed; the output already includes the base URL).

For a quick local static server:

```bash
cd frontend
python -m http.server 8080
```

Open http://localhost:8080.

## 5. Test the API directly

```bash
curl -X POST "YOUR_API_URL/ask" \
  -H "Content-Type: application/json" \
  -d '{"question":"Summarize the leave policy."}'
```

Expected response shape:

```json
{
  "answer": "The retrieved answer...",
  "citations": [
    {
      "text": "Relevant retrieved passage",
      "sources": ["s3://bucket/documents/company-policy.txt"]
    }
  ]
}
```

## Project structure

```text
serverless-rag-application/
├── backend/
│   ├── lambda_function.py
│   └── requirements.txt
├── frontend/
│   ├── index.html
│   ├── style.css
│   ├── app.js
│   └── config.js
├── sample-docs/
│   └── company-policy.txt
└── terraform/
    ├── main.tf
    ├── variables.tf
    ├── outputs.tf
    ├── terraform.tfvars.example
    └── lambda-trust-policy.json
```

## Security and production notes

- Do not commit AWS access keys, credentials, or real confidential documents.
- Replace wildcard CORS with your actual frontend domain.
- Add authentication (for example Amazon Cognito) before exposing this API publicly.
- Restrict IAM permissions further for your environment and use encryption/access logging as required.
- Add request validation, throttling, alarms, and budget alerts before production.
- Bedrock model availability, model IDs/ARNs, and permissions vary by region/account.
- This starter does not create the Bedrock Knowledge Base/vector store because those resources require model, vector-store, and service-role choices that depend on your account and region.

## Cleanup

```bash
cd terraform
terraform destroy
```

Empty the S3 bucket first if it contains uploaded documents; S3 bucket deletion will fail while objects remain.
