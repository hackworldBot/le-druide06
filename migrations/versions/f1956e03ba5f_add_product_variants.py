"""add_product_variants"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "f1956e03ba5f"
down_revision: Union[str, Sequence[str], None] = "9094bd186ddb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    op.create_table(
        "product_variants",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("price", sa.Numeric(10, 2), nullable=False),
        sa.Column("stock", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["products.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_product_variants_product_id",
        "product_variants",
        ["product_id"],
        unique=False,
    )


def downgrade() -> None:

    op.drop_index(
        "ix_product_variants_product_id",
        table_name="product_variants",
    )

    op.drop_table("product_variants")
