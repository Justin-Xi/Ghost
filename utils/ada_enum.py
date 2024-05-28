from enum import Enum


class OperatingSystem(Enum):
    ANDROID = "Android"
    ANDROID_CLOUD = "Android_Cloud"
    IOS = "iOS"
    LINUX = "Linux"
    LINUX_CLOUD = "Linux_Cloud"
    MACOS = "macOS"
    WINDOWS = "Windows"
    WINDOWS_CLOUD = "Windows_Cloud"


class Language(Enum):
    CHINESE = "Chinese"
    ENGLISH = "English"
    FRENCH = "French"
    GERMAN = "German"
    JAPANESE = "Japanese"
    KOREAN = "Korean"
    SPANISH = "Spanish"


class ScreenResolution(Enum):
    HD = "1280x720"
    FHD = "1920x1080"
    QHD = "2560x1440"
    UHD = "3840x2160"
    OTHER = "Other"


class State(Enum):
    CREATED = 0
    READY = 1
    RUNNING = 2
    BLOCKED = 3
    CANCELLED = 4
    COMPLETED = 5


class Result(Enum):
    SUCCESSFUL = 0
    FAILED = 1
