from sqlmodel import Session, select

from src.models.models import BlockedSite


class BlockedSiteRepository:
    def list_urls(self, db: Session, *, owner_id: int) -> list[str]:
        rows = db.exec(select(BlockedSite.url).where(BlockedSite.owner_id == owner_id)).all()
        return list(rows)

    def add(self, db: Session, *, owner_id: int, url: str) -> None:
        normalized = url.strip()
        if not normalized:
            return
        exists = db.exec(
            select(BlockedSite).where(
                BlockedSite.owner_id == owner_id,
                BlockedSite.url == normalized,
            )
        ).first()
        if exists:
            return
        db.add(BlockedSite(owner_id=owner_id, url=normalized))
        db.commit()

    def delete(self, db: Session, *, owner_id: int, url: str) -> None:
        row = db.exec(
            select(BlockedSite).where(
                BlockedSite.owner_id == owner_id,
                BlockedSite.url == url,
            )
        ).first()
        if row:
            db.delete(row)
            db.commit()


blocked_site_repo = BlockedSiteRepository()
