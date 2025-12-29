"""API 기본 테스트"""


def test_root(client):
    """루트 엔드포인트 테스트"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "해몬도감 API"


def test_health_check(client):
    """헬스체크 테스트"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_creatures_list(client):
    """생물 도감 목록 테스트"""
    response = client.get("/api/creatures")
    assert response.status_code == 200
    assert "creatures" in response.json()
    assert "total" in response.json()


def test_badges_list(client):
    """뱃지 목록 테스트"""
    response = client.get("/api/badges")
    assert response.status_code == 200
    assert "badges" in response.json()
