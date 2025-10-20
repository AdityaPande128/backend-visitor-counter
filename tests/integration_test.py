import os
import boto3
import json
import time

# Get the function name from the environment variable set in the GitHub workflow
function_name = os.environ.get('LAMBDA_FUNCTION_NAME')
if not function_name:
    raise ValueError("LAMBDA_FUNCTION_NAME environment variable not set.")

lambda_client = boto3.client('lambda')

print(f"--- Running integration test on Lambda function: {function_name} ---")

try:
    # --- First invocation ---
    print("Invoking function for the first time...")
    response1 = lambda_client.invoke(
        FunctionName=function_name,
        InvocationType='RequestResponse' # Synchronous invocation
    )

    # The response payload is a streaming body, so you need to read and parse it
    payload1 = json.loads(response1['Payload'].read().decode('utf-8'))
    body1 = json.loads(payload1['body'])
    count1 = body1['count']
    print(f"Received count: {count1}")
    assert isinstance(count1, int), f"Count should be an integer, but got {type(count1)}"

    # Add a small delay to ensure the next invocation is a distinct event
    time.sleep(2)

    # --- Second invocation ---
    print("\nInvoking function for the second time...")
    response2 = lambda_client.invoke(
        FunctionName=function_name,
        InvocationType='RequestResponse'
    )

    payload2 = json.loads(response2['Payload'].read().decode('utf-8'))
    body2 = json.loads(payload2['body'])
    count2 = body2['count']
    print(f"Received count: {count2}")
    
    # --- Assertions ---
    print("\n--- Verifying results ---")
    assert count2 == count1 + 1, f"Expected count to be {count1 + 1}, but got {count2}"
    print(f"✅ Success: Counter incremented correctly from {count1} to {count2}.")

except Exception as e:
    print(f"❌ Test failed: {e}")
    exit(1) # Exit with a non-zero code to fail the workflow
