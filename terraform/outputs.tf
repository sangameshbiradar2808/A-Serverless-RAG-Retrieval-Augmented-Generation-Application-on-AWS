output "api_url" {
  description = "Base URL for the HTTP API. Append /ask for the question endpoint."
  value       = aws_apigatewayv2_api.http.api_endpoint
}

output "documents_bucket_name" {
  description = "S3 bucket name for document storage."
  value       = aws_s3_bucket.documents.bucket
}

output "lambda_function_name" {
  value = aws_lambda_function.ask.function_name
}
