variable "aws_region" {
  description = "AWS region where the application resources will be created."
  type        = string
  default     = "ap-south-1"
}

variable "project_name" {
  description = "Prefix used to name project resources."
  type        = string
  default     = "serverless-rag"
}

variable "knowledge_base_id" {
  description = "Existing Amazon Bedrock Knowledge Base ID."
  type        = string
}

variable "model_arn" {
  description = "Foundation model ARN used by RetrieveAndGenerate."
  type        = string
}

variable "allowed_origin" {
  description = "Allowed browser origin. Restrict this to your frontend domain for production."
  type        = string
  default     = "*"
}
