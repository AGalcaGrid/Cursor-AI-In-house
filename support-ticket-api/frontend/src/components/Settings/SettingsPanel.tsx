import { useState, useCallback, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import { useTheme } from '../../context/ThemeContext';
import { authService, NotificationPreferences } from '../../services/api';
import {
  User,
  Bell,
  Shield,
  Palette,
  Save,
  X,
  Check,
  Camera,
  Mail,
  Phone,
  Moon,
  Sun,
  Monitor
} from 'lucide-react';

import SettingsTabs, { Tab, TabId } from './SettingsTabs';
import ToggleSwitch from '../ui/ToggleSwitch';
import FormInput from '../ui/FormInput';
import FormSelect from '../ui/FormSelect';
import FormTextarea from '../ui/FormTextarea';

const tabs: Tab[] = [
  { id: 'profile', label: 'Profile', icon: User },
  { id: 'notifications', label: 'Notifications', icon: Bell },
  { id: 'privacy', label: 'Privacy', icon: Shield },
  { id: 'appearance', label: 'Appearance', icon: Palette },
];

interface FormErrors {
  name?: string;
  email?: string;
  phone?: string;
  bio?: string;
}

export default function SettingsPanel() {
  const { user } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const [activeTab, setActiveTab] = useState<TabId>('profile');
  const [isSaving, setIsSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [hasChanges, setHasChanges] = useState(false);
  const [errors, setErrors] = useState<FormErrors>({});

  // Profile state
  const [profileData, setProfileData] = useState({
    name: user?.name || '',
    email: user?.email || '',
    phone: '',
    bio: '',
    language: 'en',
    timezone: 'UTC',
  });

  // Store initial values for cancel functionality
  const [initialProfileData] = useState({ ...profileData });

  // Notification settings state (FR-037)
  const [notificationSettings, setNotificationSettings] = useState<NotificationPreferences>({
    email_ticket_created: true,
    email_ticket_assigned: true,
    email_status_changed: true,
    email_new_comment: true,
    email_sla_warning: true,
    email_sla_breach: true,
    email_mentions: true,
    in_app_notifications: true,
  });

  const [initialNotificationSettings, setInitialNotificationSettings] = useState({ ...notificationSettings });
  const [isLoadingPrefs, setIsLoadingPrefs] = useState(false);

  // Load notification preferences from API
  useEffect(() => {
    const loadPreferences = async () => {
      try {
        setIsLoadingPrefs(true);
        const response = await authService.getNotificationPreferences();
        setNotificationSettings(response.preferences);
        setInitialNotificationSettings(response.preferences);
      } catch (error) {
        console.error('Failed to load notification preferences:', error);
      } finally {
        setIsLoadingPrefs(false);
      }
    };
    loadPreferences();
  }, []);

  // Privacy settings state
  const [privacySettings, setPrivacySettings] = useState({
    profileVisibility: 'team',
    showEmail: true,
    showPhone: false,
    activityStatus: true,
    twoFactorAuth: false,
    sessionTimeout: '30',
  });

  const [initialPrivacySettings] = useState({ ...privacySettings });

  // Appearance settings state
  const [appearanceSettings, setAppearanceSettings] = useState({
    accentColor: 'blue',
    fontSize: 'medium',
    compactMode: false,
    animations: true,
  });

  const [initialAppearanceSettings] = useState({ ...appearanceSettings });

  // Validation functions
  const validateEmail = (email: string): string | undefined => {
    if (!email) return 'Email is required';
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) return 'Please enter a valid email address';
    return undefined;
  };

  const validateName = (name: string): string | undefined => {
    if (!name) return 'Name is required';
    if (name.length < 2) return 'Name must be at least 2 characters';
    if (name.length > 50) return 'Name must be less than 50 characters';
    return undefined;
  };

  const validatePhone = (phone: string): string | undefined => {
    if (!phone) return undefined; // Phone is optional
    const phoneRegex = /^[+]?[(]?[0-9]{1,4}[)]?[-\s./0-9]*$/;
    if (!phoneRegex.test(phone)) return 'Please enter a valid phone number';
    return undefined;
  };

  const validateBio = (bio: string): string | undefined => {
    if (bio.length > 500) return 'Bio must be less than 500 characters';
    return undefined;
  };

  const validateForm = (): boolean => {
    const newErrors: FormErrors = {
      name: validateName(profileData.name),
      email: validateEmail(profileData.email),
      phone: validatePhone(profileData.phone),
      bio: validateBio(profileData.bio),
    };

    setErrors(newErrors);
    return !Object.values(newErrors).some(error => error !== undefined);
  };

  const handleProfileChange = useCallback((field: string, value: string) => {
    setProfileData(prev => ({ ...prev, [field]: value }));
    setHasChanges(true);
    
    // Clear error when user starts typing
    if (errors[field as keyof FormErrors]) {
      setErrors(prev => ({ ...prev, [field]: undefined }));
    }
  }, [errors]);

  const handleToggle = useCallback((
    setter: React.Dispatch<React.SetStateAction<any>>,
    key: string,
    currentValue: boolean
  ) => {
    setter((prev: any) => ({ ...prev, [key]: !currentValue }));
    setHasChanges(true);
  }, []);

  const handleSave = async () => {
    if (activeTab === 'profile' && !validateForm()) {
      return;
    }

    setIsSaving(true);
    try {
      if (activeTab === 'notifications') {
        // Save notification preferences to API (FR-037)
        await authService.updateNotificationPreferences(notificationSettings);
        setInitialNotificationSettings({ ...notificationSettings });
      } else {
        // Simulate API call for other tabs
        await new Promise(resolve => setTimeout(resolve, 1000));
      }
      setSaveSuccess(true);
      setHasChanges(false);
      setTimeout(() => setSaveSuccess(false), 3000);
    } catch (error) {
      console.error('Failed to save settings:', error);
    } finally {
      setIsSaving(false);
    }
  };

  const handleCancel = () => {
    // Reset all settings to initial values
    setProfileData({ ...initialProfileData });
    setNotificationSettings({ ...initialNotificationSettings });
    setPrivacySettings({ ...initialPrivacySettings });
    setAppearanceSettings({ ...initialAppearanceSettings });
    setErrors({});
    setHasChanges(false);
  };

  const renderProfileTab = () => (
    <div className="space-y-6">
      {/* Avatar section */}
      <div className="flex items-center gap-6 pb-6 border-b border-gray-200 dark:border-gray-700">
        <div className="relative">
          <div className="w-24 h-24 bg-blue-100 dark:bg-blue-900 rounded-full flex items-center justify-center">
            <User className="w-12 h-12 text-blue-600 dark:text-blue-400" />
          </div>
          <button
            className="absolute bottom-0 right-0 p-2 bg-blue-600 rounded-full text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 dark:focus:ring-offset-gray-800"
            aria-label="Change profile picture"
          >
            <Camera className="w-4 h-4" />
          </button>
        </div>
        <div>
          <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">{user?.name}</h3>
          <p className="text-sm text-gray-500 dark:text-gray-400 capitalize">{user?.role}</p>
          <button className="mt-2 text-sm text-blue-600 dark:text-blue-400 hover:underline focus:outline-none focus:ring-2 focus:ring-blue-500 rounded">
            Remove photo
          </button>
        </div>
      </div>

      {/* Form fields */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-x-6">
        <FormInput
          id="name"
          label="Full Name"
          value={profileData.name}
          onChange={(value) => handleProfileChange('name', value)}
          icon={User}
          placeholder="Enter your full name"
          error={errors.name}
          required
        />
        <FormInput
          id="email"
          label="Email Address"
          type="email"
          value={profileData.email}
          onChange={(value) => handleProfileChange('email', value)}
          icon={Mail}
          placeholder="Enter your email"
          error={errors.email}
          required
        />
        <FormInput
          id="phone"
          label="Phone Number"
          type="tel"
          value={profileData.phone}
          onChange={(value) => handleProfileChange('phone', value)}
          icon={Phone}
          placeholder="+1 (555) 000-0000"
          error={errors.phone}
        />
        <FormSelect
          id="language"
          label="Language"
          value={profileData.language}
          onChange={(value) => handleProfileChange('language', value)}
          options={[
            { value: 'en', label: 'English' },
            { value: 'es', label: 'Spanish' },
            { value: 'fr', label: 'French' },
            { value: 'de', label: 'German' },
          ]}
        />
      </div>

      <FormTextarea
        id="bio"
        label="Bio"
        value={profileData.bio}
        onChange={(value) => handleProfileChange('bio', value)}
        placeholder="Tell us about yourself..."
        maxLength={500}
        error={errors.bio}
      />

      <FormSelect
        id="timezone"
        label="Timezone"
        value={profileData.timezone}
        onChange={(value) => handleProfileChange('timezone', value)}
        options={[
          { value: 'UTC', label: 'UTC (Coordinated Universal Time)' },
          { value: 'EST', label: 'EST (Eastern Standard Time)' },
          { value: 'PST', label: 'PST (Pacific Standard Time)' },
          { value: 'CET', label: 'CET (Central European Time)' },
        ]}
      />
    </div>
  );

  const renderNotificationsTab = () => {
    if (isLoadingPrefs) {
      return (
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      );
    }

    return (
      <div className="divide-y divide-gray-200 dark:divide-gray-700">
        <div className="pb-6">
          <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-1">Ticket Email Notifications</h3>
          <p className="text-sm text-gray-500 dark:text-gray-400">Choose which ticket events trigger email notifications</p>
        </div>

        <ToggleSwitch
          enabled={notificationSettings.email_ticket_created}
          onChange={() => handleToggle(setNotificationSettings, 'email_ticket_created', notificationSettings.email_ticket_created)}
          label="Ticket Created"
          description="When a new ticket is created"
        />

        <ToggleSwitch
          enabled={notificationSettings.email_ticket_assigned}
          onChange={() => handleToggle(setNotificationSettings, 'email_ticket_assigned', notificationSettings.email_ticket_assigned)}
          label="Ticket Assigned"
          description="When a ticket is assigned to you"
        />

        <ToggleSwitch
          enabled={notificationSettings.email_status_changed}
          onChange={() => handleToggle(setNotificationSettings, 'email_status_changed', notificationSettings.email_status_changed)}
          label="Status Changed"
          description="When a ticket status is updated"
        />

        <ToggleSwitch
          enabled={notificationSettings.email_new_comment}
          onChange={() => handleToggle(setNotificationSettings, 'email_new_comment', notificationSettings.email_new_comment)}
          label="New Comments"
          description="When someone adds a comment to your ticket"
        />

        <div className="pt-6 pb-6">
          <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-1">SLA Notifications</h3>
          <p className="text-sm text-gray-500 dark:text-gray-400">Get notified about SLA deadlines</p>
        </div>

        <ToggleSwitch
          enabled={notificationSettings.email_sla_warning}
          onChange={() => handleToggle(setNotificationSettings, 'email_sla_warning', notificationSettings.email_sla_warning)}
          label="SLA Warning"
          description="When a ticket is approaching its SLA deadline"
        />

        <ToggleSwitch
          enabled={notificationSettings.email_sla_breach}
          onChange={() => handleToggle(setNotificationSettings, 'email_sla_breach', notificationSettings.email_sla_breach)}
          label="SLA Breach"
          description="When a ticket has breached its SLA"
        />

        <div className="pt-6 pb-6">
          <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-1">Other</h3>
        </div>

        <ToggleSwitch
          enabled={notificationSettings.email_mentions}
          onChange={() => handleToggle(setNotificationSettings, 'email_mentions', notificationSettings.email_mentions)}
          label="Mentions"
          description="When someone @mentions you in a comment"
        />

        <ToggleSwitch
          enabled={notificationSettings.in_app_notifications}
          onChange={() => handleToggle(setNotificationSettings, 'in_app_notifications', notificationSettings.in_app_notifications)}
          label="In-App Notifications"
          description="Show notifications within the application"
        />
      </div>
    );
  };

  const renderPrivacyTab = () => (
    <div className="divide-y divide-gray-200 dark:divide-gray-700">
      <div className="pb-6">
        <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-1">Profile Visibility</h3>
        <p className="text-sm text-gray-500 dark:text-gray-400">Control who can see your profile information</p>
      </div>

      <FormSelect
        id="profileVisibility"
        label="Who can see your profile"
        value={privacySettings.profileVisibility}
        onChange={(value) => {
          setPrivacySettings(prev => ({ ...prev, profileVisibility: value }));
          setHasChanges(true);
        }}
        options={[
          { value: 'public', label: 'Public - Anyone can view' },
          { value: 'team', label: 'Team - Only team members' },
          { value: 'private', label: 'Private - Only you' },
        ]}
      />

      <ToggleSwitch
        enabled={privacySettings.showEmail}
        onChange={() => handleToggle(setPrivacySettings, 'showEmail', privacySettings.showEmail)}
        label="Show Email Address"
        description="Display your email on your profile"
      />

      <ToggleSwitch
        enabled={privacySettings.showPhone}
        onChange={() => handleToggle(setPrivacySettings, 'showPhone', privacySettings.showPhone)}
        label="Show Phone Number"
        description="Display your phone number on your profile"
      />

      <ToggleSwitch
        enabled={privacySettings.activityStatus}
        onChange={() => handleToggle(setPrivacySettings, 'activityStatus', privacySettings.activityStatus)}
        label="Activity Status"
        description="Show when you're online"
      />

      <div className="pt-6 pb-6">
        <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-1">Security</h3>
        <p className="text-sm text-gray-500 dark:text-gray-400">Manage your account security settings</p>
      </div>

      <ToggleSwitch
        enabled={privacySettings.twoFactorAuth}
        onChange={() => handleToggle(setPrivacySettings, 'twoFactorAuth', privacySettings.twoFactorAuth)}
        label="Two-Factor Authentication"
        description="Add an extra layer of security to your account"
      />

      <FormSelect
        id="sessionTimeout"
        label="Session Timeout"
        value={privacySettings.sessionTimeout}
        onChange={(value) => {
          setPrivacySettings(prev => ({ ...prev, sessionTimeout: value }));
          setHasChanges(true);
        }}
        options={[
          { value: '15', label: '15 minutes' },
          { value: '30', label: '30 minutes' },
          { value: '60', label: '1 hour' },
          { value: '120', label: '2 hours' },
          { value: 'never', label: 'Never' },
        ]}
      />

      <div className="pt-6">
        <button className="px-4 py-2 text-red-600 dark:text-red-400 border border-red-300 dark:border-red-700 rounded-lg hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors focus:outline-none focus:ring-2 focus:ring-red-500">
          Delete Account
        </button>
        <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">
          Once you delete your account, there is no going back. Please be certain.
        </p>
      </div>
    </div>
  );

  const renderAppearanceTab = () => (
    <div className="divide-y divide-gray-200 dark:divide-gray-700">
      <div className="pb-6">
        <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-1">Theme</h3>
        <p className="text-sm text-gray-500 dark:text-gray-400">Choose your preferred color scheme</p>
      </div>

      <div className="py-6">
        <label className="block text-sm font-medium text-gray-900 dark:text-gray-100 mb-4">
          Color Mode
        </label>
        <div className="grid grid-cols-3 gap-4">
          {[
            { value: 'light', label: 'Light', icon: Sun },
            { value: 'dark', label: 'Dark', icon: Moon },
            { value: 'system', label: 'System', icon: Monitor },
          ].map((option) => {
            const Icon = option.icon;
            const isSelected = theme === option.value;
            return (
              <button
                key={option.value}
                onClick={() => {
                  if (option.value === 'light' && theme === 'dark') toggleTheme();
                  if (option.value === 'dark' && theme === 'light') toggleTheme();
                  setHasChanges(true);
                }}
                className={`
                  flex flex-col items-center gap-2 p-4 rounded-lg border-2 transition-colors
                  focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 dark:focus:ring-offset-gray-800
                  ${isSelected 
                    ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/30' 
                    : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
                  }
                `}
                aria-pressed={isSelected}
              >
                <Icon className={`w-6 h-6 ${isSelected ? 'text-blue-600 dark:text-blue-400' : 'text-gray-500 dark:text-gray-400'}`} />
                <span className={`text-sm font-medium ${isSelected ? 'text-blue-600 dark:text-blue-400' : 'text-gray-700 dark:text-gray-300'}`}>
                  {option.label}
                </span>
              </button>
            );
          })}
        </div>
      </div>

      <div className="py-6">
        <label className="block text-sm font-medium text-gray-900 dark:text-gray-100 mb-4">
          Accent Color
        </label>
        <div className="flex gap-3">
          {[
            { value: 'blue', color: 'bg-blue-500' },
            { value: 'purple', color: 'bg-purple-500' },
            { value: 'green', color: 'bg-green-500' },
            { value: 'orange', color: 'bg-orange-500' },
            { value: 'pink', color: 'bg-pink-500' },
          ].map((option) => (
            <button
              key={option.value}
              onClick={() => {
                setAppearanceSettings(prev => ({ ...prev, accentColor: option.value }));
                setHasChanges(true);
              }}
              className={`
                w-10 h-10 rounded-full ${option.color} flex items-center justify-center
                focus:outline-none focus:ring-2 focus:ring-offset-2 dark:focus:ring-offset-gray-800 focus:ring-blue-500
                ${appearanceSettings.accentColor === option.value ? 'ring-2 ring-offset-2 dark:ring-offset-gray-800 ring-gray-900 dark:ring-white' : ''}
              `}
              aria-label={`${option.value} accent color`}
              aria-pressed={appearanceSettings.accentColor === option.value}
            >
              {appearanceSettings.accentColor === option.value && (
                <Check className="w-5 h-5 text-white" />
              )}
            </button>
          ))}
        </div>
      </div>

      <FormSelect
        id="fontSize"
        label="Font Size"
        value={appearanceSettings.fontSize}
        onChange={(value) => {
          setAppearanceSettings(prev => ({ ...prev, fontSize: value }));
          setHasChanges(true);
        }}
        options={[
          { value: 'small', label: 'Small' },
          { value: 'medium', label: 'Medium (Default)' },
          { value: 'large', label: 'Large' },
        ]}
      />

      <ToggleSwitch
        enabled={appearanceSettings.compactMode}
        onChange={() => handleToggle(setAppearanceSettings, 'compactMode', appearanceSettings.compactMode)}
        label="Compact Mode"
        description="Reduce spacing and padding for a denser layout"
      />

      <ToggleSwitch
        enabled={appearanceSettings.animations}
        onChange={() => handleToggle(setAppearanceSettings, 'animations', appearanceSettings.animations)}
        label="Animations"
        description="Enable smooth transitions and animations"
      />
    </div>
  );

  const renderTabContent = () => {
    switch (activeTab) {
      case 'profile':
        return renderProfileTab();
      case 'notifications':
        return renderNotificationsTab();
      case 'privacy':
        return renderPrivacyTab();
      case 'appearance':
        return renderAppearanceTab();
      default:
        return null;
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">Settings</h1>
        <p className="text-gray-500 dark:text-gray-400 mt-1">Manage your account settings and preferences</p>
      </div>

      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm overflow-hidden">
        {/* Tabs */}
        <SettingsTabs
          tabs={tabs}
          activeTab={activeTab}
          onTabChange={setActiveTab}
        />

        {/* Tab content */}
        <div
          role="tabpanel"
          id={`${activeTab}-panel`}
          aria-labelledby={`${activeTab}-tab`}
          className="p-6"
        >
          {renderTabContent()}
        </div>

        {/* Save/Cancel buttons */}
        <div className="px-6 py-4 bg-gray-50 dark:bg-gray-800/50 border-t border-gray-200 dark:border-gray-700 flex items-center justify-between">
          <div>
            {saveSuccess && (
              <div className="flex items-center gap-2 text-green-600 dark:text-green-400">
                <Check className="w-5 h-5" />
                <span className="text-sm font-medium">Settings saved successfully!</span>
              </div>
            )}
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={handleCancel}
              disabled={!hasChanges || isSaving}
              className="flex items-center gap-2 px-4 py-2 text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 dark:focus:ring-offset-gray-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <X className="w-4 h-4" />
              Cancel
            </button>
            <button
              onClick={handleSave}
              disabled={isSaving}
              className="flex items-center gap-2 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 dark:focus:ring-offset-gray-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {isSaving ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  Saving...
                </>
              ) : (
                <>
                  <Save className="w-4 h-4" />
                  Save Changes
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
