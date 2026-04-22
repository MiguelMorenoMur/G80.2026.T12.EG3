"""Module for enterprise management operations."""
import json
import re
from datetime import datetime, timezone

from freezegun import freeze_time

from uc3m_consulting.enterprise_management_exception import EnterpriseManagementException
from uc3m_consulting.enterprise_manager_config import (
    PROJECTS_STORE_FILE,
    TEST_DOCUMENTS_STORE_FILE,
    TEST_NUMDOCS_STORE_FILE,
)
from uc3m_consulting.enterprise_project import EnterpriseProject
from uc3m_consulting.project_document import ProjectDocument


class EnterpriseManager:
    """Class for providing the methods for managing enterprise projects and documents."""

    def __init__(self):
        pass

    @staticmethod
    def validate_cif(cif_code: str):
        """Validate a CIF number."""
        if not isinstance(cif_code, str):
            raise EnterpriseManagementException("CIF code must be a string")

        cif_pattern = re.compile(r"^[ABCDEFGHJKNPQRSUVW]\d{7}[0-9A-J]$")
        if not cif_pattern.fullmatch(cif_code):
            raise EnterpriseManagementException("Invalid CIF format")

        cif_letter = cif_code[0]
        cif_digits = cif_code[1:8]
        control_character = cif_code[8]

        even_sum = 0
        odd_sum = 0

        for digit_index in range(len(cif_digits)):
            if digit_index % 2 == 0:
                doubled_value = int(cif_digits[digit_index]) * 2
                if doubled_value > 9:
                    even_sum = even_sum + (doubled_value // 10) + (doubled_value % 10)
                else:
                    even_sum = even_sum + doubled_value
            else:
                odd_sum = odd_sum + int(cif_digits[digit_index])

        total_sum = even_sum + odd_sum
        last_digit = total_sum % 10
        control_digit = 10 - last_digit

        if control_digit == 10:
            control_digit = 0

        control_letters = "JABCDEFGHI"

        if cif_letter in ("A", "B", "E", "H"):
            if str(control_digit) != control_character:
                raise EnterpriseManagementException("Invalid CIF character control number")
        elif cif_letter in ("P", "Q", "S", "K"):
            if control_letters[control_digit] != control_character:
                raise EnterpriseManagementException("Invalid CIF character control letter")
        else:
            raise EnterpriseManagementException("CIF type not supported")
        return True

    def validate_starting_date(self, t_d):
        """Validate date format using regex."""
        date_pattern = re.compile(r"^(([0-2]\d|3[0-1])\/(0\d|1[0-2])\/\d\d\d\d)$")
        match_result = date_pattern.fullmatch(t_d)
        if not match_result:
            raise EnterpriseManagementException("Invalid date format")

        try:
            parsed_date = datetime.strptime(t_d, "%d/%m/%Y").date()
        except ValueError as ex:
            raise EnterpriseManagementException("Invalid date format") from ex

        if parsed_date < datetime.now(timezone.utc).date():
            raise EnterpriseManagementException("Project's date must be today or later.")

        if parsed_date.year < 2025 or parsed_date.year > 2050:
            raise EnterpriseManagementException("Invalid date format")
        return t_d

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
        self.validate_cif(company_cif)

        acronym_pattern = re.compile(r"^[a-zA-Z0-9]{5,10}$")
        match_result = acronym_pattern.fullmatch(project_acronym)
        if not match_result:
            raise EnterpriseManagementException("Invalid acronym")

        description_pattern = re.compile(r"^.{10,30}$")
        match_result = description_pattern.fullmatch(project_description)
        if not match_result:
            raise EnterpriseManagementException("Invalid description format")

        department_pattern = re.compile(r"(HR|FINANCE|LEGAL|LOGISTICS)")
        match_result = department_pattern.fullmatch(department)
        if not match_result:
            raise EnterpriseManagementException("Invalid department")

        self.validate_starting_date(date)

        try:
            budget_value = float(budget)
        except ValueError as exc:
            raise EnterpriseManagementException("Invalid budget amount") from exc

        budget_text = str(budget_value)
        if "." in budget_text:
            decimal_digits = len(budget_text.split(".")[1])
            if decimal_digits > 2:
                raise EnterpriseManagementException("Invalid budget amount")

        if budget_value < 50000 or budget_value > 1000000:
            raise EnterpriseManagementException("Invalid budget amount")

        my_project = EnterpriseProject(
            company_cif=company_cif,
            project_acronym=project_acronym,
            project_description=project_description,
            department=department,
            starting_date=date,
            project_budget=budget,
        )

        try:
            with open(PROJECTS_STORE_FILE, "r", encoding="utf-8", newline="") as file:
                projects_list = json.load(file)
        except FileNotFoundError:
            projects_list = []
        except json.JSONDecodeError as ex:
            raise EnterpriseManagementException("JSON Decode Error - Wrong JSON Format") from ex

        for stored_project in projects_list:
            if stored_project == my_project.to_json():
                raise EnterpriseManagementException("Duplicated project in projects list")

        projects_list.append(my_project.to_json())

        try:
            with open(PROJECTS_STORE_FILE, "w", encoding="utf-8", newline="") as file:
                json.dump(projects_list, file, indent=2)
        except FileNotFoundError as ex:
            raise EnterpriseManagementException("Wrong file  or file path") from ex
        except json.JSONDecodeError as ex:
            raise EnterpriseManagementException("JSON Decode Error - Wrong JSON Format") from ex
        return my_project.project_id

    def find_docs(self, date_str):
        """
        Generate a JSON report counting valid documents for a specific date.

        Checks cryptographic hashes and timestamps to ensure historical data integrity.
        Saves the output to the configured JSON report file.
        """
        date_pattern = re.compile(r"^(([0-2]\d|3[0-1])\/(0\d|1[0-2])\/\d\d\d\d)$")
        match_result = date_pattern.fullmatch(date_str)
        if not match_result:
            raise EnterpriseManagementException("Invalid date format")

        try:
            datetime.strptime(date_str, "%d/%m/%Y").date()
        except ValueError as ex:
            raise EnterpriseManagementException("Invalid date format") from ex

        try:
            with open(TEST_DOCUMENTS_STORE_FILE, "r", encoding="utf-8", newline="") as file:
                stored_documents = json.load(file)
        except FileNotFoundError as ex:
            raise EnterpriseManagementException("Wrong file  or file path") from ex

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

        if found_documents == 0:
            raise EnterpriseManagementException("No documents found")

        report_timestamp = datetime.now(timezone.utc).timestamp()
        report_data = {
            "Querydate": date_str,
            "ReportDate": report_timestamp,
            "Numfiles": found_documents,
        }

        try:
            with open(TEST_NUMDOCS_STORE_FILE, "r", encoding="utf-8", newline="") as file:
                reports_list = json.load(file)
        except FileNotFoundError:
            reports_list = []
        except json.JSONDecodeError as ex:
            raise EnterpriseManagementException("JSON Decode Error - Wrong JSON Format") from ex

        reports_list.append(report_data)

        try:
            with open(TEST_NUMDOCS_STORE_FILE, "w", encoding="utf-8", newline="") as file:
                json.dump(reports_list, file, indent=2)
        except FileNotFoundError as ex:
            raise EnterpriseManagementException("Wrong file  or file path") from ex

        return found_documents