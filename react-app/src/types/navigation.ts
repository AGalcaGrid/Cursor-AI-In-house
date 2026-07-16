export interface NavItem {
  label: string;
  href: string;
  icon?: React.ReactNode;
}

export interface UserMenuProps {
  user: {
    name: string;
    email: string;
    avatar: string;
  } | null;
  onLogin?: () => void;
  onLogout?: () => void;
  onProfile?: () => void;
  onSettings?: () => void;
}

export interface NavBarProps {
  logo?: React.ReactNode;
  logoText?: string;
  navItems: NavItem[];
  user: UserMenuProps['user'];
  onSearch?: (query: string) => void;
  onLogin?: () => void;
  onLogout?: () => void;
  onProfile?: () => void;
  onSettings?: () => void;
}
