"""initial models: users, properties, hail_events, property_hail_events, campaigns

Revision ID: 0001_initial
Revises: 
Create Date: 2026-04-28 23:29:17.000000+00:00

"""
from alembic import op
import sqlalchemy as sa
from geoalchemy2 import Geometry

revision = '0001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute('CREATE EXTENSION IF NOT EXISTS postgis')

    op.execute("CREATE TYPE campaign_status AS ENUM ('pending', 'running', 'complete', 'failed')")

    op.create_table(
        'users',
        sa.Column('id', sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('email', sa.String(255), unique=True, nullable=False),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(255), nullable=False),
        sa.Column('company_name', sa.String(255)),
        sa.Column('is_active', sa.Boolean, nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )
    op.create_index('ix_users_email', 'users', ['email'])

    op.create_table(
        'hail_events',
        sa.Column('id', sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('event_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('severity', sa.Numeric(3, 1), nullable=False),
        sa.Column('source', sa.String(100), nullable=False),
        sa.Column('source_event_id', sa.String(255)),
        sa.Column('affected_area', Geometry(geometry_type='POLYGON', srid=4326), nullable=False),
        sa.Column('centroid', Geometry(geometry_type='POINT', srid=4326)),
        sa.Column('state', sa.String(2)),
        sa.Column('county', sa.String(100)),
        sa.Column('raw_payload', sa.dialects.postgresql.JSONB(astext_type=sa.Text())),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )
    op.create_index('ix_hail_events_event_date', 'hail_events', ['event_date'])
    op.create_index('ix_hail_events_affected_area', 'hail_events', ['affected_area'], postgresql_using='gist')

    op.create_table(
        'properties',
        sa.Column('id', sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('address', sa.String(512), nullable=False),
        sa.Column('city', sa.String(255), nullable=False),
        sa.Column('state', sa.String(2), nullable=False),
        sa.Column('zip_code', sa.String(10), nullable=False),
        sa.Column('latitude', sa.Float),
        sa.Column('longitude', sa.Float),
        sa.Column('geom', Geometry(geometry_type='POINT', srid=4326)),
        sa.Column('owner_name', sa.String(255)),
        sa.Column('owner_email', sa.String(255)),
        sa.Column('owner_phone', sa.String(50)),
        sa.Column('year_built', sa.Integer),
        sa.Column('last_known_roof_year', sa.Integer),
        sa.Column('property_value', sa.Numeric(12, 2)),
        sa.Column('data_source', sa.String(100)),
        sa.Column('last_hail_event_id', sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey('hail_events.id')),
        sa.Column('confidence_score', sa.Numeric(3, 2)),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )
    op.create_index('ix_properties_zip_code', 'properties', ['zip_code'])
    op.create_index('ix_properties_geom', 'properties', ['geom'], postgresql_using='gist')

    op.create_table(
        'property_hail_events',
        sa.Column('property_id', sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey('properties.id'), primary_key=True),
        sa.Column('hail_event_id', sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey('hail_events.id'), primary_key=True),
        sa.Column('distance_meters', sa.Float),
    )

    op.create_table(
        'campaigns',
        sa.Column('id', sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('search_params', sa.dialects.postgresql.JSONB(astext_type=sa.Text())),
        sa.Column('hail_events_found', sa.Integer, server_default=sa.text('0')),
        sa.Column('properties_returned', sa.Integer, server_default=sa.text('0')),
        sa.Column('status', sa.Enum('pending', 'running', 'complete', 'failed', name='campaign_status'), nullable=False, server_default='pending'),
        sa.Column('error_message', sa.Text),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('completed_at', sa.DateTime(timezone=True)),
    )


def downgrade() -> None:
    op.drop_table('campaigns')
    op.drop_table('property_hail_events')
    op.drop_table('properties')
    op.drop_table('hail_events')
    op.drop_table('users')
    op.execute('DROP TYPE campaign_status')
    op.execute('DROP EXTENSION IF EXISTS postgis')
