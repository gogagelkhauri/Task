from nimble_python import Nimble

# Initialize the official Nimble client to bypass local SSL/TLS handshake restrictions
client = Nimble(api_key="key there")

JCREW_URL = "https://www.jcrew.com/p/mens/categories/clothing/shirts/linen/baird-mcnutt-irish-linen-shirt/C8839"

print("Sending request via Nimble Python SDK...")

try:
    # Use the SDK's managed extraction pipeline
    response = client.extract.run(
        url=JCREW_URL,
        country="US",
        render=True
    )

    # Extract content safely from the response object
    raw_html = getattr(response, "html_content", None) or str(response)

    if raw_html:
        # Save directly into the current working directory
        with open("jcrew_pdp.html", "w", encoding="utf-8") as f:
            f.write(raw_html)
        print("=== SUCCESS ===")
        print(f"Saved raw HTML ({len(raw_html)} bytes) to 'jcrew_pdp.html'")
    else:
        print("=== WARNING: Content was empty ===")

except Exception as e:
    print("\n=== ERROR RESPONSE ===")
    print(e)