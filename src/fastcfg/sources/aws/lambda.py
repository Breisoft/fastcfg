import json
from typing import Optional, Dict, Any

from fastcfg.sources.aws.boto3_live_tracker import AWSLiveTracker, AWSConfig


class LambdaLiveTracker(AWSLiveTracker):
    """Concrete class implementing a live lambda tracker."""

    def __init__(
        self,
        function_name: str,
        payload: Optional[Dict[str, Any]] = None,
        aws_config: Optional[AWSConfig] = None,
        *args,
        **kwargs
    ):
        super().__init__("lambda", aws_config, *args, **kwargs)
        self._function_name = function_name
        self._payload = payload or {}

    def fetch_from_aws(self):
        """Invoke Lambda function and return the response."""
        # Prepare the payload
        payload_bytes = json.dumps(self._payload).encode('utf-8')
        
        # Invoke the Lambda function
        response = self.client.invoke(
            FunctionName=self._function_name,
            InvocationType='RequestResponse',  # Synchronous
            Payload=payload_bytes
        )
        
        # Read the response
        response_payload = response['Payload'].read().decode('utf-8')
        
        # Parse the response
        try:
            result = json.loads(response_payload)
            
            # If Lambda returned an error, raise it
            if 'errorMessage' in result:
                raise Exception(f"Lambda error: {result['errorMessage']}")
                
            # If the response has a body field (API Gateway pattern), extract it
            if isinstance(result, dict) and 'body' in result:
                body = result['body']
                # Try to parse body as JSON if it's a string
                if isinstance(body, str):
                    try:
                        return json.loads(body)
                    except json.JSONDecodeError:
                        return body
                return body
            
            return result
        except json.JSONDecodeError:
            # Return as string if not valid JSON
            return response_payload
