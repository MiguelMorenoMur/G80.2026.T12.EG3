"""Module for enterprise management operations."""
from datetime import datetime, timezone

from freezegun import freeze_time

from uc3m_consulting.enterprise_management_exception import EnterpriseManagementException
from uc3m_consulting.enterprise_manager_config import (
    PROJECTS_STORE_FILE,
    TEST_DOCUMENTS_STORE_FILE,
    TEST_NUMDOCS_STORE_FILE,
)
from uc3m_consulting.enterprise_project import EnterpriseProject
from uc3m_consulting.json_store import JsonStore
from uc3m_consulting.project_document import ProjectDocument
from uc3m_consulting.project_validator import ProjectValidator


class EnterpriseManager:
    """Class for providing the methods for managing enterprise projects and documents."""

    def __init__(self):
        pass

    @staticmethod
    def validate_cif(cif_code: str):
        """Validate a CIF number."""
        return ProjectValidator.validate_cif(cif_code)

    def validate_starting_date(self, t_d):
        """Validate date format and business rules for project start date."""
        return ProjectValidator.validate_starting_date(t_d)

    @staticmethod
    def _create_project(company_cif, project_acronym, project_description, department, date, budget):
        """Create a project entity."""
        return EnterpriseProject(
            company_cif=company_cif,
            project_acronym=project_acronym,
            project_description=project_description,
            department=department,
            starting_date=date,
            project_budget=budget,
        )

    @staticmethod
    def _ensure_project_is_not_duplicated(projects_list, new_project):
        """Check that the project is not duplicated."""
        for stored_project in projects_list:
            if stored_project == new_project.to_json():
                raise EnterpriseManagementException("Duplicated project in projects list")

    @staticmethod
    def _count_documents_for_date(stored_documents, date_str):
        """Count valid documents for a specific date."""
        found_documents = 0

        for stored_document in stored_documents:
            register_timestamp = stored_document["register_date"]
            formatted_date = datetime.fromtimestamp(register_timestamp).strftime("%d/%m/%Y")

            if formatted_date == date_str:
                frozen_datetime = datetime.fromtimestamp(register_timestamp, tz=timezone.utc)
                with freeze_time(frozen_datetime):
                    project_document = ProjectDocument(
                        stored_document["project_id"],
                        stored_document["file_name"],
                    )
                    if project_document.document_signature == stored_document["document_signature"]:
                        found_documents = found_documents + 1
                    else:
                        raise EnterpriseManagementException("Inconsistent document signature")

        return found_documents

    @staticmethod
    def _build_report_data(date_str, found_documents):
        """Build the report entry."""
        report_timestamp = datetime.now(timezone.utc).timestamp()
        return {
            "Querydate": date_str,
            "ReportDate": report_timestamp,
            "Numfiles": found_documents,
        }

    # pylint: disable=too-many-arguments, too-many-positional-arguments
    def register_project(
        self,
        company_cif: str,
        project_acronym: str,
        project_description: str,
        department: str,
        date: str,
        budget: str,
    ):
        """Register a new project."""
        ProjectValidator.validate_project_inputs(
            company_cif,
            project_acronym,
            project_description,
            department,
            date,
        )
        ProjectValidator.validate_budget(budget)

        new_project = self._create_project(
            company_cif,
            project_acronym,
            project_description,
            department,
            date,
            budget,
        )

        projects_list = JsonStore.load_with_empty_default(PROJECTS_STORE_FILE)
        self._ensure_project_is_not_duplicated(projects_list, new_project)

        projects_list.append(new_project.to_json())
        JsonStore.save(PROJECTS_STORE_FILE, projects_list)

        return new_project.project_id

    def find_docs(self, date_str):
        """
        Generate a JSON report counting valid documents for a specific date.

        Checks cryptographic hashes and timestamps to ensure historical data integrity.
        Saves the output to the configured JSON report file.
        """
        ProjectValidator.validate_date_format(date_str)

        stored_documents = JsonStore.load_required(TEST_DOCUMENTS_STORE_FILE)
        found_documents = self._count_documents_for_date(stored_documents, date_str)

        if found_documents == 0:
            raise EnterpriseManagementException("No documents found")

        report_data = self._build_report_data(date_str, found_documents)

        reports_list = JsonStore.load_with_empty_default(TEST_NUMDOCS_STORE_FILE)
        reports_list.append(report_data)
        JsonStore.save(TEST_NUMDOCS_STORE_FILE, reports_list)

        return found_documents