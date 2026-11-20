import json
import os
import base64
import boto3
from botocore.exceptions import ClientError

bedrock_agent = boto3.client("bedrock-agent-runtime")
KNOWLEDGE_BASE_ID = os.environ["KNOWLEDGE_BASE_ID"]
MODEL_ARN = os.environ["MODEL_ARN"]


def response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": os.environ.get("ALLOWED_ORIGIN", "*"),
            "Access-Control-Allow-Headers": "content-type",
            "Access-Control-Allow-Methods": "OPTIONS,POST",
        },
        "body": json.dumps(body),
    }


def lambda_handler(event, context):
    if event.get("requestContext", {}).get("http", {}).get("method") == "OPTIONS":
        return response(200, {"ok": True})

    try:
        raw_body = event.get("body") or "{}"
        if event.get("isBase64Encoded"):
            raw_body = base64.b64decode(raw_body).decode("utf-8")
        payload = json.loads(raw_body)
        question = (payload.get("question") or "").strip()

        if not question:
            return response(400, {"error": "Please provide a non-empty 'question'."})
        if len(question) > 4000:
            return response(400, {"error": "Question is too long (maximum 4000 characters)."})

        result = bedrock_agent.retrieve_and_generate(
            input={"text": question},
            retrieveAndGenerateConfiguration={
                "type": "KNOWLEDGE_BASE",
                "knowledgeBaseConfiguration": {
                    "knowledgeBaseId": KNOWLEDGE_BASE_ID,
                    "modelArn": MODEL_ARN,
                },
            },
        )

        citations = []
        for citation in result.get("citations", []):
            references = []
            for reference in citation.get("retrievedReferences", []):
                location = reference.get("location", {})
                s3_location = location.get("s3Location", {}).get("uri")
                references.append({
                    "text": reference.get("content", {}).get("text", ""),
                    "source": s3_location or location,
                })
            citations.append({
                "text": citation.get("generatedResponsePart", {})
                    .get("textResponsePart", {}).get("text", ""),
                "sources": references,
            })

        answer = result.get("output", {}).get("text", "No answer was returned.")
        return response(200, {"answer": answer, "citations": citations})

    except json.JSONDecodeError:
        return response(400, {"error": "Request body must be valid JSON."})
    except ClientError as exc:
        print("AWS service error:", str(exc))
        return response(502, {"error": "The AI service request failed. Check Lambda logs and Bedrock configuration."})
    except Exception as exc:
        print("Unexpected error:", str(exc))
        return response(500, {"error": "Internal server error."})
