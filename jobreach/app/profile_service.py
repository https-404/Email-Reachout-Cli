from pathlib import Path

from jobreach.ai.base import AIClient
from jobreach.ai.prompt_builder import build_profile_prompt
from jobreach.core.models import CandidateProfile
from jobreach.cv.parser import parse_cv
from jobreach.utils.json_utils import read_json, write_json


class ProfileService:
    def __init__(self, ai_client: AIClient):
        self.ai_client = ai_client

    def create_profile_from_cv(self, cv_path: str) -> CandidateProfile:
        cv_text = parse_cv(cv_path)
        return self.ai_client.generate_structured(build_profile_prompt(cv_text), CandidateProfile)


def save_profile(profile: CandidateProfile, path: str) -> None:
    write_json(path, profile.model_dump(mode="json"))


def load_profile(path: str) -> CandidateProfile:
    return CandidateProfile(**read_json(Path(path)))
