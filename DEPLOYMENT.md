# Deployment Information

## Public URL
https://thach97s-agent-production.up.railway.app/

## Platform
Railway

## Test Commands
curl -X POST https://thach97s-agent-production.up.railway.app/ask \
  -H "X-Api-Key: 123456" \
  -H "Content-Type: application/json" \
  -d '{"question": "Bay từ Hà Nội đến Đà Nẵng?", "conversation_id": "s1"}'

curl -X POST https://thach97s-agent-production.up.railway.app/ask \
  -H "X-Api-Key: 123456" \
  -H "Content-Type: application/json" \
  -d '{"question": "Còn khách sạn ở đó thì sao?", "conversation_id": "s1"}'

##  Pre-Submission Checklist

- [v] Repository is public (or instructor has access)
- [v] `MISSION_ANSWERS.md` completed with all exercises
- [v] `DEPLOYMENT.md` has working public URL
- [v] All source code in `app/` directory
- [v] `README.md` has clear setup instructions
- [v] No `.env` file committed (only `.env.example`)
- [v] No hardcoded secrets in code
- [v] Public URL is accessible and working
- [v] Screenshots included in `screenshots/` folder
- [v] Repository has clear commit history

---

##  Self-Test

Before submitting, verify your deployment:

```bash
# 1. Health check
curl https://thach97s-agent-production.up.railway.app/health
`{"status":"ok","timestamp":"2026-04-17T16:36:11.896696+00:00"}`
curl https://thach97s-agent-production.up.railway.app/ready
`{"status":"ready","redis":"ok"}`

# 2. Authentication required
curl -X POST https://thach97s-agent-production.up.railway.app/ask
`{"detail":[{"type":"missing","loc":["header","x-api-key"],"msg":"Field required","input":null},{"type":"missing","loc":["header","x-api-key"],"msg":"Field required","input":null},{"type":"missing","loc":["header","x-api-key"],"msg":"Field required","input":null},{"type":"missing","loc":["body"],"msg":"Field required","input":null}]}`

# 3. With API key works
curl -X POST https://thach97s-agent-production.up.railway.app/ask \
  -H "X-Api-Key: 123456" \         
  -H "Content-Type: application/json" \
  -d '{"question": "Bay từ Hà Nội đến Đà Nẵng?"}'

`{"answer":"Dưới đây là một số chuyến bay từ Hà Nội đến Đà Nẵng mà bạn có thể chọn:\n\n1. **Vietnam Airlines**\n   - Giờ khởi hành: 06:00\n   - Giờ đến: 07:20\n   - Giá: 1.450.000đ (hạng economy)\n\n2. **Vietnam Airlines**\n   - Giờ khởi hành: 14:00\n   - Giờ đến: 15:20\n   - Giá: 2.800.000đ (hạng business)\n\n3. **VietJet Air**\n   - Giờ khởi hành: 08:30\n   - Giờ đến: 09:50\n   - Giá: 890.000đ (hạng economy)\n\n4. **Bamboo Airways**\n   - Giờ khởi hành: 11:00\n   - Giờ đến: 12:20\n   - Giá: 1.200.000đ (hạng economy)\n\nNếu bạn cần hỗ trợ thêm về việc đặt vé hoặc chương trình du lịch tại Đà Nẵng, cứ cho mình biết nhé!","conversation_id":"default","cost_usd":0.000272}`

# 4. Rate limiting
for i in $(seq 1 11); do
  echo "Request $i:"
  curl -s -o /dev/null -w "%{http_code}" -X POST https://thach97s-agent-production.up.railway.app/ask \
    -H "X-Api-Key: 123456" \
    -H "Content-Type: application/json" \
    -d '{"question": "test"}'
  echo
done
`Request 1:
200
Request 2:
200
Request 3:
200
Request 4:
200
Request 5:
200
Request 6:
200
Request 7:
200
Request 8:
200
Request 9:
200
Request 10:
200
Request 11:
429`