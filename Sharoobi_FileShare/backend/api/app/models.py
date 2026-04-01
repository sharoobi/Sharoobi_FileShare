from datetime import UTC, datetime

from sqlalchemy import JSON, Boolean, Column, DateTime, ForeignKey, Integer, String, Table, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("role_id", ForeignKey("roles.id"), primary_key=True),
)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(128), default="")
    password_hash: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(tz=UTC))
    roles: Mapped[list["Role"]] = relationship(
        secondary=user_roles,
        back_populates="users",
        lazy="selectin",
    )


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(128))
    description: Mapped[str] = mapped_column(Text, default="")
    permissions: Mapped[list[str]] = mapped_column(JSON, default=list)
    users: Mapped[list[User]] = relationship(
        secondary=user_roles,
        back_populates="roles",
        lazy="selectin",
    )


class AccessPolicy(Base):
    __tablename__ = "access_policies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(128))
    description: Mapped[str] = mapped_column(Text, default="")
    read_limit_mbps: Mapped[int] = mapped_column(Integer, default=0)
    install_only: Mapped[bool] = mapped_column(Boolean, default=False)
    allow_download: Mapped[bool] = mapped_column(Boolean, default=True)
    allow_browse: Mapped[bool] = mapped_column(Boolean, default=True)
    allow_smb: Mapped[bool] = mapped_column(Boolean, default=True)
    allow_web: Mapped[bool] = mapped_column(Boolean, default=True)
    allow_guest: Mapped[bool] = mapped_column(Boolean, default=False)
    concurrent_sessions: Mapped[int] = mapped_column(Integer, default=4)
    shares: Mapped[list["Share"]] = relationship(back_populates="policy")


class Share(Base):
    __tablename__ = "shares"
    __table_args__ = (UniqueConstraint("slug", name="uq_shares_slug"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(128))
    source_path: Mapped[str] = mapped_column(String(512))
    access_mode: Mapped[str] = mapped_column(String(64), default="browse-download")
    publish_strategy: Mapped[str] = mapped_column(String(64), default="hybrid")
    smb_share_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    allow_guest: Mapped[bool] = mapped_column(Boolean, default=False)
    expose_via_smb: Mapped[bool] = mapped_column(Boolean, default=True)
    expose_via_web: Mapped[bool] = mapped_column(Boolean, default=True)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    notes: Mapped[str] = mapped_column(Text, default="")
    last_bridge_status: Mapped[str | None] = mapped_column(String(64), nullable=True)
    last_bridge_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    last_bridge_node: Mapped[str | None] = mapped_column(String(128), nullable=True)
    last_path_exists: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    last_path_kind: Mapped[str | None] = mapped_column(String(32), nullable=True)
    last_smb_published: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    last_smb_publish_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    file_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    size_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    last_scanned_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(tz=UTC))
    policy_id: Mapped[int | None] = mapped_column(ForeignKey("access_policies.id"), nullable=True)
    policy: Mapped[AccessPolicy | None] = relationship(back_populates="shares", lazy="joined")
    packages: Mapped[list["Package"]] = relationship(back_populates="share")
    jobs: Mapped[list["Job"]] = relationship(back_populates="share")


class Package(Base):
    __tablename__ = "packages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(128))
    version: Mapped[str] = mapped_column(String(64), default="")
    category: Mapped[str] = mapped_column(String(64), default="general")
    installer_type: Mapped[str] = mapped_column(String(64), default="folder")
    silent_supported: Mapped[bool] = mapped_column(Boolean, default=False)
    install_args: Mapped[str] = mapped_column(Text, default="")
    entry_path: Mapped[str] = mapped_column(String(512), default=".")
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    share_id: Mapped[int] = mapped_column(ForeignKey("shares.id"))
    share: Mapped[Share] = relationship(back_populates="packages", lazy="joined")


class Device(Base):
    __tablename__ = "devices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    hostname: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    ip_address: Mapped[str] = mapped_column(String(64), default="")
    mac_address: Mapped[str | None] = mapped_column(String(64), nullable=True)
    state: Mapped[str] = mapped_column(String(32), default="unknown")
    profile: Mapped[str] = mapped_column(String(64), default="guest")
    agent_version: Mapped[str | None] = mapped_column(String(64), nullable=True)
    device_type: Mapped[str] = mapped_column(String(32), default="client")
    notes: Mapped[str] = mapped_column(Text, default="")
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(128))
    job_type: Mapped[str] = mapped_column(String(64))
    state: Mapped[str] = mapped_column(String(32), default="draft")
    target_selector: Mapped[str] = mapped_column(String(128), default="manual")
    queued: Mapped[int] = mapped_column(Integer, default=0)
    succeeded: Mapped[int] = mapped_column(Integer, default=0)
    failed: Mapped[int] = mapped_column(Integer, default=0)
    last_message: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(tz=UTC))
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    share_id: Mapped[int | None] = mapped_column(ForeignKey("shares.id"), nullable=True)
    package_id: Mapped[int | None] = mapped_column(ForeignKey("packages.id"), nullable=True)
    share: Mapped[Share | None] = relationship(back_populates="jobs", lazy="joined")
    package: Mapped[Package | None] = relationship(lazy="joined")
