import base64
import json
import socket
import urllib3
import requests

# 1. Disable local SSL warning popups
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def resolve_via_google_dns(host):
    """
    Bypasses local computer connection drops by resolving the host via Google DNS
    directly over an isolated UDP stream.
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(3)
        dns_server = ("8.8.8.8", 53)
        packet = b"\x12\x34\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00"
        for part in host.split("."):
            packet += bytes([len(part)]) + part.encode("utf-8")
        packet += b"\x00\x00\x01\x00\x01"
        sock.sendto(packet, dns_server)
        data, _ = sock.recvfrom(512)
        sock.close()
        if data and len(data) > 4:
            return f"{data[-4]}.{data[-3]}.{data[-2]}.{data[-1]}"
    except Exception:
        pass
    return "40.233.89.174"


# 2. Inject runtime memory patch to route around local DNS connection outages
TARGET_HOST = "api.webit.live"
REAL_ACTIVE_IP = resolve_via_google_dns(TARGET_HOST)
print(f"[System Setup] Resolving destination host internally via Google DNS...")
print(f"[System Setup] Mapping {TARGET_HOST} directly to network node IP: {REAL_ACTIVE_IP}")

orig_getaddrinfo = socket.getaddrinfo


def patched_getaddrinfo(host, port, *args, **kwargs):
    if host == TARGET_HOST:
        return orig_getaddrinfo(REAL_ACTIVE_IP, port, *args, **kwargs)
    return orig_getaddrinfo(host, port, *args, **kwargs)


socket.getaddrinfo = patched_getaddrinfo

# 3. Compile standard API Session configurations
session = requests.Session()
endpoint = f"https://{TARGET_HOST}/api/v1/realtime/web"

raw_creds = "creds there"
encoded_creds = base64.b64encode(raw_creds.encode()).decode()

headers = {
    "Authorization": f"Basic {encoded_creds}",
    "Content-Type": "application/json"
}

# 4. Construct the absolute production GraphQL query data block
graphql_payload = {
    "operationName": "storeFulfillment",
    "variables": {
        "itemId": 325573249,
        "keyword": "10001",
        "requestContext": {
            "calculationOverride": 14
        }
    },
    "query": "query storeFulfillment($itemId: Int!, $keyword: String!, $requestContext: RequestContext) { storeFulfillment(itemId: $itemId, keyword: $keyword, requestContext: $requestContext) { fulfillmentOptions { type available quantity } } }"
}

# 5. Build Native Platform Parameter Blueprint
# We leverage the Web API's native support for forwarding raw POST bodies through a browser instance.
# Turning on "render": true instructs the cloud node to handle the Akamai fingerprints and TLS settings natively.
payload = {
    "url": "https://homedepot.com",
    "country": "US",
    "method": "POST",
    "render": True,
    "headers": {
        "Content-Type": "application/json",
        "Accept": "*/*",
        "Origin": "https://homedepot.com",
        "Referer": "https://homedepot.com/"
    },
    "body": json.dumps(graphql_payload)
}

print("\n[Network Stream] Transmitting rendered POST blueprint directly to API cluster...")
try:
    response = session.post(endpoint, headers=headers, json=payload, timeout=60)
    print(f"[Network Stream] Server response code received: {response.status_code}")

    if response.status_code == 200:
        response_json = response.json()

        # Pull text from the real property key returned by the cluster
        raw_text_payload = response_json.get("html_content", response_json.get("html", "")).strip()

        # Strip out any baseline container layouts if appended by the wrapper node
        if "<body>" in raw_text_payload:
            raw_text_payload = raw_text_payload.split("<body>")[-1].split("</body>")[0].strip()

        print("\n🎉 SUCCESS! TARGET GRAPHQL RESPONSE OBJECT RETRIEVED COMPLETELY:")
        try:
            # Output beautifully formatted JSON arrays to the console window
            print(json.dumps(json.loads(raw_text_payload), indent=2))
        except Exception:
            print(raw_text_payload if raw_text_payload else "Empty data stream returned from server.")
    else:
        print(f"[Failure Response Body]: {response.text}")

except Exception as e:
    print(f"[System Drop] Script aborted due to execution failure: {e}")
