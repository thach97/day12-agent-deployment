# Day 12 Lab - Mission Answers

**Student Name:** Hoàng Ngọc Thạch
**Student ID:** 2A202600068
**Date:** 17/04/2026

## Part 1: Localhost vs Production

### Exercise 1.1: Anti-patterns found
1. API key hardcode trong code. Nếu push lên GitHub → key bị lộ ngay lập tức
2. Không có config management
3. Print thay vì proper logging
4. Không có health check endpoint. Nếu agent crash, platform không biết để restart
5. Port cố định — không đọc từ environment. Trên Railway/Render, PORT được inject qua env var

### Exercise 1.3: Comparison table

| | Basic | Advanced | Tại sao quan trọng |
|-|-------|----------|--------------------|
| Config | Hardcode trong code | Đọc từ env vars | Thay đổi config không cần sửa code, tránh lộ thông tin khi push GitHub |
| Secrets | `api_key = "sk-abc123"` | `os.getenv("OPENAI_API_KEY")` | Key hardcode có thể bị lộ qua git history, bị dùng trái phép gây tốn tiền |
| Port | Cố định `8000` | Từ `PORT` env var | Railway/Render inject PORT động, cố định port sẽ không deploy được |
| Health check | Không có | `GET /health` | Platform cần endpoint này để biết app còn sống, tự động restart khi crash |
| Shutdown | Tắt đột ngột | Graceful — hoàn thành request hiện tại | Tắt đột ngột làm mất request đang xử lý, user nhận lỗi |
| Logging | `print()` | Structured JSON logging | JSON log dễ query, filter, alert trên các hệ thống monitoring như Datadog |

## Part 2: Docker

### Exercise 2.1: Dockerfile questions
1. Base image: python:3.11
2. Working directory: /app
3. Copy requirements.txt trước vì để cài pip ở câu lệnh sau thì cần file requirements.txt tồn tại trước.
4. 
| | CMD |ENTRYPOINT|
|-|----|----------|
| Vai trò |	Lệnh mặc định | Lệnh cố định (executable) |
| Override được không? | Có — ghi đè khi docker run image <lệnh_khác> | Không — luôn chạy, chỉ thêm argument |

### Exercise 2.2:
- Develop: 1.16 GB

### Exercise 2.3:
- Production: 186 MB
- Stage 1 - Builder: Dùng python:3.11-slim + cài thêm gcc, libpq-dev để compile các package cần build tool. Cài dependencies vào /root/.local bằng --user.
- Stage 2 - Runtime: Bắt đầu lại từ python:3.11-slim, chỉ COPY 2 thứ từ Stage 1 -> image nhỏ.

### Exercise 2.4:
- Các services được start: agent, redis, qdrant, nginx
- Các services này communicate qua bridge internal

## Part 3: Cloud Deployment

### Exercise 3.1: Railway deployment
- URL: https://new-project-production-6d7d.up.railway.app/
- Screenshot: ./images/railway.png

### Exercise 3.2: Deploy Render
- URL: https://ai-agent-rvl9.onrender.com/
- Screenshot: ./images/render.png

## Part 4: API Security

### Exercise 4.1:
1. API key được check ở đâu?
Hàm verify_api_key() — được inject vào endpoint /ask qua Depends(verify_api_key). FastAPI tự động chạy dependency này trước khi vào logic endpoint.
2. Điều gì xảy ra nếu sai key?
Không có key → HTTP 401 Missing API key
Sai key → HTTP 403 Invalid API key
Request bị chặn ngay, không chạy tới /ask
3. Làm sao rotate key?
Thay đổi key trong env var, restart app

### Exercise 4.2:
- Screenshot: ./images/jwt.png

### Exercise 4.3:
1. Algorithm nào?
Sliding Window. Cách hoạt động: mỗi request lưu timestamp vào deque, khi check thì loại bỏ timestamp cũ hơn 60 giây, đếm còn lại so với limit.

2. Limit bao nhiêu req/min?

| Role | Limit |
|------|-------|
| user | 10 req/phút |
| admin | 100 req/phút |

3. JWT token chứa role, khi verify token trả về role → app chọn đúng limiter. Muốn user student có limit cao hơn thì phải đổi role thành admin lúc tạo token

- Screenshot: ./images/rate-limit.png

### Exercise 4.4: Cost guard implementation
- Kết nối Redis local
- Tạo key theo tháng — sang tháng mới key khác → budget tự reset
- Lấy tổng chi phí tháng này của user. Nếu cộng thêm request hiện tại vượt $10/tháng → từ chối
- Cộng thêm chi phí vào Redis. Set TTL 32 ngày để key tự xóa sau khi tháng qua

## Part 5: Scaling & Reliability

### Exercise 5.1-5.5: Implementation notes
