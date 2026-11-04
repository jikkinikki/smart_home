"""
Zigbee remote: the EZSP USB dongle joins the Innr bridge's network as a router (like a remote
would) and reads every device on it into a JSON file.

Needs: pip install bellows zigpy

    python zigbee_remote.py scan             # list nearby Zigbee networks (harmless)
    python zigbee_remote.py join             # leave the dongle's current network, join the bridge
    python zigbee_remote.py join --no-tclk   # retry without requesting a unique TC link key
    python zigbee_remote.py status           # which network the dongle is on
    python zigbee_remote.py devices          # read all devices on the bridge -> res/json/zigbee_devices.json

    Options: --port COM4 (default settings.ZIGBEE_PORT), --out <file> (devices only)

From code:

    async with ZigbeeRemote() as remote:
        data = await remote.read_devices()
"""

from __future__ import annotations

import argparse
import asyncio
import enum
import itertools
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import bellows.types as t
import zigpy.config as zconf
import zigpy.types as zt
import zigpy.zcl as zcl
import zigpy.zcl.foundation as zcl_f
import zigpy.zdo.types as zdo_t
from bellows.zigbee.application import ControllerApplication

import settings

DEFAULT_PORT = getattr(settings, "ZIGBEE_PORT", "COM4")
DEFAULT_BAUDRATE = getattr(settings, "ZIGBEE_BAUDRATE", 115200)
DEFAULT_DEVICES_FILE = Path(__file__).resolve().parents[1] / "json" / "zigbee_devices.json"

ALL_CHANNELS = list(range(11, 27))
HA_PROFILE = 0x0104
ONOFF_CLUSTER = 0x0006
LEVEL_CLUSTER = 0x0008
COLOR_CLUSTER = 0x0300
GROUPS_CLUSTER = 0x0004

PROFILE_NAMES = {0x0104: "Home Automation", 0xC05E: "Zigbee Light Link", 0xA1E0: "Green Power"}

# Attributes per Read Attributes request. Zigbee frames are small (~80 bytes), so a few
# string attributes can already fill one; attributes missing from a reply are re-read alone.
READ_CHUNK = 3


# ---------------------------------------------------------------------------
# Radio: a small request/response layer on top of raw EZSP
# ---------------------------------------------------------------------------

class Radio:
    """Send ZDO/ZCL requests through the dongle and await the matching reply."""

    def __init__(self, ezsp):
        self.ezsp = ezsp
        self._tsn = itertools.count(1)
        self._waiters: dict[tuple, asyncio.Future] = {}
        ezsp.add_callback(self._on_frame)

    def next_tsn(self) -> int:
        return next(self._tsn) % 256

    def _on_frame(self, frame_name, args):
        if frame_name != "incomingMessageHandler":
            return
        if self.ezsp.ezsp_version >= 14:
            _, aps, nwk, _, _, _, _, _, _, message = args
        else:
            _, aps, _, _, nwk, _, _, message = args
        if not message:
            return

        if aps.profileId == 0:  # ZDO
            key = ("zdo", nwk, aps.clusterId, message[0])
        else:
            try:
                hdr, _ = zcl_f.ZCLHeader.deserialize(message)
            except Exception:
                return
            key = ("zcl", nwk, aps.clusterId, hdr.tsn)

        # Exact sender match first; then "any sender" waiters (used for broadcast requests)
        fut = self._waiters.pop(key, None) or self._waiters.pop((key[0], None, *key[2:]), None)
        if fut and not fut.done():
            fut.set_result(message)

    async def _request(self, key, nwk, aps, data, timeout):
        fut = asyncio.get_running_loop().create_future()
        self._waiters[key] = fut
        try:
            status, _ = await self.ezsp.send_unicast(
                nwk=t.NWK(nwk), aps_frame=aps, message_tag=key[-1], data=data
            )
            if status != t.sl_Status.OK:
                raise RuntimeError(f"send failed: {status!r}")
            return await asyncio.wait_for(fut, timeout)
        finally:
            self._waiters.pop(key, None)

    async def get_ieee(self, nwk: int) -> str:
        """Ask a device for its permanent IEEE address."""
        status, ieee, *_ = await self.zdo(
            nwk, zdo_t.ZDOCmd.IEEE_addr_req, t.NWK(nwk), zdo_t.AddrRequestType.Single, 0
        )
        if status != zdo_t.Status.SUCCESS:
            raise RuntimeError(f"IEEE lookup failed: {status!r}")
        return str(ieee)

    async def zdo(self, nwk: int, cmd: zdo_t.ZDOCmd, *args, timeout=6):
        """Send a ZDO request and return the parsed response fields."""
        _, req_types = zdo_t.CLUSTERS[cmd]
        rsp_cmd = zdo_t.ZDOCmd(cmd | 0x8000)
        _, rsp_types = zdo_t.CLUSTERS[rsp_cmd]
        tsn = self.next_tsn()
        aps = make_aps(0x0000, cmd, src_ep=0, dst_ep=0, unicast=True)
        data = bytes([tsn]) + zt.serialize(args, req_types)
        message = await self._request(("zdo", nwk, rsp_cmd, tsn), nwk, aps, data, timeout)
        values, _ = zt.deserialize(message[1:], rsp_types)
        return values

    async def zcl_general(self, nwk, ep, cluster, command_id, payload=b"", timeout=6):
        """Send a general (profile-wide) ZCL command; returns (reply header, reply payload)."""
        tsn = self.next_tsn()
        data = zcl_f.ZCLHeader.general(tsn, command_id).serialize() + payload
        aps = make_aps(HA_PROFILE, cluster, src_ep=1, dst_ep=ep, unicast=True)
        message = await self._request(("zcl", nwk, cluster, tsn), nwk, aps, data, timeout)
        return zcl_f.ZCLHeader.deserialize(message)

    async def read_attribute_records(self, nwk, ep, cluster, attr_ids, timeout=6):
        """{attr_id: ReadAttributeRecord} for the records in the reply, or None if the
        device answered with something else (usually 'cluster not supported').

        A record zigpy can't decode (e.g. manufacturer-specific arrays) stops the parsing;
        when only one attribute was asked for, its raw reply bytes are returned instead."""
        payload = b"".join(zt.uint16_t(a).serialize() for a in attr_ids)
        hdr, rest = await self.zcl_general(
            nwk, ep, cluster, zcl_f.GeneralCommand.Read_Attributes, payload, timeout
        )
        if hdr.frame_control.is_cluster or hdr.command_id != zcl_f.GeneralCommand.Read_Attributes_rsp:
            return None
        records = {}
        while rest:
            try:
                record, rest = zcl_f.ReadAttributeRecord.deserialize(rest)
            except Exception:
                if len(attr_ids) == 1:
                    records[attr_ids[0]] = bytes(rest)
                break
            records[int(record.attrid)] = record
        return records

    async def discover_attributes(self, nwk, ep, cluster, timeout=6):
        """[(attr_id, data_type_id), ...] the device says it supports, or None if it
        doesn't support attribute discovery."""
        found, start = [], 0
        while True:
            payload = zt.uint16_t(start).serialize() + zt.uint8_t(16).serialize()
            hdr, rest = await self.zcl_general(
                nwk, ep, cluster, zcl_f.GeneralCommand.Discover_Attributes, payload, timeout
            )
            if hdr.frame_control.is_cluster or hdr.command_id != zcl_f.GeneralCommand.Discover_Attributes_rsp:
                return None if not found else found
            complete, rest = rest[0], rest[1:]
            batch = [
                (int.from_bytes(rest[i:i + 2], "little"), rest[i + 2])
                for i in range(0, len(rest) - 2, 3)
            ]
            found += batch
            if complete or not batch:
                return found
            start = batch[-1][0] + 1

    async def read_all_attributes(self, nwk, ep, cluster, attr_ids):
        """Read many attributes in small chunks. Returns {attr_id: ReadAttributeRecord}."""
        results = {}
        for i in range(0, len(attr_ids), READ_CHUNK):
            chunk = attr_ids[i:i + READ_CHUNK]
            records = await self.read_attribute_records(nwk, ep, cluster, chunk)
            if records is None:
                break  # cluster not readable at all
            results.update(records)
            # A reply that didn't fit in one frame drops attributes: read those one by one
            for attr_id in chunk:
                if attr_id not in results and len(chunk) > 1:
                    single = await self.read_attribute_records(nwk, ep, cluster, [attr_id])
                    if single:
                        results.update(single)
        return results

    async def cluster_command(self, nwk, ep, cluster, command_id, payload=b"", timeout=6):
        """Send a cluster-specific command and return (reply header, reply payload)."""
        tsn = self.next_tsn()
        data = bytes([0x01, tsn, command_id]) + payload  # cluster-specific, client->server
        aps = make_aps(HA_PROFILE, cluster, src_ep=1, dst_ep=ep, unicast=True)
        message = await self._request(("zcl", nwk, cluster, tsn), nwk, aps, data, timeout)
        return zcl_f.ZCLHeader.deserialize(message)


def make_aps(profile, cluster, src_ep, dst_ep, unicast):
    options = t.EmberApsOption.APS_OPTION_NONE
    if unicast:
        options = t.EmberApsOption.APS_OPTION_RETRY | t.EmberApsOption.APS_OPTION_ENABLE_ROUTE_DISCOVERY
    return t.EmberApsFrame(
        profileId=profile,
        clusterId=cluster,
        sourceEndpoint=src_ep,
        destinationEndpoint=dst_ep,
        options=options,
        groupId=0,
        sequence=0,
    )


# ---------------------------------------------------------------------------
# JSON helpers
# ---------------------------------------------------------------------------

def hex16(value) -> str:
    return f"0x{int(value):04X}"


def jsonable(value, enum_names=True):
    """Turn zigpy/bellows values into plain JSON values."""
    if value is None or isinstance(value, bool):
        return value
    if isinstance(value, enum.Flag):
        if not enum_names:
            return int(value)
        return [m.name for m in type(value) if m.value and (value & m) == m]
    if isinstance(value, enum.Enum):
        if enum_names or not isinstance(value.value, int):
            return value.name
        return int(value.value)
    if isinstance(value, (zt.EUI64, zt.ExtendedPanId)):
        return str(value)
    if isinstance(value, int):
        return int(value)
    if isinstance(value, float):
        return float(value)
    if isinstance(value, str):
        return str(value)
    if isinstance(value, (bytes, bytearray)):
        return bytes(value).hex()
    if isinstance(value, zt.Struct):
        return {k: jsonable(v, enum_names) for k, v in value.as_dict().items() if v is not None}
    if isinstance(value, dict):
        return {str(k): jsonable(v, enum_names) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [jsonable(v, enum_names) for v in value]
    return str(value)


def cluster_class(cluster_id):
    return zcl.Cluster._registry.get(cluster_id)


def cluster_name(cluster_id) -> str:
    name = getattr(cluster_class(cluster_id), "name", None)
    return name if isinstance(name, str) else hex16(cluster_id)


def device_type_name(profile, device_type):
    try:
        if profile == HA_PROFILE:
            from zigpy.profiles import zha
            return zha.DeviceType(device_type).name
        if profile == 0xC05E:
            from zigpy.profiles import zll
            return zll.DeviceType(device_type).name
    except ValueError:
        pass
    return None


def describe_attribute(cls, record):
    """(name, {id, type, value, meaning?}) for one successfully read attribute."""
    attr_id = int(record.attrid)
    attr_def = cls.attributes.get(attr_id) if cls else None
    value = record.value.value
    try:
        type_name = zcl_f.DataTypeId(record.value.type).name
    except ValueError:
        type_name = f"0x{int(record.value.type):02X}"

    entry = {"id": hex16(attr_id), "type": type_name, "value": jsonable(value, enum_names=False)}

    # Give enums/bitmaps a readable meaning using zigpy's definition of the attribute
    def_type = getattr(attr_def, "type", None)
    if isinstance(def_type, type) and issubclass(def_type, enum.Enum):
        try:
            entry["meaning"] = jsonable(def_type(int(value)))
        except (ValueError, TypeError):
            pass

    return (attr_def.name if attr_def else hex16(attr_id)), entry


def known_attribute_ids(cls) -> list[int]:
    """Standard (non-manufacturer) attribute ids zigpy knows for a cluster."""
    if cls is None:
        return []
    return sorted(
        attr_id for attr_id, attr_def in cls.attributes.items()
        if not attr_def.is_manufacturer_specific and attr_id < 0xFFF0
    )


# ---------------------------------------------------------------------------
# The remote
# ---------------------------------------------------------------------------

class ZigbeeRemote:
    """The USB dongle acting as a remote on the bridge's Zigbee network."""

    def __init__(self, port: str | None = None, baudrate: int | None = None, log=print):
        self.port = port or DEFAULT_PORT
        self.baudrate = baudrate or DEFAULT_BAUDRATE
        self.log = log
        self.app = None
        self.ezsp = None
        self.radio: Radio | None = None

    # ---------- connection ----------

    async def connect(self):
        """Connect to the dongle without starting zigpy's coordinator logic."""
        self.app = ControllerApplication({
            zconf.CONF_DEVICE: {
                zconf.CONF_DEVICE_PATH: self.port,
                zconf.CONF_DEVICE_BAUDRATE: self.baudrate,
                zconf.CONF_DEVICE_FLOW_CONTROL: zconf.CONF_DEVICE_FLOW_CONTROL_DEFAULT,
            }
        })
        await self.app.connect()  # also registers endpoint 1 on the radio
        self.ezsp = self.app._ezsp
        self.radio = Radio(self.ezsp)
        return self

    async def disconnect(self):
        if self.app is not None:
            await self.app.disconnect()
            self.app = self.ezsp = self.radio = None

    async def __aenter__(self):
        return await self.connect()

    async def __aexit__(self, *exc):
        await self.disconnect()

    # ---------- network ----------

    async def bring_up_stored_network(self) -> bool:
        """Resume whatever network is stored in the dongle. Returns True if it is up."""
        (state,) = await self.ezsp.networkState()
        if state == t.EmberNetworkStatus.JOINED_NETWORK:
            return True
        with self.ezsp.wait_for_stack_status(t.sl_Status.NETWORK_UP) as network_up:
            status = await self.ezsp.initialize_network()
            if status != t.sl_Status.OK:
                return False
            await asyncio.wait_for(network_up, 20)
        return True

    async def network_info(self) -> dict | None:
        """The network the dongle is on, or None if it isn't on one."""
        if not await self.bring_up_stored_network():
            return None
        _, node_type, params = await self.ezsp.getNetworkParameters()
        (nwk,) = await self.ezsp.getNodeId()
        (ieee,) = await self.ezsp.getEui64()
        return {
            "role": node_type.name,
            "pan_id": hex16(params.panId),
            "extended_pan_id": str(params.extendedPanId),
            "channel": int(params.radioChannel),
            "tx_power": int(params.radioTxPower),
            "nwk_update_id": int(params.nwkUpdateId),
            "our_nwk": hex16(nwk),
            "our_ieee": str(ieee),
            "port": self.port,
        }

    async def is_remote(self) -> bool:
        """True if the dongle is joined to someone else's network (not its own coordinator)."""
        info = await self.network_info()
        if info is None:
            self.log("Dongle isn't on any network. Run 'join' first.")
            return False
        if info["role"] == t.EmberNodeType.COORDINATOR.name:
            self.log("Dongle is still the coordinator of its own network. Run 'join' first.")
            return False
        return True

    async def _scan_raw(self):
        results = await self.ezsp.startScan(
            scanType=t.EzspNetworkScanType.ACTIVE_SCAN,
            channelMask=t.Channels.from_channel_list(ALL_CHANNELS),
            duration=3,
        )
        best = {}
        for network, lqi, rssi in results:
            key = (network.extendedPanId, network.panId)
            if key not in best or lqi > best[key][1]:
                best[key] = (network, lqi, rssi)
        return list(best.values())

    async def scan(self) -> list[dict]:
        """Nearby Zigbee networks (takes ~10 s)."""
        return [{
            "pan_id": hex16(network.panId),
            "extended_pan_id": str(network.extendedPanId),
            "channel": int(network.channel),
            "allowing_join": bool(network.allowingJoin),
            "stack_profile": int(network.stackProfile),
            "nwk_update_id": int(network.nwkUpdateId),
            "lqi": int(lqi),
            "rssi": int(rssi),
        } for network, lqi, rssi in await self._scan_raw()]

    async def join(self, request_tclk: bool = True, wait_for_bridge=None) -> bool:
        """
        Leave the dongle's current network and join the bridge as a router.

        wait_for_bridge: optional async callable, awaited right before scanning, so the user
        can put the bridge in 'add device' mode first. The open network with the best
        signal is joined.
        """
        ezsp = self.ezsp

        # 1. Drop whatever network the dongle is on
        if await self.bring_up_stored_network():
            self.log(f"Dongle is on a network, leaving it first: {await self.network_info()}")
            await ezsp.leaveNetwork()
            await asyncio.sleep(1)

        # 2. Security: only the well-known Zigbee 3.0 link key is known; the bridge hands
        #    over the network key during the join.
        sec = t.EmberInitialSecurityState()
        sec.bitmask = (
            t.EmberInitialSecurityBitmask.HAVE_PRECONFIGURED_KEY
            | t.EmberInitialSecurityBitmask.REQUIRE_ENCRYPTED_KEY
            | t.EmberInitialSecurityBitmask.TRUST_CENTER_GLOBAL_LINK_KEY
        )
        if request_tclk:
            sec.bitmask |= t.EmberInitialSecurityBitmask.GET_LINK_KEY_WHEN_JOINING
        sec.preconfiguredKey = t.KeyData(b"ZigBeeAlliance09")
        sec.networkKey = t.KeyData(bytes(16))
        sec.networkKeySequenceNumber = 0
        sec.preconfiguredTrustCenterEui64 = t.EUI64.convert("00:00:00:00:00:00:00:00")
        (status,) = await ezsp.setInitialSecurityState(sec)
        self.log(f"Set security state: {status!r}")

        # 3. Find the bridge while it's in pairing mode
        if wait_for_bridge is not None:
            await wait_for_bridge()
        self.log("Scanning channels 11-26 (takes ~10 s)...")
        open_networks = sorted(
            (entry for entry in await self._scan_raw() if entry[0].allowingJoin),
            key=lambda entry: entry[1], reverse=True,
        )
        if not open_networks:
            self.log("No network is open for joining. Put the bridge in 'add device' mode and retry.")
            return False
        network = open_networks[0][0]

        # 4. Join as a router (mains-powered, no polling needed)
        params = t.EmberNetworkParameters()
        params.extendedPanId = network.extendedPanId
        params.panId = network.panId
        params.radioTxPower = 8
        params.radioChannel = network.channel
        params.joinMethod = t.EmberJoinMethod.USE_MAC_ASSOCIATION
        params.nwkManagerId = t.EmberNodeId(0)
        params.nwkUpdateId = 0
        params.channels = t.Channels(0)

        final = asyncio.get_running_loop().create_future()

        def on_frame(frame_name, response):
            if frame_name != "stackStatusHandler":
                return
            self.log(f"  stack status: {response[0]!r}")
            status = t.sl_Status.from_ember_status(response[0])
            if not final.done() and status != t.sl_Status.OK:
                final.set_result(status)

        cb_id = ezsp.add_callback(on_frame)
        try:
            self.log(f"Joining PAN {hex16(network.panId)} on channel {network.channel} as ROUTER...")
            (status,) = await ezsp.joinNetwork(t.EmberNodeType.ROUTER, params)
            if t.sl_Status.from_ember_status(status) != t.sl_Status.OK:
                self.log(f"joinNetwork refused immediately: {status!r}")
                return False
            try:
                result = await asyncio.wait_for(final, 60)
            except asyncio.TimeoutError:
                self.log("No answer from the network within 60 s.")
                return False
        finally:
            ezsp.remove_callback(cb_id)

        if result != t.sl_Status.NETWORK_UP:
            self.log(f"Join failed: {result!r}")
            if request_tclk:
                self.log("Try again with: python zigbee_remote.py join --no-tclk")
            return False

        self.log(f"Joined: {await self.network_info()}")
        return True

    # ---------- devices ----------

    async def read_devices(self, path: str | Path | None = DEFAULT_DEVICES_FILE) -> dict | None:
        """
        Find every device on the bridge's network, ask each one everything it will tell us,
        and save it as JSON to `path` (pass None to skip saving). Returns the data.
        """
        if not await self.is_remote():
            return None

        network = await self.network_info()
        devices = await self._walk_network(int(network["our_nwk"], 16))
        self.log(f"Found {len(devices)} device(s). Reading each one...")

        for nwk, info in sorted(devices.items()):
            self.log(f"  {hex16(nwk)} {info.get('ieee') or ''}")
            await self._interview(nwk, info)

        data = {
            "read_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "network": network,
            "devices": [devices[nwk] for nwk in sorted(devices)],
        }
        if path is not None:
            save_json(data, path)
            self.log(f"Saved {len(devices)} device(s) to {path}")
        return data

    async def _walk_network(self, own_nwk: int) -> dict[int, dict]:
        """Walk the neighbour tables, starting at the bridge (0x0000), then every router."""
        devices: dict[int, dict] = {0x0000: self._new_device(0x0000, None, "Coordinator")}
        to_visit, visited = [0x0000], set()

        while to_visit:
            router = to_visit.pop(0)
            visited.add(router)
            start = 0
            while True:
                try:
                    status, neighbors = await self.radio.zdo(router, zdo_t.ZDOCmd.Mgmt_Lqi_req, start)
                except Exception as exc:
                    devices[router]["errors"].append(f"neighbour table: no answer ({exc.__class__.__name__})")
                    break
                if status != zdo_t.Status.SUCCESS or not neighbors or not neighbors.NeighborTableList:
                    break

                for n in neighbors.NeighborTableList:
                    nwk = int(n.nwk)
                    if nwk == own_nwk:
                        continue
                    entry = devices.setdefault(nwk, self._new_device(nwk, str(n.ieee), n.device_type.name))
                    entry["ieee"] = entry["ieee"] or str(n.ieee)
                    entry["links"].append({
                        "seen_by": hex16(router),
                        "relationship": jsonable(n.relationship),
                        "lqi": int(n.lqi),
                        "depth": int(n.depth),
                        "rx_on_when_idle": jsonable(n.rx_on_when_idle),
                        "permit_joining": jsonable(n.permit_joining),
                    })
                    if (
                        n.device_type == zdo_t.Neighbor.DeviceType.Router
                        and nwk not in visited
                        and nwk not in to_visit
                    ):
                        to_visit.append(nwk)

                start += len(neighbors.NeighborTableList)
                if start >= neighbors.Entries:
                    break

        return devices

    @staticmethod
    def _new_device(nwk: int, ieee: str | None, role: str) -> dict:
        return {
            "nwk": hex16(nwk),
            "ieee": ieee,
            "role": role,
            "manufacturer": None,
            "model": None,
            "capabilities": [],
            "links": [],
            "errors": [],
        }

    async def _interview(self, nwk: int, info: dict):
        """Fill `info` with everything the device answers. Failures go into info['errors']."""
        radio = self.radio
        errors = info["errors"]

        async def attempt(what, coro):
            try:
                return await coro
            except Exception as exc:
                errors.append(f"{what}: {exc.__class__.__name__} {exc}".strip())
                return None

        if not info["ieee"]:
            info["ieee"] = await attempt("ieee address", radio.get_ieee(nwk))

        reply = await attempt("node descriptor", radio.zdo(nwk, zdo_t.ZDOCmd.Node_Desc_req, t.NWK(nwk)))
        if reply and reply[0] == zdo_t.Status.SUCCESS and reply[2] is not None:
            info["node_descriptor"] = jsonable(reply[2])

        reply = await attempt("power descriptor", radio.zdo(nwk, zdo_t.ZDOCmd.Power_Desc_req, t.NWK(nwk)))
        if reply and reply[0] == zdo_t.Status.SUCCESS and reply[2] is not None:
            info["power_descriptor"] = jsonable(reply[2])

        reply = await attempt("endpoints", radio.zdo(nwk, zdo_t.ZDOCmd.Active_EP_req, t.NWK(nwk)))
        if not reply or reply[0] != zdo_t.Status.SUCCESS:
            errors.append("no endpoint list - a sleeping battery device (remote/sensor) or switched off?")
            return

        info["endpoints"] = {}
        for ep in reply[2]:
            reply = await attempt(f"endpoint {ep} descriptor",
                                  radio.zdo(nwk, zdo_t.ZDOCmd.Simple_Desc_req, t.NWK(nwk), ep))
            if not reply or reply[0] != zdo_t.Status.SUCCESS or reply[2] is None:
                continue
            desc = reply[2]
            endpoint = {
                "profile": hex16(desc.profile),
                "profile_name": PROFILE_NAMES.get(int(desc.profile)),
                "device_type": hex16(desc.device_type),
                "device_type_name": device_type_name(int(desc.profile), int(desc.device_type)),
                "device_version": int(desc.device_version),
                "in_clusters": {},
                "out_clusters": {hex16(c): cluster_name(c) for c in desc.output_clusters},
            }
            info["endpoints"][str(ep)] = endpoint

            # Only the Home Automation / ZLL endpoints answer ZCL reads
            if int(desc.profile) not in (HA_PROFILE, 0xC05E):
                endpoint["in_clusters"] = {hex16(c): {"name": cluster_name(c)} for c in desc.input_clusters}
                continue

            for cluster_id in desc.input_clusters:
                endpoint["in_clusters"][hex16(cluster_id)] = await self._read_cluster(
                    nwk, ep, int(cluster_id), attempt
                )

            if GROUPS_CLUSTER in desc.input_clusters:
                groups = await attempt(f"endpoint {ep} groups", self._read_groups(nwk, ep))
                if groups is not None:
                    endpoint["groups"] = groups

        self._summarize(info)

    async def _read_cluster(self, nwk, ep, cluster_id, attempt) -> dict:
        cls = cluster_class(cluster_id)
        result = {"name": cluster_name(cluster_id)}

        discovered = await attempt(
            f"ep {ep} {result['name']} attribute discovery",
            self.radio.discover_attributes(nwk, ep, cluster_id),
        )
        if discovered:
            attr_ids = sorted({attr_id for attr_id, _ in discovered})
            result["attribute_source"] = "discovered"
        else:
            attr_ids = known_attribute_ids(cls)
            result["attribute_source"] = "zigpy definitions"
        if not attr_ids:
            return result

        records = await attempt(
            f"ep {ep} {result['name']} attributes",
            self.radio.read_all_attributes(nwk, ep, cluster_id, attr_ids),
        ) or {}

        discovered_types = dict(discovered or [])
        attributes, unreadable = {}, []
        for attr_id in attr_ids:
            record = records.get(attr_id)
            if isinstance(record, bytes):  # answered, but zigpy couldn't decode it: keep raw
                attr_def = cls.attributes.get(attr_id) if cls else None
                type_id = discovered_types.get(attr_id)
                try:
                    type_name = zcl_f.DataTypeId(type_id).name if type_id is not None else None
                except ValueError:
                    type_name = f"0x{type_id:02X}"
                attributes[attr_def.name if attr_def else hex16(attr_id)] = {
                    "id": hex16(attr_id), "type": type_name, "raw": record.hex(),
                    "note": "could not be decoded, raw reply bytes",
                }
            elif record is not None and record.status == zcl_f.Status.SUCCESS and record.value is not None:
                name, entry = describe_attribute(cls, record)
                attributes[name] = entry
            elif result["attribute_source"] == "discovered":
                unreadable.append(hex16(attr_id))
        result["attributes"] = attributes
        if unreadable:
            result["unreadable_attributes"] = unreadable
        return result

    async def _read_groups(self, nwk, ep) -> dict | None:
        # Groups cluster: Get Group Membership (0x02) with an empty list = "all groups"
        hdr, rest = await self.radio.cluster_command(nwk, ep, GROUPS_CLUSTER, 0x02, b"\x00")
        if not hdr.frame_control.is_cluster or hdr.command_id != 0x02 or len(rest) < 2:
            return None
        capacity, count = rest[0], rest[1]
        ids = [int.from_bytes(rest[2 + i * 2:4 + i * 2], "little") for i in range(count)]
        return {"member_of": [hex16(g) for g in ids], "free_slots": capacity}

    @staticmethod
    def _summarize(info: dict):
        """Copy the most useful facts to the top of the device entry."""
        capabilities = []
        for endpoint in info.get("endpoints", {}).values():
            clusters = endpoint["in_clusters"]
            basic = clusters.get(hex16(0x0000), {}).get("attributes", {})
            for key, attr in (("manufacturer", "manufacturer"), ("model", "model"),
                              ("sw_build_id", "sw_build_id"), ("date_code", "date_code")):
                if attr in basic and not info.get(key):
                    info[key] = basic[attr]["value"]
            if "power_source" in basic and "power_source" not in info:
                info["power_source"] = basic["power_source"].get("meaning", basic["power_source"]["value"])

            if hex16(ONOFF_CLUSTER) in clusters:
                capabilities.append("on_off")
            if hex16(LEVEL_CLUSTER) in clusters:
                capabilities.append("brightness")
            color = clusters.get(hex16(COLOR_CLUSTER))
            if color is not None:
                caps = color.get("attributes", {}).get("color_capabilities", {}).get("meaning")
                if isinstance(caps, list):
                    if "Color_temperature" in caps:
                        capabilities.append("color_temperature")
                    if set(caps) - {"Color_temperature"}:
                        capabilities.append("color")
                else:
                    capabilities.append("color")
            if endpoint.get("groups"):
                info.setdefault("groups", sorted(set(endpoint["groups"]["member_of"])))

        info["capabilities"] = sorted(set(capabilities))
        info["is_light"] = "on_off" in info["capabilities"]


def save_json(data, path):
    """Write JSON atomically, so a crash never leaves a half-written file."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, path)


# ---------------------------------------------------------------------------
# Command line
# ---------------------------------------------------------------------------

async def _main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", choices=["scan", "join", "status", "devices"])
    parser.add_argument("--port", default=DEFAULT_PORT)
    parser.add_argument("--no-tclk", action="store_true", help="join without requesting a unique link key")
    parser.add_argument("--out", default=str(DEFAULT_DEVICES_FILE), help="devices: where to save the JSON")
    args = parser.parse_args()

    async with ZigbeeRemote(args.port) as remote:
        if args.command == "scan":
            print("Scanning channels 11-26 (takes ~10 s)...")
            networks = await remote.scan()
            if not networks:
                print("No Zigbee networks found.")
            for i, n in enumerate(networks, 1):
                joinable = "OPEN FOR JOINING" if n["allowing_join"] else "closed"
                print(f"  {i}. PAN {n['pan_id']}  ext {n['extended_pan_id']}  ch {n['channel']}  "
                      f"LQI {n['lqi']}  RSSI {n['rssi']}  -> {joinable}")

        elif args.command == "join":
            async def wait_for_bridge():
                await asyncio.get_running_loop().run_in_executor(
                    None, input,
                    "\n>>> Open the Innr app and start 'add device' on the bridge, then press Enter... ",
                )
            await remote.join(request_tclk=not args.no_tclk, wait_for_bridge=wait_for_bridge)

        elif args.command == "status":
            info = await remote.network_info()
            print(json.dumps(info, indent=2) if info else "Dongle isn't on any network.")

        elif args.command == "devices":
            await remote.read_devices(args.out)


if __name__ == "__main__":
    asyncio.run(_main())
