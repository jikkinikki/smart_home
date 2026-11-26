from sqlmodel import JSON, Column, Field, Relationship, SQLModel


class Room(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(unique=True)

    devices: list["Device"] = Relationship(back_populates="room")


class Device(SQLModel, table=True):
    # Same id as "dev_id" in devices.json (tuya id / zigbee ieee address)
    id: str = Field(primary_key=True)
    name: str
    type: str                       # "lamp", "bridge", ...
    source: str | None = None       # "tuya", "zigbee", ...

    address: str | None = None
    local_key: str | None = None    # tuya only - secret, keep the .db file out of git
    version: str | None = None

    disabled: bool = False
    hidden: bool = False            # still loaded, just not shown in device control

    # Source specific data, e.g. zigbee endpoint/capabilities. Set by the importers.
    extra: dict = Field(default_factory=dict, sa_column=Column(JSON, nullable=False))

    room_id: int | None = Field(default=None, foreign_key="room.id")
    room: Room | None = Relationship(back_populates="devices")
