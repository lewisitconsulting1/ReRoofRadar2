import uuid
from datetime import datetime, timezone

from geoalchemy2 import Geometry
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, relationship

Base = DeclarativeBase()


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    company_name = Column(String(255))
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)

    campaigns = relationship("Campaign", back_populates="user")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email})>"


class Property(Base):
    __tablename__ = "properties"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    address = Column(String(512), nullable=False)
    city = Column(String(255), nullable=False)
    state = Column(String(2), nullable=False)
    zip_code = Column(String(10), nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    geom = Column(Geometry(geometry_type="POINT", srid=4326), nullable=True)
    owner_name = Column(String(255))
    owner_email = Column(String(255))
    owner_phone = Column(String(50))
    year_built = Column(Integer, nullable=True)
    last_known_roof_year = Column(Integer, nullable=True)
    property_value = Column(Numeric(12, 2), nullable=True)
    data_source = Column(String(100))
    last_hail_event_id = Column(UUID(as_uuid=True), ForeignKey("hail_events.id"), nullable=True)
    confidence_score = Column(Numeric(3, 2), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow)

    hail_events = relationship("PropertyHailEvent", back_populates="property")

    __table_args__ = (
        Index("ix_properties_zip_code", "zip_code"),
        Index("ix_properties_geom", "geom", postgresql_using="gist"),
    )

    def __repr__(self) -> str:
        return f"<Property(id={self.id}, address={self.address})>"


class HailEvent(Base):
    __tablename__ = "hail_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_date = Column(DateTime(timezone=True), nullable=False)
    severity = Column(Numeric(3, 1), nullable=False)
    source = Column(String(100), nullable=False)
    source_event_id = Column(String(255))
    affected_area = Column(Geometry(geometry_type="POLYGON", srid=4326), nullable=False)
    centroid = Column(Geometry(geometry_type="POINT", srid=4326), nullable=True)
    state = Column(String(2))
    county = Column(String(100))
    raw_payload = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)

    property_links = relationship("PropertyHailEvent", back_populates="hail_event")

    __table_args__ = (
        Index("ix_hail_events_event_date", "event_date"),
        Index("ix_hail_events_affected_area", "affected_area", postgresql_using="gist"),
    )

    def __repr__(self) -> str:
        return f"<HailEvent(id={self.id}, severity={self.severity})>"


class PropertyHailEvent(Base):
    __tablename__ = "property_hail_events"

    property_id = Column(UUID(as_uuid=True), ForeignKey("properties.id"), primary_key=True)
    hail_event_id = Column(UUID(as_uuid=True), ForeignKey("hail_events.id"), primary_key=True)
    distance_meters = Column(Float, nullable=True)

    property = relationship("Property", back_populates="hail_events")
    hail_event = relationship("HailEvent", back_populates="property_links")

    def __repr__(self) -> str:
        return f"<PropertyHailEvent(property_id={self.property_id}, hail_event_id={self.hail_event_id})>"


class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    search_params = Column(JSONB, nullable=True)
    hail_events_found = Column(Integer, default=0)
    properties_returned = Column(Integer, default=0)
    status = Column(
        Enum("pending", "running", "complete", "failed", name="campaign_status"),
        default="pending",
        nullable=False,
    )
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="campaigns")

    def __repr__(self) -> str:
        return f"<Campaign(id={self.id}, status={self.status})>"
