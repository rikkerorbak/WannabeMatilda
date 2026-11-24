"""
Data models and Enums for Matilda Platform Client.

Matches OpenAPI / Swagger definitions for Party and ServiceUsers endpoints.
"""

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any

from matilda_client.utils import clean_dict


class DayOfWeek(str, Enum):
    """Days of the week."""
    SUNDAY = "Sunday"
    MONDAY = "Monday"
    TUESDAY = "Tuesday"
    WEDNESDAY = "Wednesday"
    THURSDAY = "Thursday"
    FRIDAY = "Friday"
    SATURDAY = "Saturday"


class CommonStatus(str, Enum):
    """Common statuses for entities in Matilda."""
    INACTIVE = "Inactive"
    ACTIVE = "Active"
    DELETED = "Deleted"
    PLANNING = "Planning"
    UNKNOWN = "Unknown"
    ORDERED = "Ordered"
    REPLACED = "Replaced"
    DELIVERED = "Delivered"
    CANCELLED = "Cancelled"
    IS_BEING_MODIFIED = "IsBeingModified"
    IS_BEING_PROCESSED = "IsBeingProcessed"
    SENT = "Sent"
    REGISTERING = "Registering"
    APPROVED = "Approved"


class OrderType(str, Enum):
    """Order types in Matilda."""
    GROSSERIES = "Grosseries"
    CANTINE = "Cantine"
    TRAY = "Tray"
    MEALBOX = "Mealbox"
    RE_PURCHASE = "RePurchase"


@dataclass
class ServicePeriod:
    """Represents a service period for a service user."""
    start: str | None = None
    end: str | None = None
    customerExternalId: str | None = None
    customerName: str | None = None
    externalId: str | None = None
    externalValues: dict[str, Any] | None = None
    externalSystem: str | None = None
    mealType: str | None = None
    comment: str | None = None
    portionSize: str | None = None
    orderType: str | OrderType | None = None
    allergens: list[str] | None = None
    enabledWeekDays: list[str | DayOfWeek] | None = None

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        if self.enabledWeekDays:
            d["enabledWeekDays"] = [
                day.value if isinstance(day, DayOfWeek) else day
                for day in self.enabledWeekDays
            ]
        if isinstance(self.orderType, OrderType):
            d["orderType"] = self.orderType.value
        return clean_dict(d)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ServicePeriod":
        return cls(
            start=data.get("start"),
            end=data.get("end"),
            customerExternalId=data.get("customerExternalId"),
            customerName=data.get("customerName"),
            externalId=data.get("externalId"),
            externalValues=data.get("externalValues"),
            externalSystem=data.get("externalSystem"),
            mealType=data.get("mealType"),
            comment=data.get("comment"),
            portionSize=data.get("portionSize"),
            orderType=data.get("orderType"),
            allergens=data.get("allergens"),
            enabledWeekDays=data.get("enabledWeekDays"),
        )


@dataclass
class ServiceUserRequest:
    """Request payload to create or update a service user."""
    externalId: str
    servicePeriods: list[ServicePeriod | dict[str, Any]]
    personalIdNumber: str | None = None
    firstName: str | None = None
    lastName: str | None = None
    phone: str | None = None
    email: str | None = None
    streetAddress: str | None = None
    careOf: str | None = None
    zipCode: str | None = None
    city: str | None = None
    mealType: str | None = None
    comment: str | None = None
    portionSize: str | None = None
    orderType: str | OrderType | None = None
    allergens: list[str] | None = None
    enabledWeekDays: list[str | DayOfWeek] | None = None
    extraData: dict[str, Any] | None = None
    username: str | None = None
    loginEnabled: bool | None = None
    createOrderTemplate: bool | None = None
    password: str | None = None

    def to_dict(self) -> dict[str, Any]:
        periods = []
        for p in self.servicePeriods:
            if isinstance(p, ServicePeriod):
                periods.append(p.to_dict())
            elif isinstance(p, dict):
                periods.append(p)
        res = asdict(self)
        res["servicePeriods"] = periods
        if self.enabledWeekDays:
            res["enabledWeekDays"] = [
                day.value if isinstance(day, DayOfWeek) else day
                for day in self.enabledWeekDays
            ]
        if isinstance(self.orderType, OrderType):
            res["orderType"] = self.orderType.value
        return clean_dict(res)


@dataclass
class ServiceUserResponse:
    """Response returned for a service user from Matilda."""
    externalId: str
    id: str | None = None
    personalIdNumber: str | None = None
    firstName: str | None = None
    lastName: str | None = None
    phone: str | None = None
    email: str | None = None
    streetAddress: str | None = None
    careOf: str | None = None
    zipCode: str | None = None
    city: str | None = None
    servicePeriods: list[dict[str, Any]] = field(default_factory=list)
    mealType: str | None = None
    comment: str | None = None
    portionSize: str | None = None
    orderType: str | None = None
    allergens: list[str] | None = None
    enabledWeekDays: list[str] | None = None
    extraData: dict[str, Any] | None = None
    username: str | None = None
    loginEnabled: bool | None = None
    status: str | None = None
    isPausedOrder: bool | None = None
    isFinishedUser: bool | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ServiceUserResponse":
        return cls(
            externalId=data.get("externalId", ""),
            id=data.get("id"),
            personalIdNumber=data.get("personalIdNumber"),
            firstName=data.get("firstName"),
            lastName=data.get("lastName"),
            phone=data.get("phone"),
            email=data.get("email"),
            streetAddress=data.get("streetAddress"),
            careOf=data.get("careOf"),
            zipCode=data.get("zipCode"),
            city=data.get("city"),
            servicePeriods=data.get("servicePeriods") or [],
            mealType=data.get("mealType"),
            comment=data.get("comment"),
            portionSize=data.get("portionSize"),
            orderType=data.get("orderType"),
            allergens=data.get("allergens"),
            enabledWeekDays=data.get("enabledWeekDays"),
            extraData=data.get("extraData"),
            username=data.get("username"),
            loginEnabled=data.get("loginEnabled"),
            status=data.get("status"),
            isPausedOrder=data.get("isPausedOrder"),
            isFinishedUser=data.get("isFinishedUser"),
        )


@dataclass
class ServiceUserFilter:
    """Filter criteria when searching for service users."""
    personalIdNumber: str | None = None
    customerExternalId: str | None = None
    externalId: str | None = None
    servicePeriodStart: str | None = None
    servicePeriodEnd: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return clean_dict(asdict(self))


@dataclass
class ServiceUserIdentifier:
    """Identifier for service user (by externalId or personalIdNumber)."""
    externalId: str | None = None
    personalIdNumber: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return clean_dict(asdict(self))

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ServiceUserIdentifier":
        return cls(
            externalId=data.get("externalId"),
            personalIdNumber=data.get("personalIdNumber"),
        )


@dataclass
class AttendanceRequest:
    """Request for registering service user attendance / absences."""
    externalId: str | None = None
    numberOfAttendees: int | None = None
    absentServiceUsers: list[ServiceUserIdentifier | dict[str, Any]] | None = None

    def to_dict(self) -> dict[str, Any]:
        absent = []
        if self.absentServiceUsers:
            for u in self.absentServiceUsers:
                if isinstance(u, ServiceUserIdentifier):
                    absent.append(u.to_dict())
                elif isinstance(u, dict):
                    absent.append(u)
        res = asdict(self)
        if absent:
            res["absentServiceUsers"] = absent
        return clean_dict(res)


@dataclass
class AttendingServiceUsersRequest:
    """Request for registering attending service users for a meal."""
    externalId: str
    mealId: str
    attendingServiceUsers: list[ServiceUserIdentifier | dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        attending = []
        for u in self.attendingServiceUsers:
            if isinstance(u, ServiceUserIdentifier):
                attending.append(u.to_dict())
            elif isinstance(u, dict):
                attending.append(u)
        res = asdict(self)
        res["attendingServiceUsers"] = attending
        return clean_dict(res)


@dataclass
class Party:
    """Represents a Party (Organization / Supplier / Unit) in Matilda."""
    id: int | None = None
    name: str | None = None
    shortName: str | None = None
    streetAddress: str | None = None
    postalCode: str | None = None
    postalAddress: str | None = None
    externalId: str | None = None
    gln: str | None = None
    glnBy: str | None = None
    invoiceSystemId: int | None = None
    isProducer: bool | None = None
    isRecipeOwner: bool | None = None
    isSupplier: bool | None = None
    isGroceriesOwner: bool | None = None
    isExternal: bool | None = None
    isManager: bool | None = None
    lastModified: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Party":
        return cls(
            id=data.get("id"),
            name=data.get("name"),
            shortName=data.get("shortName"),
            streetAddress=data.get("streetAddress"),
            postalCode=data.get("postalCode"),
            postalAddress=data.get("postalAddress"),
            externalId=data.get("externalId"),
            gln=data.get("gln"),
            glnBy=data.get("glnBy"),
            invoiceSystemId=data.get("invoiceSystemId"),
            isProducer=data.get("isProducer"),
            isRecipeOwner=data.get("isRecipeOwner"),
            isSupplier=data.get("isSupplier"),
            isGroceriesOwner=data.get("isGroceriesOwner"),
            isExternal=data.get("isExternal"),
            isManager=data.get("isManager"),
            lastModified=data.get("lastModified"),
        )


@dataclass
class PartyPaginationResponse:
    """Pagination response for parties endpoint."""
    startIndex: int | None = None
    itemsPerPage: int | None = None
    totalItemsCount: int | None = None
    totalPages: int | None = None
    items: list[Party] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PartyPaginationResponse":
        raw_items = data.get("items") or []
        items = [Party.from_dict(item) if isinstance(item, dict) else item for item in raw_items]
        return cls(
            startIndex=data.get("startIndex"),
            itemsPerPage=data.get("itemsPerPage"),
            totalItemsCount=data.get("totalItemsCount"),
            totalPages=data.get("totalPages"),
            items=items,
        )


@dataclass
class ServiceUserDocumentResponse:
    """Represents a service user document metadata."""
    documentId: str | None = None
    name: str | None = None
    date: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ServiceUserDocumentResponse":
        return cls(
            documentId=data.get("documentId"),
            name=data.get("name"),
            date=data.get("date"),
        )
