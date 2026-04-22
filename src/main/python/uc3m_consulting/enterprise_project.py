"""MODULE: enterprise_project. Contains the EnterpriseProject class."""
import hashlib
import json
from datetime import datetime, timezone


class EnterpriseProject:
    """Class representing a project."""

    # pylint: disable=too-many-arguments,too-many-positional-arguments
    def __init__(
        self,
        company_cif: str,
        project_acronym: str,
        project_description: str,
        department: str,
        starting_date: str,
        project_budget: float,
    ):
        self.__company_cif = company_cif
        self.__project_description = project_description
        self.__project_achronym = project_acronym
        self.__department = department
        self.__starting_date = starting_date
        self.__project_budget = project_budget
        current_datetime = datetime.now(timezone.utc)
        self.__time_stamp = datetime.timestamp(current_datetime)

    def __str__(self):
        return "Project:" + json.dumps(self.__dict__)

    def to_json(self):
        """Return the object information in JSON format."""
        return {
            "company_cif": self.__company_cif,
            "project_description": self.__project_description,
            "project_achronym": self.__project_achronym,
            "project_budget": self.__project_budget,
            "department": self.__department,
            "starting_date": self.__starting_date,
            "time_stamp": self.__time_stamp,
            "project_id": self.project_id,
        }

    @property
    def company_cif(self):
        """Company cif."""
        return self.__company_cif

    @company_cif.setter
    def company_cif(self, value):
        self.__company_cif = value

    @property
    def project_description(self):
        """Project description."""
        return self.__project_description

    @project_description.setter
    def project_description(self, value):
        self.__project_description = value

    @property
    def project_achronym(self):
        """Project achronym."""
        return self.__project_achronym

    @project_achronym.setter
    def project_achronym(self, value):
        self.__project_achronym = value

    @property
    def project_budget(self):
        """Project budget."""
        return self.__project_budget

    @project_budget.setter
    def project_budget(self, value):
        self.__project_budget = value

    @property
    def department(self):
        """Department."""
        return self.__department

    @department.setter
    def department(self, value):
        self.__department = value

    @property
    def starting_date(self):
        """Starting date."""
        return self.__starting_date

    @starting_date.setter
    def starting_date(self, value):
        self.__starting_date = value

    @property
    def time_stamp(self):
        """Time stamp."""
        return self.__time_stamp

    @property
    def project_id(self):
        """Return project id."""
        return hashlib.md5(str(self).encode()).hexdigest()
