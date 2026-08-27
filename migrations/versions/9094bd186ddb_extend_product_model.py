"""extend product model"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "9094bd186ddb"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    op.add_column(
        "products",
        sa.Column("sku", sa.String(length=100), nullable=True),
    )

    op.add_column(
        "products",
        sa.Column(
            "product_type",
            sa.String(length=50),
            nullable=False,
            server_default="physical",
        ),
    )

    op.add_column(
        "products",
        sa.Column(
            "sold_count",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
    )

    op.add_column(
        "products",
        sa.Column(
            "download_link",
            sa.Text(),
            nullable=True,
        ),
    )

    op.add_column(
        "products",
        sa.Column(
            "created_by",
            sa.Integer(),
            nullable=True,
        ),
    )

    op.add_column(
        "products",
        sa.Column(
            "updated_by",
            sa.Integer(),
            nullable=True,
        ),
    )

    op.create_unique_constraint(
        "uq_products_sku",
        "products",
        ["sku"],
    )


def downgrade() -> None:

    op.drop_constraint(
        "uq_products_sku",
        "products",
        type_="unique",
    )

    op.drop_column("products", "updated_by")
    op.drop_column("products", "created_by")
    op.drop_column("products", "download_link")
    op.drop_column("products", "sold_count")
    op.drop_column("products", "product_type")
    op.drop_column("products", "sku")
