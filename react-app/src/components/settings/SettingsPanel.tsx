import { useState } from 'react';
import { Input, Textarea, Select, Toggle, Button, ColorPicker, Section } from './FormComponents';
import { SettingsTabs, settingsTabsConfig } from './SettingsTabs';
import type { Settings, SettingsTab, UserProfile, NotificationSettings, PrivacySettings, AppearanceSettings } from '../../types/settings';

interface SettingsPanelProps {
  initialSettings: Settings;
  onSave?: (settings: Settings) => void;
  onCancel?: () => void;
}

const timezones = [
  { value: 'UTC', label: 'UTC' },
  { value: 'America/New_York', label: 'Eastern Time (ET)' },
  { value: 'America/Chicago', label: 'Central Time (CT)' },
  { value: 'America/Denver', label: 'Mountain Time (MT)' },
  { value: 'America/Los_Angeles', label: 'Pacific Time (PT)' },
  { value: 'Europe/London', label: 'London (GMT)' },
  { value: 'Europe/Paris', label: 'Paris (CET)' },
  { value: 'Asia/Tokyo', label: 'Tokyo (JST)' },
];

const languages = [
  { value: 'en', label: 'English' },
  { value: 'es', label: 'Spanish' },
  { value: 'fr', label: 'French' },
  { value: 'de', label: 'German' },
  { value: 'ja', label: 'Japanese' },
  { value: 'zh', label: 'Chinese' },
];

const visibilityOptions = [
  { value: 'public', label: 'Public - Anyone can see' },
  { value: 'private', label: 'Private - Only you' },
  { value: 'contacts', label: 'Contacts - Only your contacts' },
];

const themeOptions = [
  { value: 'light', label: 'Light' },
  { value: 'dark', label: 'Dark' },
  { value: 'system', label: 'System' },
];

const fontSizeOptions = [
  { value: 'small', label: 'Small' },
  { value: 'medium', label: 'Medium' },
  { value: 'large', label: 'Large' },
];

const accentColors = [
  '#3B82F6', '#8B5CF6', '#EC4899', '#EF4444', '#F97316', '#EAB308', '#22C55E', '#14B8A6',
];

export function SettingsPanel({ initialSettings, onSave, onCancel }: SettingsPanelProps) {
  const [activeTab, setActiveTab] = useState<SettingsTab>('profile');
  const [settings, setSettings] = useState<Settings>(initialSettings);
  const [isSaving, setIsSaving] = useState(false);
  const [hasChanges, setHasChanges] = useState(false);

  const updateProfile = (updates: Partial<UserProfile>) => {
    setSettings((prev) => ({ ...prev, profile: { ...prev.profile, ...updates } }));
    setHasChanges(true);
  };

  const updateNotifications = (updates: Partial<NotificationSettings>) => {
    setSettings((prev) => ({ ...prev, notifications: { ...prev.notifications, ...updates } }));
    setHasChanges(true);
  };

  const updatePrivacy = (updates: Partial<PrivacySettings>) => {
    setSettings((prev) => ({ ...prev, privacy: { ...prev.privacy, ...updates } }));
    setHasChanges(true);
  };

  const updateAppearance = (updates: Partial<AppearanceSettings>) => {
    setSettings((prev) => ({ ...prev, appearance: { ...prev.appearance, ...updates } }));
    setHasChanges(true);
  };

  const handleSave = async () => {
    setIsSaving(true);
    await new Promise((resolve) => setTimeout(resolve, 1000));
    onSave?.(settings);
    setIsSaving(false);
    setHasChanges(false);
  };

  const handleCancel = () => {
    setSettings(initialSettings);
    setHasChanges(false);
    onCancel?.();
  };

  return (
    <div className="w-full max-w-4xl mx-auto bg-white dark:bg-gray-900 rounded-2xl shadow-xl overflow-hidden">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Settings</h2>
        <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
          Manage your account settings and preferences
        </p>
      </div>

      <div className="flex flex-col md:flex-row">
        {/* Tabs - Using SettingsTabs component */}
        <SettingsTabs
          tabs={settingsTabsConfig}
          activeTab={activeTab}
          onTabChange={setActiveTab}
        />

        {/* Content */}
        <div className="flex-1 p-6 overflow-y-auto max-h-[600px]">
          {/* Profile Tab */}
          {activeTab === 'profile' && (
            <div id="panel-profile" role="tabpanel" aria-labelledby="tab-profile" className="space-y-6">
              {/* Avatar */}
              <div className="flex items-center gap-4">
                <img
                  src={settings.profile.avatar}
                  alt="Profile"
                  className="w-20 h-20 rounded-full object-cover"
                />
                <div>
                  <Button variant="secondary" size="sm">Change Photo</Button>
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">JPG, PNG or GIF. Max 2MB.</p>
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <Input
                  id="firstName"
                  label="First Name"
                  value={settings.profile.firstName}
                  onChange={(e) => updateProfile({ firstName: e.target.value })}
                />
                <Input
                  id="lastName"
                  label="Last Name"
                  value={settings.profile.lastName}
                  onChange={(e) => updateProfile({ lastName: e.target.value })}
                />
              </div>

              <Input
                id="email"
                label="Email Address"
                type="email"
                value={settings.profile.email}
                onChange={(e) => updateProfile({ email: e.target.value })}
              />

              <Input
                id="phone"
                label="Phone Number"
                type="tel"
                value={settings.profile.phone}
                onChange={(e) => updateProfile({ phone: e.target.value })}
                helperText="Used for two-factor authentication"
              />

              <Textarea
                id="bio"
                label="Bio"
                value={settings.profile.bio}
                onChange={(e) => updateProfile({ bio: e.target.value })}
                rows={3}
                placeholder="Tell us about yourself..."
              />

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <Select
                  id="timezone"
                  label="Timezone"
                  value={settings.profile.timezone}
                  options={timezones}
                  onChange={(value) => updateProfile({ timezone: value })}
                />
                <Select
                  id="language"
                  label="Language"
                  value={settings.profile.language}
                  options={languages}
                  onChange={(value) => updateProfile({ language: value })}
                />
              </div>
            </div>
          )}

          {/* Notifications Tab */}
          {activeTab === 'notifications' && (
            <div id="panel-notifications" role="tabpanel" aria-labelledby="tab-notifications" className="space-y-6">
              <Section title="Communication" description="Choose how you want to be notified">
                <Toggle
                  id="emailNotifications"
                  label="Email Notifications"
                  description="Receive notifications via email"
                  checked={settings.notifications.emailNotifications}
                  onChange={(checked) => updateNotifications({ emailNotifications: checked })}
                />
                <Toggle
                  id="pushNotifications"
                  label="Push Notifications"
                  description="Receive push notifications in browser"
                  checked={settings.notifications.pushNotifications}
                  onChange={(checked) => updateNotifications({ pushNotifications: checked })}
                />
                <Toggle
                  id="smsNotifications"
                  label="SMS Notifications"
                  description="Receive notifications via text message"
                  checked={settings.notifications.smsNotifications}
                  onChange={(checked) => updateNotifications({ smsNotifications: checked })}
                />
              </Section>

              <Section title="Activity" description="Notifications about your tasks and mentions">
                <Toggle
                  id="mentionAlerts"
                  label="Mention Alerts"
                  description="When someone mentions you in a comment"
                  checked={settings.notifications.mentionAlerts}
                  onChange={(checked) => updateNotifications({ mentionAlerts: checked })}
                />
                <Toggle
                  id="taskReminders"
                  label="Task Reminders"
                  description="Reminders for upcoming tasks"
                  checked={settings.notifications.taskReminders}
                  onChange={(checked) => updateNotifications({ taskReminders: checked })}
                />
                <Toggle
                  id="dueDateAlerts"
                  label="Due Date Alerts"
                  description="Alerts when tasks are due soon"
                  checked={settings.notifications.dueDateAlerts}
                  onChange={(checked) => updateNotifications({ dueDateAlerts: checked })}
                />
              </Section>

              <Section title="Marketing" description="Promotional and digest emails">
                <Toggle
                  id="marketingEmails"
                  label="Marketing Emails"
                  description="News, updates, and promotions"
                  checked={settings.notifications.marketingEmails}
                  onChange={(checked) => updateNotifications({ marketingEmails: checked })}
                />
                <Toggle
                  id="weeklyDigest"
                  label="Weekly Digest"
                  description="Summary of your weekly activity"
                  checked={settings.notifications.weeklyDigest}
                  onChange={(checked) => updateNotifications({ weeklyDigest: checked })}
                />
              </Section>
            </div>
          )}

          {/* Privacy Tab */}
          {activeTab === 'privacy' && (
            <div id="panel-privacy" role="tabpanel" aria-labelledby="tab-privacy" className="space-y-6">
              <Section title="Profile Visibility" description="Control who can see your information">
                <div className="py-3">
                  <Select
                    id="profileVisibility"
                    label="Profile Visibility"
                    value={settings.privacy.profileVisibility}
                    options={visibilityOptions}
                    onChange={(value) => updatePrivacy({ profileVisibility: value as PrivacySettings['profileVisibility'] })}
                  />
                </div>
                <Toggle
                  id="showEmail"
                  label="Show Email Address"
                  description="Display your email on your profile"
                  checked={settings.privacy.showEmail}
                  onChange={(checked) => updatePrivacy({ showEmail: checked })}
                />
                <Toggle
                  id="showPhone"
                  label="Show Phone Number"
                  description="Display your phone on your profile"
                  checked={settings.privacy.showPhone}
                  onChange={(checked) => updatePrivacy({ showPhone: checked })}
                />
                <Toggle
                  id="showActivity"
                  label="Show Activity Status"
                  description="Let others see when you're online"
                  checked={settings.privacy.showActivity}
                  onChange={(checked) => updatePrivacy({ showActivity: checked })}
                />
                <Toggle
                  id="allowTagging"
                  label="Allow Tagging"
                  description="Let others tag you in tasks and comments"
                  checked={settings.privacy.allowTagging}
                  onChange={(checked) => updatePrivacy({ allowTagging: checked })}
                />
              </Section>

              <Section title="Security" description="Protect your account">
                <Toggle
                  id="twoFactorAuth"
                  label="Two-Factor Authentication"
                  description="Add an extra layer of security"
                  checked={settings.privacy.twoFactorAuth}
                  onChange={(checked) => updatePrivacy({ twoFactorAuth: checked })}
                />
                <Toggle
                  id="loginAlerts"
                  label="Login Alerts"
                  description="Get notified of new login attempts"
                  checked={settings.privacy.loginAlerts}
                  onChange={(checked) => updatePrivacy({ loginAlerts: checked })}
                />
              </Section>

              <Section title="Data" description="Control your data">
                <Toggle
                  id="dataSharing"
                  label="Data Sharing"
                  description="Share anonymous usage data to improve the app"
                  checked={settings.privacy.dataSharing}
                  onChange={(checked) => updatePrivacy({ dataSharing: checked })}
                />
              </Section>
            </div>
          )}

          {/* Appearance Tab */}
          {activeTab === 'appearance' && (
            <div id="panel-appearance" role="tabpanel" aria-labelledby="tab-appearance" className="space-y-6">
              <Section title="Theme" description="Customize the look and feel">
                <div className="py-3">
                  <Select
                    id="theme"
                    label="Color Theme"
                    value={settings.appearance.theme}
                    options={themeOptions}
                    onChange={(value) => updateAppearance({ theme: value as AppearanceSettings['theme'] })}
                  />
                </div>
                <div className="py-3">
                  <ColorPicker
                    label="Accent Color"
                    value={settings.appearance.accentColor}
                    onChange={(color) => updateAppearance({ accentColor: color })}
                    colors={accentColors}
                  />
                </div>
              </Section>

              <Section title="Display" description="Adjust display settings">
                <div className="py-3">
                  <Select
                    id="fontSize"
                    label="Font Size"
                    value={settings.appearance.fontSize}
                    options={fontSizeOptions}
                    onChange={(value) => updateAppearance({ fontSize: value as AppearanceSettings['fontSize'] })}
                  />
                </div>
                <Toggle
                  id="compactMode"
                  label="Compact Mode"
                  description="Reduce spacing for more content"
                  checked={settings.appearance.compactMode}
                  onChange={(checked) => updateAppearance({ compactMode: checked })}
                />
                <Toggle
                  id="animations"
                  label="Animations"
                  description="Enable smooth transitions and animations"
                  checked={settings.appearance.animations}
                  onChange={(checked) => updateAppearance({ animations: checked })}
                />
              </Section>

              <Section title="Accessibility" description="Make the app easier to use">
                <Toggle
                  id="highContrast"
                  label="High Contrast"
                  description="Increase contrast for better visibility"
                  checked={settings.appearance.highContrast}
                  onChange={(checked) => updateAppearance({ highContrast: checked })}
                />
              </Section>
            </div>
          )}
        </div>
      </div>

      {/* Footer */}
      <div className="px-6 py-4 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50 flex flex-col sm:flex-row items-center justify-between gap-3">
        <p className="text-sm text-gray-500 dark:text-gray-400">
          {hasChanges ? 'You have unsaved changes' : 'All changes saved'}
        </p>
        <div className="flex items-center gap-3">
          <Button variant="ghost" onClick={handleCancel} disabled={!hasChanges}>
            Cancel
          </Button>
          <Button onClick={handleSave} loading={isSaving} disabled={!hasChanges}>
            Save Changes
          </Button>
        </div>
      </div>
    </div>
  );
}
