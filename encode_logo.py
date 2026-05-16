import base64

with open('assets/bob_logo.png', 'rb') as f:
    encoded = base64.b64encode(f.read()).decode()
    print(encoded)

# Made with Bob
