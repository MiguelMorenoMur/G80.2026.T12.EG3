"""Contains the ProjectDocument class."""
import hashlib
from datetime import datetime, timezone


class ProjectDocument:
    """Class representing a project document."""

    def __init__(self, project_id: str, file_name: str):
        self.__alg = "SHA-256"
        self.__type = "PDF"
        self.__project_id = project_id
        self.__file_name = file_name
        current_datetime = datetime.now(timezone.utc)
        self.__register_date = datetime.timestamp(current_datetime)

    def to_json(self):
        """Return object data in JSON format."""
        return {
            "alg": self.__alg,
            "type": self.__type,
            "project_id": self.__project_id,
            "file_name": self.__file_name,
            "register_date": self.__register_date,
            "document_signature": self.document_signature,
        }

    def __signature_string(self):
        return (
            "{alg:" + str(self.__alg)
            + ",typ:" + str(self.__type)
            + ",project_id:" + str(self.__project_id)
            + ",file_name:" + str(self.__file_name)
            + ",register_date:" + str(self.__register_date) + "}"
        )

    @property
    def project_id(self):
        """Project id."""
        return self.__project_id

    @project_id.setter
    def project_id(self, value):
        self.__project_id = value

    @property
    def file_name(self):
        """File name."""
        return self.__file_name

    @file_name.setter
    def file_name(self, value):
        self.__file_name = value

    @property
    def register_date(self):
        """Register date."""
        return self.__register_date

    @register_date.setter
    def register_date(self, value):
        self.__register_date = value

    @property
    def document_signature(self):
        """Return document signature."""
        return hashlib.sha256(self.__signature_string().encode()).hexdigest()