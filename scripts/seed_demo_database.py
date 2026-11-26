"""Idempotent, non-destructive OptiFreight demo database seeder."""
from __future__ import annotations

import asyncio
import hashlib
import os
import sys
import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.authentication.security import hash_password
from app.db import get_sessionmaker
from app.domain.routes import get_route
from app.models import (
    DemoSubscription,
    DriverCargoRequest,
    DriverReport,
    FleetContainer,
    FleetDriver,
    InPortalNotification,
    ManualCargo,
    Organization,
    Shipment,
    User,
)

DEMO_COMPANY_LOGO = (
    "data:image/jpeg;base64,"
    "/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDABQODxIPDRQSEBIXFRQYHjIhHhwcHj0sLiQySUBMS0dARkVQWnNiUFVtVkVGZIhl"
    "bXd7gYKBTmCNl4x9lnN+gXz/2wBDARUXFx4aHjshITt8U0ZTfHx8fHx8fHx8fHx8fHx8fHx8fHx8fHx8fHx8fHx8fHx8fHx8fHx8fHx8fHx8fHx8fHx8fHx8fHx8fHz/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAX/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFAEBAAAAAAAAAAAAAAAAAAAABP/EABQRAQAAAAAAAAAAAAAAAAAAAAD/2gAMAwEAAhEDEQA/AJYBgb//2Q=="
)

COMPANY_SPECS = (
    {
        "plan": "basic",
        "name": "Basic Company",
        "legacy_name": "Demo Basic Company",
        "admin_driver_counts": (5,) * 10,
        "price": "30000",
    },
    {
        "plan": "plus",
        "name": "Plus Company",
        "legacy_name": "Demo Plus Company",
        "admin_driver_counts": (10,) * 15,
        "price": "100000",
    },
    {
        "plan": "pro",
        "name": "Pro Company",
        "legacy_name": "Demo Pro Company",
        "admin_driver_counts": (20,) * 30,
        "price": "300000",
    },
    {
        "plan": "ultra",
        "name": "Ultra Company",
        "legacy_name": "Demo Ultra Company",
        "admin_driver_counts": (40, 75, 150),
        "price": None,
    },
)

CLIENT_SPECS = (
    {
        "plan": "basic",
        "name": "Basic Client",
        "email": "client.basic@demo.test",
        "phone": "+917000000001",
        "cargo_title": "Packaged goods · Jaipur to Ajmer",
        "category": "fmcg_packaged",
        "weight_kg": 1250,
        "rate_inr": 36000,
        "pickup": {"name": "Jaipur Pickup", "lat": 26.9124, "lng": 75.7873},
        "drop": {"name": "Ajmer Delivery", "lat": 26.4499, "lng": 74.6399},
    },
    {
        "plan": "plus",
        "name": "Plus Client",
        "email": "client.plus@demo.test",
        "phone": "+917000000002",
        "cargo_title": "Automotive parts · Udaipur to Ahmedabad",
        "category": "auto_parts",
        "weight_kg": 1800,
        "rate_inr": 48000,
        "pickup": {"name": "Udaipur Pickup", "lat": 24.5854, "lng": 73.7125},
        "drop": {"name": "Ahmedabad Delivery", "lat": 23.0225, "lng": 72.5714},
    },
    {
        "plan": "pro",
        "name": "Pro Client",
        "email": "client.pro@demo.test",
        "phone": "+917000000003",
        "cargo_title": "Textiles · Vadodara to Surat",
        "category": "textiles_garments",
        "weight_kg": 2500,
        "rate_inr": 65000,
        "pickup": {"name": "Vadodara Pickup", "lat": 22.3072, "lng": 73.1812},
        "drop": {"name": "Surat Delivery", "lat": 21.1702, "lng": 72.8311},
    },
    {
        "plan": "ultra",
        "name": "Ultra Client",
        "email": "client.ultra@demo.test",
        "phone": "+917000000004",
        "cargo_title": "Machinery · Vapi to Mumbai",
        "category": "machinery_heavy",
        "weight_kg": 5000,
        "rate_inr": 95000,
        "pickup": {"name": "Vapi Pickup", "lat": 20.3717, "lng": 72.9046},
        "drop": {"name": "Mumbai Delivery", "lat": 19.0760, "lng": 72.8777},
    },
)

SHIPMENT_SCENARIOS = (
    ("live", "in_transit", True, "Live delivery"),
    ("completed", "delivered", True, "Completed delivery"),
    ("pending", "accepted", False, "Pending delivery"),
    ("cancelled", "cancelled", False, "Cancelled delivery"),
)


def stable_id(namespace: str, key: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"optifreight-demo:{namespace}:{key}"))


def demo_phone(seed: str, prefix: str) -> str:
    digest = hashlib.sha256(seed.encode("utf-8")).hexdigest()
    return f"{prefix}{int(digest, 16) % 100000000:08d}"


def demo_tracking(route: dict, shipment_index: int) -> dict:
    points = route["polyline"]
    checkpoint_indices = [2, 4, 6, 8, 11]
    checkpoint_names = ["Jaipur", "Udaipur", "Ahmedabad", "Surat", "Mumbai"]
    last_checkpoint_index = 0
    current = points[checkpoint_indices[last_checkpoint_index]]
    detour = []
    if shipment_index in {1, 3}:
        start, middle, end = points[4], points[5], points[6]
        detour = [
            points[3],
            {"lat": start["lat"] + 0.12, "lng": start["lng"] + 0.08},
            {"lat": middle["lat"] + 0.12, "lng": middle["lng"] + 0.08},
            end,
        ]
    return {
        "is_demo": True,
        "source": "synthetic_demo",
        "notice": "Illustrative checkpoints and vehicle positions; not live GPS or verified road routing.",
        "last_checkpoint_index": last_checkpoint_index,
        "checkpoints": [
            {
                "name": name,
                "location": points[point_index],
                "crossed": index <= last_checkpoint_index,
            }
            for index, (name, point_index) in enumerate(zip(checkpoint_names, checkpoint_indices))
        ],
        "truck_location": {
            "name": "Assigned delivery truck",
            "lat": current["lat"],
            "lng": current["lng"],
        },
        "nearby_trucks": [
            {
                "name": "Nearby cargo-compatible truck A",
                "vehicle_type": "General cargo truck",
                "capacity_kg": 5000,
                "location": {"name": "Jaipur staging point", **current},
                "matches_cargo": True,
            },
            {
                "name": "Nearby cargo-compatible truck B",
                "vehicle_type": "General cargo truck",
                "capacity_kg": 2500,
                "location": {
                    "name": "Nearby staging point",
                    "lat": current["lat"] + 0.035,
                    "lng": current["lng"] + 0.025,
                },
                "matches_cargo": True,
            },
        ] if shipment_index == 1 else [],
        "detour_required": bool(detour),
        "detour_polyline": detour,
    }


def complete_demo_company_profile(organization: Organization) -> None:
    profile = dict(organization.profile or {})
    profile.setdefault("logo_data_url", DEMO_COMPANY_LOGO)
    profile["headquarters_address"] = f"{organization.name}, Test City, Karnataka, 560001"
    profile.setdefault("branch_office_same_as_headquarters", True)
    profile["branch_office_address"] = profile["headquarters_address"]
    profile["profile_submitted"] = True
    organization.profile = profile


async def get_or_create_user(
    db: AsyncSession,
    *,
    email: str,
    name: str,
    phone: str,
    role: str,
    password_hash: str,
    organization_id: str | None = None,
    organization_name: str | None = None,
    admin_id: str | None = None,
    tier: str = "basic",
) -> User:
    user = await db.scalar(select(User).where(User.email == email))
    if user:
        profile = dict(user.profile or {})
        if not profile.get("demo") or not profile.get("synthetic"):
            raise RuntimeError(f"Refusing to modify non-synthetic account {email}.")
        user.name = name
        user.role = role
        user.approval_status = "approved"
        user.tier = tier
        user.organization_id = organization_id
        user.organization_name = organization_name
        user.assigned_admin_user_id = admin_id
        user.profile_completed_at = user.profile_completed_at or datetime.now(timezone.utc)
        user.profile = {**profile, "source": "demo_seeder"}
        return user
    user = User(
        id=stable_id("user", email),
        email=email,
        phone=phone,
        phone_verified=True,
        name=name,
        password_hash=password_hash,
        role=role,
        approval_status="approved",
        tier=tier,
        organization_id=organization_id,
        organization_name=organization_name,
        assigned_admin_user_id=admin_id,
        profile_completed_at=datetime.now(timezone.utc),
        profile={"demo": True, "synthetic": True, "source": "demo_seeder"},
    )
    db.add(user)
    await db.flush()
    return user


async def seed() -> None:
    password = os.environ.get("DEMO_SEED_PASSWORD")
    if not password:
        raise SystemExit("Set DEMO_SEED_PASSWORD in the environment before running the demo seeder.")
    if len(password) < 8:
        raise SystemExit("DEMO_SEED_PASSWORD must contain at least 8 characters.")
    password_hash = hash_password(password)
    sessionmaker = get_sessionmaker()

    now = datetime.now(timezone.utc)
    async with sessionmaker() as db:
        company_records = {}
        for spec in COMPANY_SPECS[:3]:
            plan = spec["plan"]
            company_name = spec["name"]
            legacy_name = spec["legacy_name"]
            org_id = stable_id("organization", legacy_name)
            org = await db.get(Organization, org_id)
            owner_email = f"owner.{legacy_name.lower().replace(' ', '.')}@demo.test"
            owner = await get_or_create_user(
                db,
                email=owner_email,
                name=f"{company_name} Owner",
                phone=demo_phone(owner_email, "+9198"),
                role="organization_owner",
                password_hash=password_hash,
                organization_id=org_id,
                organization_name=company_name,
                tier=plan,
            )
            if org is not None and not (
                (org.profile or {}).get("demo") and (org.profile or {}).get("synthetic")
            ):
                raise RuntimeError(f"Refusing to modify non-synthetic organization {org_id}.")
            if org is None:
                org = Organization(
                    id=org_id,
                    name=company_name,
                    owner_user_id=owner.id,
                    status="active",
                    approval_status="approved",
                    profile={
                        "demo": True,
                        "synthetic": True,
                        "headquarters_address": f"{company_name}, Test City, Karnataka, 560001",
                        "branch_office_same_as_headquarters": True,
                    },
                )
                db.add(org)
                await db.flush()
            org.name = company_name
            org.owner_user_id = owner.id
            org.status = "active"
            org.approval_status = "approved"
            complete_demo_company_profile(org)

            admins = []
            drivers = []
            driver_cursor = 1
            for admin_index, assigned_driver_count in enumerate(spec["admin_driver_counts"], start=1):
                admin_email = f"admin.{admin_index}.{legacy_name.lower().replace(' ', '.')}@demo.test"
                admin = await get_or_create_user(
                    db,
                    email=admin_email,
                    name=f"{plan.title()} Admin {admin_index}",
                    phone=demo_phone(admin_email, "+9197"),
                    role="organization_admin",
                    password_hash=password_hash,
                    organization_id=org_id,
                    organization_name=company_name,
                    tier=plan,
                )
                admin.profile = {
                    "demo": True,
                    "synthetic": True,
                    "source": "demo_seeder",
                    "current_address": "Test address, Test City, Karnataka, 560001",
                    "permanent_address": "Test address, Test City, Karnataka, 560001",
                    "permanent_same_as_current": True,
                }
                admins.append(admin)
                for _ in range(assigned_driver_count):
                    driver_email = f"driver.{driver_cursor}.{legacy_name.lower().replace(' ', '.')}@demo.test"
                    driver = await get_or_create_user(
                        db,
                        email=driver_email,
                        name=f"{plan.title()} Driver {driver_cursor}",
                        phone=demo_phone(driver_email, "+9196"),
                        role="driver",
                        password_hash=password_hash,
                        organization_id=org_id,
                        organization_name=company_name,
                        admin_id=admin.id,
                        tier=plan,
                    )
                    fleet_driver = await db.scalar(select(FleetDriver).where(FleetDriver.email == driver_email))
                    if not fleet_driver:
                        fleet_driver = FleetDriver(
                            id=stable_id("fleet-driver", driver_email),
                            organization_id=org_id,
                            name=driver.name,
                            email=driver_email,
                            address="Test address, Test City, Karnataka",
                            verification_status="demo_verified",
                        )
                        db.add(fleet_driver)
                    else:
                        if fleet_driver.organization_id != org_id or fleet_driver.verification_status != "demo_verified":
                            raise RuntimeError(f"Refusing to modify non-synthetic fleet driver {driver_email}.")
                        fleet_driver.organization_id = org_id
                        fleet_driver.name = driver.name
                        fleet_driver.address = "Test address, Test City, Karnataka"
                        fleet_driver.verification_status = "demo_verified"
                    drivers.append((driver, fleet_driver))
                    driver_cursor += 1

            scope_key = f"org:{org_id}"
            subscription = await db.scalar(select(DemoSubscription).where(DemoSubscription.scope_key == scope_key))
            if subscription is not None and subscription.owner_user_id != owner.id:
                raise RuntimeError(f"Refusing to modify another account's subscription {scope_key}.")
            if subscription is None:
                subscription = DemoSubscription(
                    id=stable_id("subscription", scope_key),
                    scope_key=scope_key,
                    owner_user_id=owner.id,
                    organization_id=org_id,
                )
                db.add(subscription)
            subscription.plan = plan
            subscription.status = "active"
            subscription.billing_cycle = "monthly"
            subscription.current_period_start = now
            subscription.current_period_end = now + timedelta(days=30)
            subscription.cancel_at_period_end = False
            subscription.current_price_inr = Decimal(spec["price"])
            company_records[plan] = {
                "organization": org,
                "owner": owner,
                "admins": admins,
                "drivers": drivers,
            }

        ultra_spec = COMPANY_SPECS[3]
        ultra_name = ultra_spec["name"]
        ultra_legacy_name = ultra_spec["legacy_name"]
        ultra_org_id = stable_id("organization", ultra_legacy_name)
        ultra_owner_email = f"owner.{ultra_legacy_name.lower().replace(' ', '.')}@demo.test"
        ultra_owner = await get_or_create_user(
            db,
            email=ultra_owner_email,
            name="Ultra Company Owner",
            phone="+919000000041",
            role="organization_owner",
            password_hash=password_hash,
            organization_id=ultra_org_id,
            organization_name=ultra_name,
            tier="ultra",
        )
        ultra_org = await db.get(Organization, ultra_org_id)
        if ultra_org is not None and not (
            (ultra_org.profile or {}).get("demo") and (ultra_org.profile or {}).get("synthetic")
        ):
            raise RuntimeError(f"Refusing to modify non-synthetic organization {ultra_org_id}.")
        if ultra_org is None:
            ultra_org = Organization(
                id=ultra_org_id,
                name=ultra_name,
                owner_user_id=ultra_owner.id,
                status="active",
                approval_status="approved",
                profile={"demo": True, "synthetic": True, "headquarters_address": "Ultra Company, Test City, Karnataka, 560001", "branch_office_same_as_headquarters": True},
            )
            db.add(ultra_org)
            await db.flush()
        ultra_org.name = ultra_name
        ultra_org.owner_user_id = ultra_owner.id
        ultra_org.status = "active"
        ultra_org.approval_status = "approved"
        complete_demo_company_profile(ultra_org)

        ultra_admins = []
        ultra_drivers = []
        driver_cursor = 1
        for admin_index, assigned_count in enumerate(ultra_spec["admin_driver_counts"], start=1):
            admin_email = f"admin.{admin_index}.{ultra_legacy_name.lower().replace(' ', '.')}@demo.test"
            admin = await get_or_create_user(
                db,
                email=admin_email,
                name=f"Ultra Admin {admin_index}",
                phone=f"+919000000{admin_index:03d}",
                role="organization_admin",
                password_hash=password_hash,
                organization_id=ultra_org_id,
                organization_name=ultra_name,
                tier="ultra",
            )
            admin.profile = {
                "demo": True,
                "synthetic": True,
                "source": "demo_seeder",
                "current_address": "Test address, Test City, Karnataka, 560001",
                "permanent_address": "Test address, Test City, Karnataka, 560001",
                "permanent_same_as_current": True,
            }
            ultra_admins.append(admin)
            for _ in range(assigned_count):
                driver_email = f"driver.{driver_cursor}.{ultra_legacy_name.lower().replace(' ', '.')}@demo.test"
                driver = await get_or_create_user(
                    db,
                    email=driver_email,
                    name=f"Ultra Driver {driver_cursor}",
                    phone=f"+9180{driver_cursor:08d}",
                    role="driver",
                    password_hash=password_hash,
                    organization_id=ultra_org_id,
                    organization_name=ultra_name,
                    admin_id=admin.id,
                    tier="ultra",
                )
                fleet_driver = await db.scalar(select(FleetDriver).where(FleetDriver.email == driver_email))
                if not fleet_driver:
                    fleet_driver = FleetDriver(
                        id=stable_id("fleet-driver", driver_email),
                        organization_id=ultra_org_id,
                        name=driver.name,
                        email=driver_email,
                        address="Test address, Test City, Karnataka",
                        verification_status="demo_verified",
                    )
                    db.add(fleet_driver)
                else:
                    if fleet_driver.organization_id != ultra_org_id or fleet_driver.verification_status != "demo_verified":
                        raise RuntimeError(f"Refusing to modify non-synthetic fleet driver {driver_email}.")
                    fleet_driver.organization_id = ultra_org_id
                    fleet_driver.name = driver.name
                    fleet_driver.address = "Test address, Test City, Karnataka"
                    fleet_driver.verification_status = "demo_verified"
                ultra_drivers.append((driver, fleet_driver))
                driver_cursor += 1

        ultra_scope_key = f"org:{ultra_org_id}"
        ultra_subscription = await db.scalar(select(DemoSubscription).where(DemoSubscription.scope_key == ultra_scope_key))
        if ultra_subscription is not None and ultra_subscription.owner_user_id != ultra_owner.id:
            raise RuntimeError(f"Refusing to modify another account's subscription {ultra_scope_key}.")
        if ultra_subscription is None:
            ultra_subscription = DemoSubscription(
                id=stable_id("subscription", f"org:{ultra_org_id}"),
                scope_key=ultra_scope_key,
                owner_user_id=ultra_owner.id,
                organization_id=ultra_org_id,
            )
            db.add(ultra_subscription)
        ultra_subscription.plan = "ultra"
        ultra_subscription.status = "active"
        ultra_subscription.billing_cycle = "monthly"
        ultra_subscription.current_period_start = now
        ultra_subscription.current_period_end = now + timedelta(days=30)
        ultra_subscription.cancel_at_period_end = False
        ultra_subscription.current_price_inr = None
        company_records["ultra"] = {
            "organization": ultra_org,
            "owner": ultra_owner,
            "admins": ultra_admins,
            "drivers": ultra_drivers,
        }

        clients = {}
        for client_spec in CLIENT_SPECS:
            plan = client_spec["plan"]
            client_name = client_spec["name"]
            client_email = client_spec["email"]
            client = await get_or_create_user(
                db,
                email=client_email,
                name=client_name,
                phone=client_spec["phone"],
                role="client",
                password_hash=password_hash,
                tier=plan,
            )
            client.profile = {
                "demo": True,
                "synthetic": True,
                "source": "demo_seeder",
                "headquarters_address": f"{client_name}, Test City, Karnataka, 560001",
                "profile_complete": True,
            }
            client.profile_completed_at = now
            scope_key = f"user:{client.id}"
            subscription = await db.scalar(select(DemoSubscription).where(DemoSubscription.scope_key == scope_key))
            if subscription is not None and subscription.owner_user_id != client.id:
                raise RuntimeError(f"Refusing to modify another account's subscription {scope_key}.")
            if subscription is None:
                subscription = DemoSubscription(
                    id=stable_id("subscription", scope_key),
                    scope_key=scope_key,
                    owner_user_id=client.id,
                    organization_id=None,
                )
                db.add(subscription)
            subscription.plan = plan
            subscription.status = "active"
            subscription.billing_cycle = "monthly"
            subscription.current_period_start = now
            subscription.current_period_end = now + timedelta(days=30)
            subscription.cancel_at_period_end = False
            subscription.current_price_inr = None
            clients[plan] = client

        route = get_route("delhi_mumbai")
        if not route:
            raise RuntimeError("The seeded delivery scenarios require the Delhi–Mumbai route.")

        containers_by_plan = {}
        for plan, company in company_records.items():
            organization = company["organization"]
            containers = []
            for index, (driver_user, fleet_driver) in enumerate(company["drivers"][:2], start=1):
                registration = f"{plan.upper()}-TRUCK-{index:03d}"
                container = await db.scalar(select(FleetContainer).where(
                    FleetContainer.organization_id == organization.id,
                    FleetContainer.registration_number == registration,
                ))
                truck = {
                    "vehicle_class": "hcv_10wheel",
                    "body_type": "closed_body",
                    "max_payload_kg": 21000,
                    "available_payload_kg": 18000,
                    "available_volume_m3": 60,
                    "location": route["origin"],
                    "available_from": now.isoformat(),
                    "handling_equipment": [],
                    "vehicle_name": f"{plan.title()} Company truck {index}",
                }
                if container is None:
                    container = FleetContainer(
                        id=stable_id("fleet-container", f"{organization.id}:{registration}"),
                        organization_id=organization.id,
                        registration_number=registration,
                        truck=truck,
                        documents={"source": "synthetic"},
                        driver_id=fleet_driver.id,
                    )
                    db.add(container)
                else:
                    if (container.documents or {}).get("source") != "synthetic":
                        raise RuntimeError(f"Refusing to modify non-synthetic fleet container {registration}.")
                    container.truck = truck
                    container.documents = {"source": "synthetic"}
                    container.driver_id = fleet_driver.id
                containers.append(container)
            containers_by_plan[plan] = containers

        for client_spec in CLIENT_SPECS:
            plan = client_spec["plan"]
            client = clients[plan]
            company = company_records[plan]
            organization = company["organization"]
            owner = company["owner"]
            admin = company["admins"][0]
            driver_pairs = company["drivers"]
            containers = containers_by_plan[plan]
            cargo_by_scenario = {}

            for index, (key, status, assigned, label) in enumerate(SHIPMENT_SCENARIOS, start=1):
                if assigned:
                    driver_index = index - 1
                    driver_user, fleet_driver = driver_pairs[driver_index]
                    container = containers[driver_index]
                else:
                    driver_user = None
                    fleet_driver = None
                    container = None

                cargo_key = f"{client.email}:tiered:{key}"
                if plan == "basic" and key == "live":
                    cargo_key = f"{client.email}:map-live"
                cargo_id = stable_id("cargo", cargo_key)
                pickup = {
                    **client_spec["pickup"],
                    "original_address": client_spec["pickup"]["name"],
                }
                drop = {
                    **client_spec["drop"],
                    "original_address": client_spec["drop"]["name"],
                }
                cargo_title = f"{client_spec['cargo_title']} · {label}"
                cargo = await db.get(ManualCargo, cargo_id)
                cargo_values = {
                    "title": cargo_title,
                    "category": client_spec["category"],
                    "weight_kg": client_spec["weight_kg"] + (index - 1) * 100,
                    "rate_inr": client_spec["rate_inr"] + (index - 1) * 2500,
                    "pickup": pickup,
                    "drop": drop,
                    "pickup_window_start": (now + timedelta(hours=2)).isoformat(),
                    "pickup_window_end": (now + timedelta(hours=8)).isoformat(),
                    "loading_minutes": 45,
                    "unloading_minutes": 30,
                    "hazardous": False,
                    "created_at": now - timedelta(days=2 if status == "delivered" else 0),
                    "source_type": "synthetic",
                    "source_record_id": f"tiered-{plan}-{key}-{client.id}",
                    "assigned_driver_id": driver_user.id if driver_user else None,
                    "assignment_status": "assigned" if assigned else "open",
                    "food_storage_type": "not_food",
                    "package_count": 24 + index,
                    "cargo_dimensions": {"length_m": 2.4, "width_m": 1.8, "height_m": 1.6},
                    "volume_m3": 6.9,
                    "required_vehicle_type": "Heavy rigid truck (3 axle)",
                    "special_handling": None,
                    "expires_at": now + timedelta(days=7),
                }
                if cargo is None:
                    cargo = ManualCargo(
                        id=cargo_id,
                        owner_id=client.id,
                        **cargo_values,
                    )
                    db.add(cargo)
                else:
                    if cargo.owner_id != client.id or cargo.source_type != "synthetic":
                        raise RuntimeError(f"Refusing to modify non-synthetic cargo {cargo_id}.")
                    for field, value in cargo_values.items():
                        if field == "assignment_status" and cargo.assignment_status != "open":
                            continue
                        if field == "assigned_driver_id" and cargo.assigned_driver_id is not None:
                            continue
                        setattr(cargo, field, value)
                cargo_by_scenario[key] = cargo

                created_at = now - timedelta(days=2 if status == "delivered" else 0)
                if status == "in_transit":
                    history = [
                        {"status": "accepted", "at": (created_at - timedelta(hours=4)).isoformat()},
                        {"status": "heading_to_pickup", "at": (created_at - timedelta(hours=3)).isoformat()},
                        {"status": "loaded", "at": (created_at - timedelta(hours=2)).isoformat()},
                        {"status": "in_transit", "at": created_at.isoformat()},
                    ]
                elif status == "delivered":
                    history = [
                        {"status": "accepted", "at": (created_at - timedelta(hours=8)).isoformat()},
                        {"status": "heading_to_pickup", "at": (created_at - timedelta(hours=7)).isoformat()},
                        {"status": "loaded", "at": (created_at - timedelta(hours=6)).isoformat()},
                        {"status": "in_transit", "at": (created_at - timedelta(hours=5)).isoformat()},
                        {"status": "delivered", "at": created_at.isoformat()},
                    ]
                elif status == "cancelled":
                    history = [
                        {"status": "accepted", "at": created_at.isoformat()},
                        {"status": "cancelled", "at": (created_at + timedelta(minutes=20)).isoformat()},
                    ]
                else:
                    history = [{"status": "accepted", "at": created_at.isoformat()}]

                candidate_id = f"{plan}-{key}-shipment"
                candidate = {
                    "id": candidate_id,
                    "title": cargo_title,
                    "category": cargo.category,
                    "category_label": cargo.category.replace("_", " ").title(),
                    "weight_kg": cargo.weight_kg,
                    "pickup": pickup,
                    "drop": drop,
                    "pickup_at_km": 250 + (index - 1) * 80,
                    "drop_at_km": 340 + (index - 1) * 80,
                    "source_type": "synthetic",
                    "listing_status": "assigned" if assigned else "open",
                    "is_bundle": False,
                    "bundle_size": 1,
                    "eligible": "pass",
                    "rejection_codes": [],
                    "checks": [],
                    "explanation": [],
                    "load_profile": [],
                    "timeline": [],
                    "net_inr": {"low": None, "expected": None, "high": None},
                    "baseline_score": None,
                    "model_score": None,
                    "route_class": "off_route",
                    "pickup_excursion_km": 12,
                    "drop_excursion_km": 8,
                    "extra_distance_km": 20,
                    "extra_active_minutes": 90,
                    "revenue_inr": cargo.rate_inr,
                    "incremental_cost_inr": None,
                    "budget_after": None,
                    "member_ids": [cargo.id],
                    "synthetic": True,
                    "seed_revision": 2,
                    "demo_tracking": demo_tracking(route, index),
                }
                if plan == "basic":
                    shipment_key = f"driver-map:{driver_pairs[0][1].id}:{index}"
                else:
                    shipment_key = f"tiered-delivery:{plan}:{key}"
                shipment_id = stable_id("shipment", shipment_key)
                shipment = await db.get(Shipment, shipment_id)
                is_new_seed = shipment is None or not (shipment.candidate or {}).get("seed_revision")
                if shipment is None:
                    shipment = Shipment(
                        id=shipment_id,
                        user_id=owner.id,
                        run_id=f"tiered-demo-{plan}",
                        candidate_id=candidate_id,
                        route_id=route["id"],
                        route_version=route["version"],
                        route_name=route["name"],
                        origin=route["origin"],
                        destination=route["destination"],
                        route_polyline=route["polyline"],
                        candidate=candidate,
                        status=status,
                        status_history=history,
                        assigned_driver_id=fleet_driver.id if fleet_driver else None,
                        fleet_container_id=container.id if container else None,
                        assigned_by_user_id=admin.id if assigned else None,
                        assigned_at=created_at if assigned else None,
                        created_at=created_at,
                    )
                    db.add(shipment)
                else:
                    if shipment.user_id != owner.id or not (shipment.candidate or {}).get("synthetic"):
                        raise RuntimeError(f"Refusing to modify non-synthetic shipment {shipment_id}.")
                    shipment.candidate = {**(shipment.candidate or {}), **candidate}
                    shipment.route_name = route["name"]
                    shipment.route_version = route["version"]
                    shipment.origin = route["origin"]
                    shipment.destination = route["destination"]
                    shipment.route_polyline = route["polyline"]
                    if is_new_seed:
                        shipment.status = status
                        shipment.status_history = history
                        shipment.assigned_driver_id = fleet_driver.id if fleet_driver else None
                        shipment.fleet_container_id = container.id if container else None
                        shipment.assigned_by_user_id = admin.id if assigned else None
                        shipment.assigned_at = created_at if assigned else None

                if key == "live":
                    report_id = stable_id("driver-report", f"{plan}:{shipment_id}")
                    report = await db.get(DriverReport, report_id)
                    if report is not None and (
                        report.client_user_id != client.id
                        or report.shipment_id != shipment_id
                        or report.organization_id != organization.id
                    ):
                        raise RuntimeError(f"Refusing to modify unrelated driver report {report_id}.")
                    if report is None:
                        report = DriverReport(
                            id=report_id,
                            shipment_id=shipment_id,
                            client_user_id=client.id,
                            driver_id=fleet_driver.id,
                            organization_id=organization.id,
                            reason="The delivery status needs a routine review.",
                            status="pending",
                            created_at=now - timedelta(hours=1),
                        )
                        db.add(report)
                    notification_specs = [
                        (admin, "Driver report awaiting review"),
                        (owner, "Driver report awaiting review"),
                    ]
                    for recipient, title in notification_specs:
                        notification_id = stable_id("notification", f"report:{report_id}:{recipient.id}")
                        notification = await db.get(InPortalNotification, notification_id)
                        if notification is not None and notification.recipient_user_id != recipient.id:
                            raise RuntimeError(f"Refusing to modify unrelated notification {notification_id}.")
                        if notification is None:
                            db.add(InPortalNotification(
                                id=notification_id,
                                recipient_user_id=recipient.id,
                                organization_id=organization.id,
                                kind="driver_report",
                                title=title,
                                message=f"A client submitted a report about {driver_user.name}.",
                                payload={"report_id": report_id},
                                created_at=now - timedelta(hours=1),
                            ))

            pending_cargo = cargo_by_scenario["pending"]
            request_id = stable_id("driver-cargo-request", f"{driver_pairs[0][0].id}:{pending_cargo.id}")
            request = await db.get(DriverCargoRequest, request_id)
            if request is not None and (
                request.driver_user_id != driver_pairs[0][0].id or request.cargo_id != pending_cargo.id
            ):
                raise RuntimeError(f"Refusing to modify unrelated cargo request {request_id}.")
            if request is None:
                db.add(DriverCargoRequest(
                    id=request_id,
                    organization_id=organization.id,
                    driver_user_id=driver_pairs[0][0].id,
                    cargo_id=pending_cargo.id,
                    route_plan_shipment_id=stable_id(
                        "shipment",
                        f"driver-map:{driver_pairs[0][1].id}:1" if plan == "basic"
                        else f"tiered-delivery:{plan}:live",
                    ),
                    status="pending",
                    requested_at=now - timedelta(minutes=30),
                ))

        await db.commit()
        print(
            "Tiered sample workspaces seeded with cargo, delivery stages, requests, and reports. "
            "Accounts use DEMO_SEED_PASSWORD; no password was logged."
        )


if __name__ == "__main__":
    asyncio.run(seed())
