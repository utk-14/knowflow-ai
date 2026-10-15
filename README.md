python -c "
from app.db import supabase_public
res = supabase_public.auth.sign_in_with_password({
    'email': 'test@example.com',
    'password': 'test123456'
})
print('TOKEN:', res.session.access_token)
print('USER_ID:', res.user.id)
"


# Send a message
curl -X POST http://localhost:8000/chats/fcf32961-0d6d-4eee-a42c-67ec5d531369/messages \
  -H "Authorization: Bearer eyJhbGciOiJFUzI1NiIsImtpZCI6IjUzY2UxYjExLWM5MjAtNGM5Mi1iM2YwLTlkNGMxN2RmMzYwYyIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJodHRwczovL3hpaGZ1b29lZXhqY3Bnd2VrY2llLnN1cGFiYXNlLmNvL2F1dGgvdjEiLCJzdWIiOiJmMGIxM2ZjZC0yZWIyLTQ1M2MtYTI1Ni0yMTdmMWIxMzU0Y2EiLCJhdWQiOiJhdXRoZW50aWNhdGVkIiwiZXhwIjoxNzkyMDY5OTg1LCJpYXQiOjE3OTIwNjYzODUsImVtYWlsIjoidGVzdEBleGFtcGxlLmNvbSIsInBob25lIjoiIiwiYXBwX21ldGFkYXRhIjp7InByb3ZpZGVyIjoiZW1haWwiLCJwcm92aWRlcnMiOlsiZW1haWwiXX0sInVzZXJfbWV0YWRhdGEiOnsiZW1haWxfdmVyaWZpZWQiOnRydWV9LCJyb2xlIjoiYXV0aGVudGljYXRlZCIsImFhbCI6ImFhbDEiLCJhbXIiOlt7Im1ldGhvZCI6InBhc3N3b3JkIiwidGltZXN0YW1wIjoxNzkyMDY2Mzg1fV0sInNlc3Npb25faWQiOiIxNmZjNzRhMC0xMDhmLTQ5Y2UtYTQ4NC0yZjk3ZGUzNzdhNTMiLCJpc19hbm9ueW1vdXMiOmZhbHNlfQ.rSG9a2Jwmtq5fdnBDml62ND4dPkKuI-B38Oy36YJ6Q9VNLW8xLMqN2kUkuIja2ck80v98NI2gvTHINPwIGAB8w" \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the weather in Mumbai today?"}'