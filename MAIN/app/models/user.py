
# Defines the roles available in the College Service Request System.

from enum import Enum


class UserRole(str, Enum):
    STUDENT = "student"
    FACULTY = "faculty"
    SERVICE_STAFF = "service_staff"
    SERVICE_LEAD = "service_lead"
    ADMIN = "admin"