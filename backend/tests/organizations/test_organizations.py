import uuid

import pytest
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.db.models.deletion import ProtectedError
from rest_framework.test import APIClient

from apps.organizations.models import Organization


@pytest.fixture
def staff_user(db, django_user_model):
    return django_user_model.objects.create_user(
        email="org-admin@example.com",
        password="StrongPassword123!",
        is_staff=True,
    )


@pytest.fixture
def member(db, django_user_model):
    return django_user_model.objects.create_user(
        email="member@example.com",
        password="StrongPassword123!",
    )


@pytest.fixture
def staff_client(staff_user):
    client = APIClient()
    client.force_authenticate(user=staff_user)
    return client


@pytest.fixture
def member_client(member):
    client = APIClient()
    client.force_authenticate(user=member)
    return client


@pytest.fixture
def organization(db):
    return Organization.objects.create(
        name="Moyo University",
        code="moyo-university",
        organization_type=Organization.OrganizationType.OTHER,
        description="Health research and training",
    )


@pytest.mark.django_db
class TestOrganizationModel:
    def test_defaults_and_uuid_primary_key(self):
        organization = Organization.objects.create(
            name="Research Institute",
            code="research-institute",
        )

        assert isinstance(organization.id, uuid.UUID)
        assert organization.organization_type == Organization.OrganizationType.OTHER
        assert organization.is_active is True
        assert organization.parent is None
        assert organization.description == ""

    def test_supports_non_hospital_research_organizations(self, organization):
        assert organization.name == "Moyo University"
        assert organization.organization_type == "other"

    def test_all_declared_organization_types_are_valid_choices(self):
        assert {value for value, _label in Organization.OrganizationType.choices} == {
            "ministry", "district", "partner", "other"
        }

    def test_parent_and_child_relationship(self, organization):
        child = Organization.objects.create(
            name="School of Public Health",
            code="school-of-public-health",
            parent=organization,
        )

        assert child.parent == organization
        assert list(organization.children.all()) == [child]

    def test_string_representation_is_name(self, organization):
        assert str(organization) == "Moyo University"

    def test_code_must_be_unique(self, organization):
        duplicate = Organization(
            name="Another University",
            code=organization.code,
        )

        with pytest.raises(ValidationError) as exc_info:
            duplicate.full_clean()

        assert "code" in exc_info.value.message_dict

    def test_parent_cannot_be_deleted_while_children_exist(self, organization):
        Organization.objects.create(
            name="Research unit",
            code="research-unit",
            parent=organization,
        )

        with pytest.raises(ProtectedError):
            organization.delete()

    def test_clean_rejects_self_as_parent(self, organization):
        organization.parent = organization

        with pytest.raises(ValidationError, match="own ancestor"):
            organization.clean()

    def test_clean_rejects_descendant_as_parent(self, organization):
        child = Organization.objects.create(
            name="Research unit",
            code="research-unit",
            parent=organization,
        )
        organization.parent = child

        with pytest.raises(ValidationError, match="own ancestor"):
            organization.clean()


@pytest.mark.django_db
class TestOrganizationAPI:
    url = "/api/v1/organizations/"

    def test_anonymous_user_cannot_list_organizations(self, organization):
        response = APIClient().get(self.url)

        assert response.status_code == 401

    def test_authenticated_user_can_list_organizations(self, member_client, organization):
        response = member_client.get(self.url)

        assert response.status_code == 200
        assert response.data["count"] == 1
        assert response.data["results"][0]["id"] == str(organization.id)

    def test_authenticated_user_can_retrieve_organization(self, member_client, organization):
        response = member_client.get(f"{self.url}{organization.id}/")

        assert response.status_code == 200
        assert response.data["name"] == organization.name
        assert response.data["code"] == organization.code

    def test_unknown_organization_returns_404(self, staff_client):
        response = staff_client.get(f"{self.url}{uuid.uuid4()}/")

        assert response.status_code == 404

    @pytest.mark.parametrize("method", ["post", "put", "patch", "delete"])
    def test_anonymous_user_cannot_mutate_organizations(self, method, organization):
        response = getattr(APIClient(), method)(
            f"{self.url}{organization.id}/" if method != "post" else self.url,
            {"name": "Updated"},
        )

        assert response.status_code == 401

    @pytest.mark.parametrize("method", ["post", "put", "patch", "delete"])
    def test_non_staff_user_cannot_mutate_organizations(
        self, method, member_client, organization
    ):
        response = getattr(member_client, method)(
            f"{self.url}{organization.id}/" if method != "post" else self.url,
            {"name": "Updated"},
        )

        assert response.status_code == 403

    def test_staff_user_can_create_university(self, staff_client):
        response = staff_client.post(
            self.url,
            {
                "name": "Lakeview University",
                "code": "lakeview-university",
                "organization_type": "other",
                "description": "Conducts public health research",
            },
        )

        assert response.status_code == 201
        assert response.data["organization_type"] == "other"
        assert Organization.objects.get(code="lakeview-university").name == "Lakeview University"

    def test_staff_can_create_child_organization(self, staff_client, organization):
        response = staff_client.post(
            self.url,
            {
                "name": "Public Health Research Centre",
                "code": "public-health-research-centre",
                "parent": str(organization.id),
            },
        )

        assert response.status_code == 201
        assert str(response.data["parent"]) == str(organization.id)

    def test_staff_can_update_and_deactivate_organization(self, staff_client, organization):
        response = staff_client.patch(
            f"{self.url}{organization.id}/",
            {"name": "Moyo Research University", "is_active": False},
        )

        assert response.status_code == 200
        organization.refresh_from_db()
        assert organization.name == "Moyo Research University"
        assert organization.is_active is False

    def test_staff_can_delete_leaf_organization(self, staff_client, organization):
        response = staff_client.delete(f"{self.url}{organization.id}/")

        assert response.status_code == 204
        assert not Organization.objects.filter(pk=organization.pk).exists()

    def test_required_name_and_code_are_enforced(self, staff_client):
        response = staff_client.post(self.url, {"description": "Incomplete"})

        assert response.status_code == 400
        assert "name" in response.data
        assert "code" in response.data

    def test_invalid_type_is_rejected(self, staff_client):
        response = staff_client.post(
            self.url,
            {"name": "University", "code": "university", "organization_type": "hospital"},
        )

        assert response.status_code == 400
        assert "organization_type" in response.data

    def test_invalid_slug_code_is_rejected(self, staff_client):
        response = staff_client.post(
            self.url,
            {"name": "University", "code": "Not a valid code"},
        )

        assert response.status_code == 400
        assert "code" in response.data

    def test_duplicate_code_is_rejected(self, staff_client, organization):
        response = staff_client.post(
            self.url,
            {"name": "Duplicate", "code": organization.code},
        )

        assert response.status_code == 400
        assert "code" in response.data

    def test_parent_must_exist(self, staff_client):
        response = staff_client.post(
            self.url,
            {"name": "Unit", "code": "unit", "parent": str(uuid.uuid4())},
        )

        assert response.status_code == 400
        assert "parent" in response.data

    def test_parent_cannot_be_self(self, staff_client, organization):
        response = staff_client.patch(
            f"{self.url}{organization.id}/",
            {"parent": str(organization.id)},
        )

        assert response.status_code == 400
        assert "parent" in response.data

    def test_parent_cannot_be_descendant(self, staff_client, organization):
        child = Organization.objects.create(
            name="Research unit",
            code="research-unit",
            parent=organization,
        )

        response = staff_client.patch(
            f"{self.url}{organization.id}/",
            {"parent": str(child.id)},
        )

        assert response.status_code == 400
        assert "parent" in response.data

    def test_filtering_search_and_ordering(self, staff_client, organization):
        Organization.objects.create(
            name="District Health Office",
            code="district-health-office",
            organization_type=Organization.OrganizationType.DISTRICT,
            is_active=False,
        )

        response = staff_client.get(
            self.url,
            {"organization_type": "other", "is_active": "true", "search": "Moyo", "ordering": "name"},
        )

        assert response.status_code == 200
        assert response.data["count"] == 1
        assert response.data["results"][0]["code"] == organization.code

    def test_unknown_filter_and_ordering_fields_are_ignored(self, member_client, organization):
        response = member_client.get(
            self.url,
            {"not_a_filter": "value", "ordering": "not_a_field"},
        )

        assert response.status_code == 200
        assert response.data["count"] == 1

    def test_response_does_not_expose_unexpected_fields(self, member_client, organization):
        response = member_client.get(f"{self.url}{organization.id}/")

        assert set(response.data) == {
            "id", "name", "code", "organization_type", "description", "parent",
            "is_active", "created_at", "updated_at",
        }


@pytest.mark.django_db
class TestOrganizationAdmin:
    def test_organization_is_registered_with_admin(self):
        assert Organization in admin.site._registry

    def test_admin_lists_useful_fields_and_filters(self):
        model_admin = admin.site._registry[Organization]

        assert "name" in model_admin.list_display
        assert "organization_type" in model_admin.list_filter
        assert "code" in model_admin.search_fields
