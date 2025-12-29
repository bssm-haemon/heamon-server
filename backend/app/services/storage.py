"""Supabase Storage 연동"""
import uuid
from datetime import datetime
import httpx
from fastapi import HTTPException, status
from app.config import settings


class StorageService:
    def __init__(self):
        self.supabase_url = settings.SUPABASE_URL
        self.supabase_key = settings.SUPABASE_SERVICE_KEY
        self.bucket_name = "images"

    def _get_headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.supabase_key}",
            "apikey": self.supabase_key,
        }

    async def upload_image(
        self,
        image_bytes: bytes,
        folder: str = "sightings",
        content_type: str = "image/jpeg"
    ) -> str:
        """
        이미지를 Supabase Storage에 업로드
        Returns: 공개 URL
        """
        # 개발 모드에서는 실제 업로드를 생략하고 더미 URL 반환
        if settings.DEBUG:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"{folder}/{timestamp}_{uuid.uuid4().hex[:8]}.jpg"
            return f"{self.supabase_url}/storage/v1/object/public/{self.bucket_name}/{filename}"

        # 고유 파일명 생성
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"{folder}/{timestamp}_{uuid.uuid4().hex[:8]}.jpg"

        url = f"{self.supabase_url}/storage/v1/object/{self.bucket_name}/{filename}"

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    url,
                    headers={
                        **self._get_headers(),
                        "Content-Type": content_type,
                    },
                    content=image_bytes,
                    timeout=10.0,
                )
            except httpx.TimeoutException:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="이미지 업로드 타임아웃"
                )

            if response.status_code in [200, 201]:
                # 공개 URL 반환
                public_url = f"{self.supabase_url}/storage/v1/object/public/{self.bucket_name}/{filename}"
                return public_url
            else:
                raise Exception(f"Upload failed: {response.text}")

    async def delete_image(self, file_path: str) -> bool:
        """이미지 삭제"""
        url = f"{self.supabase_url}/storage/v1/object/{self.bucket_name}/{file_path}"

        async with httpx.AsyncClient() as client:
            response = await client.delete(
                url,
                headers=self._get_headers()
            )
            return response.status_code == 200

    def get_public_url(self, file_path: str) -> str:
        """파일의 공개 URL 반환"""
        return f"{self.supabase_url}/storage/v1/object/public/{self.bucket_name}/{file_path}"


# 싱글톤 인스턴스
storage_service = StorageService()
