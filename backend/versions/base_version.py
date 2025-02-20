from abc import ABC, abstractmethod

class BaseVersion(ABC):
    @abstractmethod
    def generate_transformed_vocals(self, vocal_file: str, output_file: str):
        """Transform vocals based on version-specific logic"""
        pass

    @abstractmethod
    def merge_with_instrumental(self, instrumental_file: str, transformed_vocals_file: str, output_file: str):
        """Merge the transformed vocals with the instrumental"""
        pass