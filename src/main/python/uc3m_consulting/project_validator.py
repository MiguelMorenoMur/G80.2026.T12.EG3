"""Project validation helpers."""
import re
from datetime import datetime, timezone

from uc3m_consulting.enterprise_management_exception import (
    EnterpriseManagementException,
)


class ProjectValidator:
    """Validate project input data."""

    _instance = None

    def __new__(cls):
        """Create a single shared instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @staticmethod
    def validate_with_pattern(pattern_text, value, error_message):
        """Validate a value with a regex."""
        compiled_pattern = re.compile(pattern_text)
        match_result = compiled_pattern.fullmatch(value)
        if not match_result:
            raise EnterpriseManagementException(error_message)

    @staticmethod
    def validate_date_format(date_text):
        """Validate the date format."""
        ProjectValidator.validate_with_pattern(
            r"^(([0-2]\d|3[0-1])\/(0\d|1[0-2])\/\d\d\d\d)$",
            date_text,
            "Invalid date format",
        )
        try:
            datetime.strptime(date_text, "%d/%m/%Y").date()
        except ValueError as ex:
            raise EnterpriseManagementException("Invalid date format") from ex

    @staticmethod
    def validate_cif(cif_code: str):
        """Validate a CIF."""
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

        for digit_index, cif_digit in enumerate(cif_digits):
            if digit_index % 2 == 0:
                doubled_value = int(cif_digit) * 2
                if doubled_value > 9:
                    even_sum += (doubled_value // 10) + (doubled_value % 10)
                else:
                    even_sum += doubled_value
            else:
                odd_sum += int(cif_digit)

        total_sum = even_sum + odd_sum
        last_digit = total_sum % 10
        control_digit = 10 - last_digit

        if control_digit == 10:
            control_digit = 0

        control_letters = "JABCDEFGHI"

        if cif_letter in ("A", "B", "E", "H"):
            if str(control_digit) != control_character:
                raise EnterpriseManagementException(
                    "Invalid CIF character control number"
                )
        elif cif_letter in ("P", "Q", "S", "K"):
            if control_letters[control_digit] != control_character:
                raise EnterpriseManagementException(
                    "Invalid CIF character control letter"
                )
        else:
            raise EnterpriseManagementException("CIF type not supported")
        return True

    @staticmethod
    def validate_starting_date(date_text):
        """Validate a project start date."""
        ProjectValidator.validate_date_format(date_text)

        parsed_date = datetime.strptime(date_text, "%d/%m/%Y").date()

        if parsed_date < datetime.now(timezone.utc).date():
            raise EnterpriseManagementException(
                "Project's date must be today or later."
            )

        if parsed_date.year < 2025 or parsed_date.year > 2050:
            raise EnterpriseManagementException("Invalid date format")
        return date_text

    @staticmethod
    def validate_project_inputs(
        company_cif,
        project_acronym,
        project_description,
        department,
        date_text,
    ):
        """Validate all project inputs."""
        ProjectValidator.validate_cif(company_cif)
        ProjectValidator.validate_with_pattern(
            r"^[a-zA-Z0-9]{5,10}$",
            project_acronym,
            "Invalid acronym",
        )
        ProjectValidator.validate_with_pattern(
            r"^.{10,30}$",
            project_description,
            "Invalid description format",
        )
        ProjectValidator.validate_with_pattern(
            r"(HR|FINANCE|LEGAL|LOGISTICS)",
            department,
            "Invalid department",
        )
        ProjectValidator.validate_starting_date(date_text)

    @staticmethod
    def validate_budget(budget):
        """Validate a budget."""
        try:
            budget_value = float(budget)
        except ValueError as exc:
            raise EnterpriseManagementException(
                "Invalid budget amount"
            ) from exc

        budget_text = str(budget_value)
        if "." in budget_text:
            decimal_digits = len(budget_text.split(".")[1])
            if decimal_digits > 2:
                raise EnterpriseManagementException("Invalid budget amount")

        if budget_value < 50000 or budget_value > 1000000:
            raise EnterpriseManagementException("Invalid budget amount")

        return budget_value
