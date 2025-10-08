import hmac
import hashlib

webhook_secret = "my_super_secret"
payload = b'{"data":{"object":{"id":"abc123","date":1681373000,"subject":"Test Email","from":[{"email":"test@example.com","name":"John Doe"}]}}}'

signature = hmac.new(
    webhook_secret.encode("utf-8"),
    msg=payload,
    digestmod=hashlib.sha256
).hexdigest()

print(signature)