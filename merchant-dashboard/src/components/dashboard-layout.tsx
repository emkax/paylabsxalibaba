'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  LayoutDashboard,
  TrendingUp,
  Wallet,
  Users,
  Lightbulb,
  Sliders,
  Menu,
  X,
  Building2,
  Bell,
  Search,
  UserCircle,
} from 'lucide-react';
import styles from './dashboard-layout.module.css';

const navItems = [
  { href: '/dashboard', icon: LayoutDashboard, label: 'Overview' },
  { href: '/dashboard/revenue', icon: TrendingUp, label: 'Revenue' },
  { href: '/dashboard/cashflow', icon: Wallet, label: 'Cashflow' },
  { href: '/dashboard/peer', icon: Users, label: 'Peer Benchmark' },
  { href: '/dashboard/recommendation', icon: Lightbulb, label: 'Recommendations' },
  { href: '/dashboard/simulation', icon: Sliders, label: 'Simulation' },
];

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className={styles.layout}>
      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <div
          className={styles.overlay}
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside className={`${styles.sidebar} ${sidebarOpen ? styles.sidebarOpen : ''}`}>
        <div className={styles.sidebarHeader}>
          <Building2 className={styles.logoIcon} />
          <span className={styles.logoText}>PayLabs</span>
          <button
            className={styles.closeBtn}
            onClick={() => setSidebarOpen(false)}
          >
            <X size={20} />
          </button>
        </div>

        <nav className={styles.nav}>
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`${styles.navItem} ${isActive ? styles.navItemActive : ''}`}
                onClick={() => setSidebarOpen(false)}
              >
                <Icon size={20} />
                <span className={styles.navLabel}>{item.label}</span>
              </Link>
            );
          })}
        </nav>

        <div className={styles.sidebarFooter}>
          <div className={styles.merchantInfo}>
            <div className={styles.merchantAvatar}>
              <UserCircle size={24} />
            </div>
            <div className={styles.merchantDetails}>
              <div className={styles.merchantName}>Merchant 010614</div>
              <div className={styles.merchantTier}>Premium</div>
            </div>
          </div>
        </div>
      </aside>

      {/* Main content */}
      <div className={styles.mainContent}>
        {/* Header */}
        <header className={styles.header}>
          <button
            className={styles.menuBtn}
            onClick={() => setSidebarOpen(true)}
          >
            <Menu size={20} />
          </button>

          <div className={styles.headerCenter}>
            <div className={styles.searchBox}>
              <Search size={18} className={styles.searchIcon} />
              <input
                type="text"
                placeholder="Search..."
                className={styles.searchInput}
              />
            </div>
          </div>

          <div className={styles.headerActions}>
            <button className={styles.iconBtn}>
              <Bell size={20} />
              <span className={styles.notificationDot}></span>
            </button>
          </div>
        </header>

        {/* Page content */}
        <main className={styles.pageContent}>
          {children}
        </main>
      </div>
    </div>
  );
}
