# 🚀 Railway 배포 가이드

## Railway 장점
- ✅ **항상 실행** (슬립 모드 없음, 핑 불필요!)
- ✅ **AI 라이브러리 지원** (PyTorch, Transformers)
- ✅ **빠른 응답 속도**
- ✅ **자동 배포** (git push만!)

---

## 📦 배포 단계

### 1️⃣ GitHub에 푸시

```bash
git add .
git commit -m "feat: Railway 배포 준비"
git push origin main
```

### 2️⃣ Railway 프로젝트 생성

1. **Railway 접속**: https://railway.app
2. **GitHub 로그인**
3. **Start a New Project**
4. **Deploy from GitHub repo**
5. **heamon-server** 선택

### 3️⃣ 환경변수 설정

Railway 대시보드 → **Variables** 탭 → **RAW Editor** 클릭


**⚠️ JWT_SECRET 생성:**
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 4️⃣ 배포 완료! 🎉

Railway가 자동으로 빌드 & 배포합니다.

**배포 URL**: `https://your-project.up.railway.app`

**API 문서**: `https://your-project.up.railway.app/docs`

---

## 🔧 배포 후 확인

### Health Check
```bash
curl https://your-project.up.railway.app/health
```

응답:
```json
{"status": "healthy"}
```

### API 문서
브라우저에서:
```
https://your-project.up.railway.app/docs
```

---

## 🔄 업데이트 배포

```bash
git add .
git commit -m "Update: ..."
git push origin main
```

Railway가 **자동으로 재배포**합니다!

---

## 💰 비용

**무료 크레딧**: $5/월

**예상 사용량**:
- 소규모: ~$3-5/월
- 중규모: ~$10-15/월

**팁**:
- Supabase 무료 티어 → DB 비용 0원
- Railway로 백엔드만 배포

---

## 🎯 완료 체크리스트

- [ ] GitHub에 푸시
- [ ] Railway 프로젝트 생성
- [ ] 환경변수 설정
- [ ] 배포 성공 확인
- [ ] API 문서 접속 확인
- [ ] Health check 테스트
- [ ] 프론트엔드에 URL 연결

---

## 🐛 트러블슈팅

### 빌드 실패
→ Railway 로그 확인, `requirements.txt` 체크

### DB 연결 실패
→ `DATABASE_URL` 환경변수 확인

### 서버 시작 실패
→ 로그 확인, `PORT` 환경변수는 자동 설정됨

### AI 모델 로딩 느림
→ 정상입니다! 첫 요청은 30초~1분 소요
