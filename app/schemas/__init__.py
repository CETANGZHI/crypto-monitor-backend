from app.schemas.user import (
    SendVerificationCode,
    UserRegister,
    UserLogin,
    AutoRegister,
    UserUpdate,
    PasswordChange,
    UserResponse,
    UserBrief,
    TokenResponse,
    TokenRefresh,
    UserStats,
    TrialStatus,
    VerificationResponse
)

from app.schemas.oauth import (
    OAuthUserInfo,
    GoogleOAuthRequest,
    AppleOAuthRequest,
    OAuthLoginResponse,
    OAuthCallbackRequest
)

from app.schemas.notification import (
    NotificationType,
    NotificationStatus,
    NotificationPriority,
    NotificationBase,
    NotificationCreate,
    NotificationUpdate,
    NotificationResponse,
    NotificationList,
    NotificationRuleBase,
    NotificationRuleCreate,
    NotificationRuleUpdate,
    NotificationRuleResponse,
    NotificationSettingsBase,
    NotificationSettingsUpdate,
    NotificationSettingsResponse,
    NotificationTemplateBase,
    NotificationTemplateCreate,
    NotificationTemplateUpdate,
    NotificationTemplateResponse,
    NotificationBatchUpdate,
    NotificationBatchDelete,
    NotificationStats
)


